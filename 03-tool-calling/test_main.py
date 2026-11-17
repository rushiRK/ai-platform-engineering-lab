import unittest
from copy import deepcopy
from unittest.mock import patch
import io

from main import request_service_status
from main import cli
from botocore.exceptions import ReadTimeoutError


class ToolCallingFlowTests(unittest.TestCase):
    def test_round_trip_preserves_history_and_tool_id(self):
        assistant_message = {
            "role": "assistant",
            "content": [
                {"text": "I will check the service."},
                {
                    "toolUse": {
                        "toolUseId": "tool-request-123",
                        "name": "get_service_status",
                        "input": {
                            "service_name": "inference-gateway",
                        },
                    }
                },
            ],
        }

        first_response = {
            "stopReason": "tool_use",
            "output": {"message": assistant_message},
        }

        final_response = {
            "stopReason": "end_turn",
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": "The service is healthy."}],
                }
            },
        }

        responses = iter([first_response, final_response])
        captured_requests = []

        def fake_converse(**kwargs):
            captured_requests.append(deepcopy(kwargs))
            return next(responses)

        with patch("main.boto3.client") as mock_client:
            bedrock = mock_client.return_value
            bedrock.converse.side_effect = fake_converse

            result = request_service_status()

        self.assertEqual(bedrock.converse.call_count, 2)
        self.assertEqual(result, final_response)

        first_request, second_request = captured_requests

        self.assertEqual(len(first_request["messages"]), 1)
        self.assertEqual(first_request["messages"][0]["role"], "user")

        history = second_request["messages"]
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], first_request["messages"][0])
        self.assertEqual(history[1], assistant_message)
        self.assertEqual(history[2]["role"], "user")

        tool_result = history[2]["content"][0]["toolResult"]

        self.assertEqual(tool_result["toolUseId"], "tool-request-123")
        self.assertEqual(tool_result["status"], "success")
        self.assertEqual(
            tool_result["content"],
            [
                {
                    "json": {
                        "service_name": "inference-gateway",
                        "status": "healthy",
                    }
                }
            ],
        )

        self.assertEqual(
            first_request["toolConfig"],
            second_request["toolConfig"],
        )

    def test_second_tool_request_does_not_execute_again(self):
        def tool_response(tool_use_id):
            return {
                "stopReason": "tool_use",
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "toolUse": {
                                    "toolUseId": tool_use_id,
                                    "name": "get_service_status",
                                    "input": {
                                        "service_name": "inference-gateway",
                                    },
                                }
                            }
                        ],
                    }
                },
            }

        with (
            patch("main.boto3.client") as mock_client,
            patch(
                "tool_executor.get_service_status",
                return_value={
                    "service_name": "inference-gateway",
                    "status": "healthy",
                },
            ) as mock_tool,
        ):
            bedrock = mock_client.return_value
            bedrock.converse.side_effect = [
                tool_response("first-request"),
                tool_response("second-request"),
            ]

            with self.assertRaisesRegex(
                RuntimeError,
                "Expected a final answer after one tool round",
            ):
                request_service_status()

            self.assertEqual(bedrock.converse.call_count, 2)
            mock_tool.assert_called_once_with("inference-gateway")

    def test_final_bedrock_timeout_does_not_repeat_tool(self):
        first_response = {
            "stopReason": "tool_use",
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "toolUse": {
                                "toolUseId": "request-before-timeout",
                                "name": "get_service_status",
                                "input": {
                                    "service_name": "inference-gateway",
                                },
                            }
                        }
                    ],
                }
            },
        }

        timeout = ReadTimeoutError(
            endpoint_url=(
                "https://bedrock-runtime.us-east-1.amazonaws.com"
            )
        )

        with (
            patch("main.boto3.client") as mock_client,
            patch(
                "tool_executor.get_service_status",
                return_value={
                    "service_name": "inference-gateway",
                    "status": "healthy",
                },
            ) as mock_tool,
        ):
            bedrock = mock_client.return_value
            bedrock.converse.side_effect = [
                first_response,
                timeout,
            ]

            with self.assertRaises(ReadTimeoutError) as caught:
                request_service_status()

            self.assertIs(caught.exception, timeout)
            self.assertEqual(bedrock.converse.call_count, 2)
            mock_tool.assert_called_once_with("inference-gateway")
    
    def test_cli_reports_timeout_and_returns_failure(self):
        timeout = ReadTimeoutError(
            endpoint_url="https://example.invalid"
        )

        with (
            patch(
                "main.request_service_status",
                side_effect=timeout,
            ) as mock_request,
            patch("sys.stderr", new_callable=io.StringIO) as stderr,
        ):
            exit_code = cli()

        self.assertEqual(exit_code, 1)
        self.assertIn(
            "AWS SDK FAILED: ReadTimeoutError",
            stderr.getvalue(),
        )
        mock_request.assert_called_once_with()
if __name__ == "__main__":
    unittest.main()