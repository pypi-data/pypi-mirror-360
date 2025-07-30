import os

os.environ["ACTIVEFENCE_RETRY_MAX"] = "2"
os.environ["ACTIVEFENCE_RETRY_BASE_DELAY"] = "0.1"
import unittest
from unittest.mock import MagicMock, patch

import pytest
import responses
from activefence_client_sdk.client import ActiveFenceClient
from activefence_client_sdk.models import AnalysisContext, CustomField, EvaluateMessageResponse, MessageType
from requests.exceptions import ConnectTimeout

pytestmark = pytest.mark.citest


class TestActiveFenceClient(unittest.TestCase):
    def setUp(self) -> None:
        self.api_key = "test_api_key"
        self.app_name = "test_app"
        self.client = ActiveFenceClient(api_key=self.api_key, app_name=self.app_name)

    @patch("activefence_client_sdk.client.requests.post")
    def test_sync_internal_call_success(self, mock_post: MagicMock) -> None:
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "correlation_id": "test-correlation-id",
            "action": "",
            "detections": [],
            "errors": [],
        }
        mock_post.return_value = mock_response

        result = self.client._sync_internal_call(
            text="test text",
            type=MessageType.PROMPT,
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model="test_model",
            version="test_version",
            platform="test_platform",
        )

        self.assertIsInstance(result, EvaluateMessageResponse)
        self.assertEqual(result.action, "")
        self.assertIsNone(result.action_text)
        self.assertEqual(result.detections, [])
        self.assertEqual(result.errors, [])

    @patch("activefence_client_sdk.client.requests.post")
    def test_sync_internal_call_blocked(self, mock_post: MagicMock) -> None:
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "correlation_id": "test-correlation-id",
            "action": "BLOCK",
            "detections": [{"type": "test_reason", "score": 0.95}],
            "errors": [],
        }
        mock_post.return_value = mock_response

        result = self.client._sync_internal_call(
            text="test text",
            type=MessageType.PROMPT,
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model="test_model",
            version="test_version",
            platform="test_platform",
        )

        self.assertIsInstance(result, EvaluateMessageResponse)
        self.assertEqual(result.action, "BLOCK")
        self.assertIsNone(result.action_text)
        self.assertEqual(len(result.detections), 1)
        self.assertEqual(result.detections[0].type, "test_reason")
        self.assertEqual(result.errors, [])

    @patch("activefence_client_sdk.client.requests.post")
    def test_sync_internal_call_mask(self, mock_post: MagicMock) -> None:
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "correlation_id": "test-correlation-id",
            "action": "MASK",
            "action_text": "***** text",
            "detections": [{"type": "test_reason", "score": 0.85}],
            "errors": [],
        }
        mock_post.return_value = mock_response

        result = self.client._sync_internal_call(
            text="test text",
            type=MessageType.PROMPT,
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model="test_model",
            version="test_version",
            platform="test_platform",
        )

        self.assertIsInstance(result, EvaluateMessageResponse)
        self.assertEqual(result.action, "MASK")
        self.assertEqual(result.action_text, "***** text")
        self.assertEqual(len(result.detections), 1)
        self.assertEqual(result.detections[0].type, "test_reason")
        self.assertEqual(result.errors, [])

    @patch("activefence_client_sdk.client.requests.post")
    def test_evaluate_prompt(self, mock_post: MagicMock) -> None:
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "correlation_id": "test-correlation-id",
            "action": "",
            "detections": [],
            "errors": [],
        }
        mock_post.return_value = mock_response

        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = self.client.evaluate_prompt_sync(prompt="test prompt", context=context)

        self.assertIsInstance(result, EvaluateMessageResponse)
        self.assertEqual(result.action, "")
        self.assertIsNone(result.action_text)
        self.assertEqual(result.detections, [])
        self.assertEqual(result.errors, [])

    @patch("activefence_client_sdk.client.requests.post")
    def test_evaluate_response(self, mock_post: MagicMock) -> None:
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "correlation_id": "test-correlation-id",
            "action": "",
            "detections": [],
            "errors": [],
        }
        mock_post.return_value = mock_response

        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = self.client.evaluate_response_sync(response="test response", context=context)

        self.assertIsInstance(result, EvaluateMessageResponse)
        self.assertEqual(result.action, "")
        self.assertIsNone(result.action_text)
        self.assertEqual(result.detections, [])
        self.assertEqual(result.errors, [])

    @responses.activate  # type: ignore[misc]
    def test_sync_internal_call_timeout(self) -> None:
        # Simulate a timeout exception
        responses.add(
            responses.POST,
            "https://apis.activefence.com/v1/evaluate/message",
            body=ConnectTimeout(),
        )

        with self.assertRaises(ConnectTimeout):
            self.client._sync_internal_call(
                text="test text",
                type=MessageType.PROMPT,
                session_id="test_session",
                user_id="test_user",
                provider="test_provider",
                model="test_model",
                version="test_version",
                platform="test_platform",
            )

    @patch("activefence_client_sdk.client.requests.post")
    def test_evaluate_prompt_custom_fields(self, mock_post: MagicMock) -> None:
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "correlation_id": "test-correlation-id",
            "action": "",
            "detections": [],
            "errors": [],
        }
        mock_post.return_value = mock_response

        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = self.client.evaluate_prompt_sync(
            prompt="test prompt",
            context=context,
            custom_fields={
                CustomField(name="test_field", value="test_value"),
                CustomField(name="test_field", value="test_value"),
            },
        )

        self.assertIsInstance(result, EvaluateMessageResponse)
        self.assertEqual(result.action, "")
        self.assertIsNone(result.action_text)
        self.assertEqual(result.detections, [])
        self.assertEqual(result.errors, [])
        mock_post.assert_called_with(
            "https://apis.activefence.com/v1/evaluate/message",
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
                "custom_fields": [{"test_field": "test_value"}],
            },
            headers={"af-api-key": f"{self.api_key}", "Content-Type": "application/json"},
            timeout=5,
        )

    @patch("activefence_client_sdk.client.requests.post")
    def test_evaluate_response_custom_fields(self, mock_post: MagicMock) -> None:
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "correlation_id": "test-correlation-id",
            "action": "",
            "detections": [],
            "errors": [],
        }
        mock_post.return_value = mock_response

        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = self.client.evaluate_response_sync(
            response="test response",
            context=context,
            custom_fields={CustomField(name="test_field", value=["val1", "val2"])},
        )

        self.assertIsInstance(result, EvaluateMessageResponse)
        self.assertEqual(result.action, "")
        self.assertIsNone(result.action_text)
        self.assertEqual(result.detections, [])
        self.assertEqual(result.errors, [])
        mock_post.assert_called_with(
            "https://apis.activefence.com/v1/evaluate/message",
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
                "custom_fields": [{"test_field": ["val1", "val2"]}],
            },
            headers={"af-api-key": f"{self.api_key}", "Content-Type": "application/json"},
            timeout=5,
        )
