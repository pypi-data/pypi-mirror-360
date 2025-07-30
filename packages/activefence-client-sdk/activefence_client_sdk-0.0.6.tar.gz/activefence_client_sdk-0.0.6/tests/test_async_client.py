import os

os.environ["ACTIVEFENCE_RETRY_MAX"] = "2"
os.environ["ACTIVEFENCE_RETRY_BASE_DELAY"] = "0.1"
import pytest
from activefence_client_sdk.client import ActiveFenceClient
from activefence_client_sdk.models import AnalysisContext, CustomField, EvaluateMessageResponse
from aiohttp import ClientConnectionError
from aioresponses import aioresponses

pytestmark = pytest.mark.citest


@pytest.mark.asyncio  # type: ignore[misc]
async def test_evaluate_prompt_async() -> None:
    with aioresponses() as mocker:
        mocker.post(
            url="https://apis.activefence.com/v1/evaluate/message",
            status=200,
            payload={
                "correlation_id": "test-correlation-id",
                "action": "",
                "detections": [],
                "errors": [],
            },
        )

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = await client.evaluate_prompt(prompt="test prompt", context=context)

        assert isinstance(result, EvaluateMessageResponse)
        assert result.action == ""
        assert result.action_text is None
        assert result.detections == []
        assert result.errors == []


@pytest.mark.asyncio  # type: ignore[misc]
async def test_evaluate_response_async() -> None:
    with aioresponses() as mocker:
        mocker.post(
            url="https://apis.activefence.com/v1/evaluate/message",
            status=200,
            payload={
                "correlation_id": "test-correlation-id",
                "action": "",
                "detections": [],
                "errors": [],
            },
        )

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = await client.evaluate_response(response="test response", context=context)

        assert isinstance(result, EvaluateMessageResponse)
        assert result.action == ""
        assert result.action_text is None
        assert result.detections == []
        assert result.errors == []


@pytest.mark.asyncio  # type: ignore[misc]
async def test_evaluate_response_timeout() -> None:
    with aioresponses() as mocker:
        mocker.post(url="https://apis.activefence.com/v1/evaluate/message", timeout=True)

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )

        with pytest.raises(ClientConnectionError):
            await client.evaluate_response(response="test response", context=context)


@pytest.mark.asyncio  # type: ignore[misc]
async def test_evaluate_prompt_async_custom_fields() -> None:
    with aioresponses() as mocker:
        mocker.post(
            url="https://apis.activefence.com/v1/evaluate/message",
            status=200,
            payload={
                "correlation_id": "test-correlation-id",
                "action": "",
                "detections": [],
                "errors": [],
            },
        )

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = await client.evaluate_prompt(
            prompt="test prompt", context=context, custom_fields={CustomField(name="test_field", value=123)}
        )

        assert isinstance(result, EvaluateMessageResponse)
        assert result.action == ""
        assert result.action_text is None
        assert result.detections == []
        assert result.errors == []
        mocker.assert_called_with(
            "https://apis.activefence.com/v1/evaluate/message",
            "POST",
            json={
                "text": "test prompt",
                "message_type": "prompt",
                "session_id": "test_session",
                "user_id": "test_user",
                "app_name": "test_app",
                "model_context": {
                    "provider": "test_provider",
                    "name": "test_model",
                    "version": "test_version",
                    "cloud_platform": "test_platform",
                },
                "custom_fields": [{"test_field": 123}],
            },
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
                "af-api-key": "test_api_key",
                "Content-Type": "application/json",
            },
            timeout=client.timeout_seconds,
        )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_evaluate_response_async_custom_fields() -> None:
    with aioresponses() as mocker:
        mocker.post(
            url="https://apis.activefence.com/v1/evaluate/message",
            status=200,
            payload={
                "correlation_id": "test-correlation-id",
                "action": "",
                "detections": [],
                "errors": [],
            },
        )

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = await client.evaluate_response(
            response="test response", context=context, custom_fields={CustomField(name="test_field", value=True)}
        )

        assert isinstance(result, EvaluateMessageResponse)
        assert result.action == ""
        assert result.action_text is None
        assert result.detections == []
        assert result.errors == []
        mocker.assert_called_with(
            "https://apis.activefence.com/v1/evaluate/message",
            "POST",
            json={
                "text": "test response",
                "message_type": "response",
                "session_id": "test_session",
                "user_id": "test_user",
                "app_name": "test_app",
                "model_context": {
                    "provider": "test_provider",
                    "name": "test_model",
                    "version": "test_version",
                    "cloud_platform": "test_platform",
                },
                "custom_fields": [{"test_field": True}],
            },
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
                "af-api-key": "test_api_key",
                "Content-Type": "application/json",
            },
            timeout=client.timeout_seconds,
        )
