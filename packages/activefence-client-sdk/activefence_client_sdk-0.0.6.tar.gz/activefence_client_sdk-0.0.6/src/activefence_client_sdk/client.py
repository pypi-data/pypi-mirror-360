import asyncio
import logging
import os
import uuid
from typing import Any, Optional

import aiohttp
import requests

from .models import AnalysisContext, CustomField, EvaluateMessageResponse, MessageType
from .utils import async_retry_with_exponential_backoff, retry_with_exponential_backoff

# HTTP status code threshold for error responses
HTTP_ERROR_THRESHOLD = 300

logger = logging.getLogger("activefence_client_sdk")


class ActiveFenceClient:
    """SDK Client for easier communication with ActiveFence API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        app_name: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        platform: Optional[str] = None,
        api_timeout: Optional[int] = None,
    ) -> None:
        """
        Initialize the ActiveFenceClient with configuration values.
        :param api_key: The supplied ActiveFence API key - provide if you want to override the env var or not use it
        :param app_name: Name of the app that is calling the API - provide if you want to override the env var
        :param base_url: Base URL for the ActiveFence API - provide if you want to override the env var
        :param provider: Default value for which LLM provider the client is analyzing (e.g. openai, anthropic, deepseek)
        :param model_name: Default value for name of the LLM model being used (e.g. gpt-3.5-turbo, claude-2)
        :param model_version: Default value for version of the LLM model being used (e.g. 2023-05-15)
        :param platform: Default value for cloud platform where the model is hosted (e.g. aws, azure, databricks)
        :param api_timeout: Timeout for API requests in seconds (default is 5 seconds)
        """
        # Initialize with provided values or environment variables
        self.api_key = api_key or os.environ.get("ACTIVEFENCE_API_KEY")
        self.app_name = app_name or os.environ.get("ACTIVEFENCE_APP_NAME", "unknown")
        self.base_url = base_url or os.environ.get("ACTIVEFENCE_URL_OVERRIDE", "https://apis.activefence.com")
        self.provider = provider or os.environ.get("ACTIVEFENCE_MODEL_PROVIDER", "unknown")
        self.model_name = model_name or os.environ.get("ACTIVEFENCE_MODEL_NAME", "unknown")
        self.model_version = model_version or os.environ.get("ACTIVEFENCE_MODEL_VERSION", "unknown")
        self.platform = platform or os.environ.get("ACTIVEFENCE_PLATFORM", "unknown")
        self.api_timeout = api_timeout or int(os.environ.get("ACTIVEFENCE_API_TIMEOUT", 5))

        # Initialize derived attributes
        self.api_url = self.base_url + "/v1/evaluate/message"  # type: ignore[operator]
        self.headers = {
            "Content-Type": "application/json",
            "af-api-key": self.api_key,
        }

        # Initialize HTTP client based on context
        self.http_client: Optional[aiohttp.ClientSession] = None
        self.timeout_seconds: Optional[aiohttp.ClientTimeout] = None

        try:
            if asyncio.get_event_loop().is_running():
                self.http_client = aiohttp.ClientSession(
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
                    },
                    connector=aiohttp.TCPConnector(limit=5000, force_close=False),
                )
                self.timeout_seconds = aiohttp.ClientTimeout(total=self.api_timeout)
        except RuntimeError:
            # If no event loop is running, we are in a synchronous context
            # http_client and timeout_seconds remain None
            pass

        # Run post-initialization validations
        self._validate_init_parameters()

        logger.debug(
            "ActiveFenceClient initialized successfully with base_url: %s, app_name: %s", self.base_url, self.app_name
        )

    async def close(self) -> None:
        """Explicitly close the HTTP client session."""
        if self.http_client and not self.http_client.closed:
            await self.http_client.close()

    def _validate_init_parameters(self) -> None:
        """
        Post-initialization validations and setup.
        This method is called after all attributes are initialized to perform validations.
        """
        # Validate required fields
        if not self.api_key or self.api_key.strip() == "":
            raise ValueError(
                "API key is required. Set ACTIVEFENCE_API_KEY environment variable or pass api_key parameter."
            )

        if not self.base_url or self.base_url.strip() == "":
            raise ValueError(
                "Base URL is required. Set ACTIVEFENCE_URL_OVERRIDE environment variable or pass base_url parameter."
            )

        # Validate URL format
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid base URL format: {self.base_url}. URL must start with http:// or https://")

        # Validate timeout
        if self.api_timeout <= 0:
            raise ValueError(f"API timeout must be positive, got: {self.api_timeout}")

        # Validate that required fields are not empty strings
        if not self.app_name or self.app_name.strip() == "":
            raise ValueError(
                "App name cannot be empty. Set ACTIVEFENCE_APP_NAME environment variable or pass app_name parameter."
            )

    def _validate_custom_fields_set(self, custom_fields: Optional[set[CustomField]] = None) -> None:
        """
        Validate that custom_fields is either None or a set of CustomField objects.

        :param custom_fields: The custom fields to validate
        :raises ValueError: If custom_fields is not None and not a set of CustomField objects
        """
        if custom_fields is not None:
            if not isinstance(custom_fields, set):
                raise ValueError(f"custom_fields must be a set of CustomField objects, got {type(custom_fields)}")

            for field in custom_fields:
                if not isinstance(field, CustomField):
                    raise ValueError(f"All items in custom_fields must be CustomField instances, got {type(field)}")

    def _create_request_body(
        self,
        text: str,
        type: MessageType,
        model: Optional[str] = None,
        platform: Optional[str] = None,
        provider: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        version: Optional[str] = None,
        custom_fields: Optional[set[CustomField]] = None,
    ) -> dict:
        # Validate custom_fields is a set
        self._validate_custom_fields_set(custom_fields)

        body: dict[str, Any] = {
            "text": text,
            "message_type": type.value,
            "session_id": session_id or str(uuid.uuid4()),
            "user_id": user_id or str(uuid.uuid4()),
            "app_name": self.app_name,
            "model_context": {
                "provider": provider or self.provider,
                "name": model or self.model_name,
                "version": version or self.model_version,
                "cloud_platform": platform or self.platform,
            },
        }
        if custom_fields is not None and len(custom_fields) > 0:
            body["custom_fields"] = [field.to_dict() for field in custom_fields]

        logger.debug("API request: %s", body)
        return body

    def _handle_api_response(self, detection: dict) -> EvaluateMessageResponse:
        logger.debug("API response: %s", detection)
        return EvaluateMessageResponse(**detection)

    @retry_with_exponential_backoff(
        max_retries=int(os.environ.get("ACTIVEFENCE_RETRY_MAX", "3")),
        base_delay=float(os.environ.get("ACTIVEFENCE_RETRY_BASE_DELAY", "1")),
    )
    def _sync_internal_call(
        self,
        text: str,
        type: MessageType,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        version: Optional[str] = None,
        platform: Optional[str] = None,
        custom_fields: Optional[set[CustomField]] = None,
    ) -> EvaluateMessageResponse:
        body = self._create_request_body(
            text,
            type,
            model,
            platform,
            provider,
            session_id,
            user_id,
            version,
            custom_fields,
        )
        detection_response = requests.post(
            self.api_url,
            headers=self.headers,
            json=body,
            timeout=self.api_timeout,
        )
        if detection_response.status_code >= HTTP_ERROR_THRESHOLD:
            raise Exception(f"{detection_response.status_code}:{detection_response.text}")

        return self._handle_api_response(detection_response.json())

    @async_retry_with_exponential_backoff(
        max_retries=int(os.environ.get("ACTIVEFENCE_RETRY_MAX", "3")),
        base_delay=float(os.environ.get("ACTIVEFENCE_RETRY_BASE_DELAY", "1")),
    )
    async def _async_internal_call(
        self,
        text: str,
        type: MessageType,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        version: Optional[str] = None,
        platform: Optional[str] = None,
        custom_fields: Optional[set[CustomField]] = None,
    ) -> EvaluateMessageResponse:
        if self.http_client is None:
            raise RuntimeError("Async client not initialized. Ensure you have a running event loop.")

        body = self._create_request_body(
            text,
            type,
            model,
            platform,
            provider,
            session_id,
            user_id,
            version,
            custom_fields,
        )

        async with self.http_client.post(
            self.api_url,
            headers=self.headers,
            json=body,
            timeout=self.timeout_seconds,
        ) as detection_response:
            if detection_response.status >= HTTP_ERROR_THRESHOLD:
                raise Exception(f"{detection_response.status}:{detection_response.text}")
            return self._handle_api_response(await detection_response.json())

    def evaluate_prompt_sync(
        self,
        prompt: str,
        context: AnalysisContext,
        custom_fields: Optional[set[CustomField]] = None,
    ) -> EvaluateMessageResponse:
        """
        Evaluate a user prompt that is sent to an LLM
        :param prompt: The text of the prompt to analyze
        :param context: Metadata for evaluation, fields that are not supplied will be taken from env vars
            session_id and user_id are required to group texts in the ActiveFence platform
        :param custom_fields: Optional set of predefined custom fields to include in the request
        :return: EvaluateMessageResponse object with analysis and detection results
        """
        return self._sync_internal_call(
            type=MessageType.PROMPT,
            text=prompt,
            session_id=context.session_id,
            user_id=context.user_id,
            provider=context.provider,
            model=context.model_name,
            version=context.model_version,
            platform=context.platform,
            custom_fields=custom_fields,
        )

    def evaluate_response_sync(
        self, response: Any, context: AnalysisContext, custom_fields: Optional[set[CustomField]] = None
    ) -> EvaluateMessageResponse:
        """
        Evaluate a return LLM response to a prompt.
        :param response: The LLM response to a given prompt
        :param context: Metadata for evaluation, fields that are not supplied will be taken from env vars
            session_id and user_id are required to group texts in the ActiveFence platform
        :param custom_fields: Optional set of predefined custom fields to include in the request
        :return: EvaluateMessageResponse object with analysis and detection results
        """
        return self._sync_internal_call(
            type=MessageType.RESPONSE,
            text=str(response),
            session_id=context.session_id,
            user_id=context.user_id,
            provider=context.provider,
            model=context.model_name,
            version=context.model_version,
            platform=context.platform,
            custom_fields=custom_fields,
        )

    async def evaluate_prompt(
        self, prompt: str, context: AnalysisContext, custom_fields: Optional[set[CustomField]] = None
    ) -> EvaluateMessageResponse:
        """
        Evaluate a user prompt that is sent to an LLM, using asyncio
        :param prompt: The text of the prompt to analyze
        :param context: Metadata for evaluation, fields that are not supplied will be taken from env vars
            session_id and user_id are required to group texts in the ActiveFence platform
        :param custom_fields: Optional set of predefined custom fields to include in the request
        :return: EvaluateMessageResponse object with analysis and detection results
        """
        return await self._async_internal_call(
            type=MessageType.PROMPT,
            text=prompt,
            session_id=context.session_id,
            user_id=context.user_id,
            provider=context.provider,
            model=context.model_name,
            version=context.model_version,
            platform=context.platform,
            custom_fields=custom_fields,
        )

    async def evaluate_response(
        self, response: Any, context: AnalysisContext, custom_fields: Optional[set[CustomField]] = None
    ) -> EvaluateMessageResponse:
        """
        Evaluate a return LLM response to a prompt, using asyncio.
        :param response: The LLM response to a given prompt
        :param context: Metadata for evaluation, fields that are not supplied will be taken from env vars
            session_id and user_id are required to group texts in the ActiveFence platform
        :param custom_fields: Optional set of predefined custom fields to include in the request
        :return: EvaluateMessageResponse object with analysis and detection results
        """
        return await self._async_internal_call(
            type=MessageType.RESPONSE,
            text=str(response),
            session_id=context.session_id,
            user_id=context.user_id,
            provider=context.provider,
            model=context.model_name,
            version=context.model_version,
            platform=context.platform,
            custom_fields=custom_fields,
        )
