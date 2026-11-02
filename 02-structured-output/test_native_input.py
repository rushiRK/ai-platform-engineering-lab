import unittest
from unittest.mock import patch

with patch("boto3.client"):
    import native_structured_output as native


class NativeInputTests(unittest.TestCase):
    def test_each_request_uses_its_argument(self):
        response = {
            "stopReason": "end_turn",
            "output": {"message": {"content": [{"text": "{}"}]}},
            "ResponseMetadata": {"RequestId": "test-request"},
            "usage": {
                "inputTokens": 1,
                "outputTokens": 1,
                "totalTokens": 2,
            },
        }

        with (
            patch.object(
                native,
                "customer_message",
                "WRONG: global message",
                create=True,
            ),
            patch.object(
                native.bedrock,
                "converse",
                return_value=response,
            ) as mock_converse,
        ):
            for message in (
                "Please cancel my subscription.",
                "My API is down.",
            ):
                with self.subTest(message=message):
                    native.invoke_structured(message)

                    request = mock_converse.call_args.kwargs
                    actual = request["messages"][0]["content"][0]["text"]

                    self.assertEqual(
                        actual,
                        "Classify this enterprise support ticket:\n\n"
                        + message,
                    )

            self.assertEqual(mock_converse.call_count, 2)


if __name__ == "__main__":
    unittest.main()