import unittest
from unittest.mock import patch

from tool_executor import build_tool_result


class ToolExecutorTests(unittest.TestCase):
    def test_allowed_request_executes_and_returns_result(self):
        request = {
            "toolUseId": "request-123",
            "name": "get_service_status",
            "input": {"service_name": "inference-gateway"},
        }
        expected = {
            "service_name": "inference-gateway",
            "status": "healthy",
        }

        with patch(
            "tool_executor.get_service_status",
            return_value=expected,
        ) as mock_tool:
            result = build_tool_result(
                request,
                allowed_services={"inference-gateway"},
            )

        mock_tool.assert_called_once_with("inference-gateway")
        self.assertEqual(
            result,
            {
                "toolUseId": "request-123",
                "content": [{"json": expected}],
                "status": "success",
            },
        )

    def test_rejected_requests_never_execute(self):
        cases = [
            (
                "invalid arguments",
                "get_service_status",
                {"service_name": 123},
                "INVALID_ARGUMENTS",
            ),
            (
                "unauthorized service",
                "get_service_status",
                {"service_name": "model-router"},
                "ACCESS_DENIED",
            ),
            (
                "unknown tool",
                "delete_service",
                {"service_name": "inference-gateway"},
                "ACCESS_DENIED",
            ),
        ]

        for label, tool_name, arguments, expected_error in cases:
            with self.subTest(case=label):
                request = {
                    "toolUseId": "request-456",
                    "name": tool_name,
                    "input": arguments,
                }

                with patch(
                    "tool_executor.get_service_status"
                ) as mock_tool:
                    result = build_tool_result(
                        request,
                        allowed_services={"inference-gateway"},
                    )

                mock_tool.assert_not_called()
                self.assertEqual(result["toolUseId"], "request-456")
                self.assertEqual(result["status"], "error")
                self.assertEqual(
                    result["content"],
                    [{"json": {"error": expected_error}}],
                )

    def test_unknown_service_returns_execution_error(self):
        request = {
            "toolUseId": "request-789",
            "name": "get_service_status",
            "input": {"service_name": "missing-service"},
        }

        result = build_tool_result(
            request,
            allowed_services={"missing-service"},
        )

        self.assertEqual(
            result,
            {
                "toolUseId": "request-789",
                "content": [
                    {"json": {"error": "TOOL_EXECUTION_FAILED"}}
                ],
                "status": "error",
            },
        )

    def test_tool_timeout_returns_error_without_retry(self):
        request = {
            "toolUseId": "timeout-request",
            "name": "get_service_status",
            "input": {"service_name": "inference-gateway"},
        }

        with patch(
            "tool_executor.get_service_status",
            side_effect=TimeoutError("Internal connection details"),
        ) as mock_tool:
            result = build_tool_result(
                request,
                allowed_services={"inference-gateway"},
            )

        mock_tool.assert_called_once_with("inference-gateway")
        self.assertEqual(
            result,
            {
                "toolUseId": "timeout-request",
                "content": [{"json": {"error": "TOOL_TIMEOUT"}}],
                "status": "error",
            },
        )

    
    

if __name__ == "__main__":
    unittest.main()