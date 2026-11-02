import unittest
from unittest.mock import patch
from botocore.exceptions import ClientError, ReadTimeoutError

import json
from pydantic import ValidationError
from schemas import SupportTicket

# Prevent AWS client initialization during this test import.
with patch("boto3.client"):
    import native_structured_output as app

def response_with(content):
    return {"output": {"message": {"content": content}}}


class ExtractTextTests(unittest.TestCase):
    def test_text_after_non_text_block(self):
        response = response_with([
            {"reasoningContent": {}},
            {"text": '{"category": "billing"}'},
        ])
        self.assertEqual(
            app.extract_text(response),
            '{"category": "billing"}',
        )

    def test_unusable_content_is_rejected(self):
        cases = [
            {},
            response_with(None),
            response_with([]),
            response_with([{"text": "   "}]),
            response_with([{"text": 123}]),
            response_with([{"text": "{}"}, {"text": "{}"}]),
        ]

        for response in cases:
            with self.subTest(response=response):
                with self.assertRaises(app.BedrockResponseError):
                    app.extract_text(response)

class InferenceFailureTests(unittest.TestCase):
    def test_incomplete_generation_is_rejected(self):
        for reason in ("max_tokens", "guardrail_intervened", None):
            with self.subTest(reason=reason):
                response = (
                    {} if reason is None else {"stopReason": reason}
                )

                with patch.object(
                    app.bedrock,
                    "converse",
                    return_value=response,
                ):
                    with self.assertRaises(app.BedrockGenerationError):
                        app.invoke_structured("Duplicate charge.")

    def test_service_error_preserves_details(self):
        original = ClientError(
            {
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "Simulated denial",
                },
                "ResponseMetadata": {"RequestId": "test-123"},
            },
            "Converse",
        )

        with patch.object(
            app.bedrock, "converse", side_effect=original
        ):
            with self.assertRaises(app.BedrockServiceError) as caught:
                app.invoke_structured("Duplicate charge.")

        self.assertEqual(caught.exception.code, "AccessDeniedException")
        self.assertEqual(caught.exception.request_id, "test-123")
        self.assertIs(caught.exception.__cause__, original)

    def test_timeout_preserves_original_exception(self):
        original = ReadTimeoutError(
            endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com"
        )

        with patch.object(
            app.bedrock, "converse", side_effect=original
        ):
            with self.assertRaises(app.BedrockTransportError) as caught:
                app.invoke_structured("Duplicate charge.")

        self.assertIs(caught.exception.__cause__, original)

VALID_TICKET = {
    "category": "billing",
    "priority": "medium",
    "summary": "Duplicate subscription charge.",
    "requires_human": True,
}


class InferenceSuccessTests(unittest.TestCase):
    def test_success_preserves_input_output_and_telemetry(self):
        raw_text = json.dumps(VALID_TICKET)
        response = {
            "stopReason": "end_turn",
            "output": {
                "message": {"content": [{"text": raw_text}]}
            },
            "ResponseMetadata": {"RequestId": "success-123"},
            "usage": {
                "inputTokens": 40,
                "outputTokens": 20,
                "totalTokens": 60,
            },
        }
        message = "I was charged twice for my subscription."

        with patch.object(
            app.bedrock, "converse", return_value=response
        ) as mock_converse:
            result = app.invoke_structured(message)

        mock_converse.assert_called_once()
        sent_text = mock_converse.call_args.kwargs[
            "messages"
        ][0]["content"][0]["text"]
        self.assertIn(message, sent_text)

        self.assertEqual(result["text"], raw_text)
        self.assertEqual(result["request_id"], "success-123")
        self.assertEqual(result["input_tokens"], 40)
        self.assertEqual(result["output_tokens"], 20)
        self.assertEqual(result["total_tokens"], 60)
        self.assertGreaterEqual(result["latency_seconds"], 0)

        ticket = SupportTicket.model_validate_json(result["text"])
        self.assertEqual(ticket.category, "billing")


class TicketValidationTests(unittest.TestCase):
    def test_valid_ticket_is_accepted(self):
        ticket = SupportTicket.model_validate_json(
            json.dumps(VALID_TICKET)
        )
        self.assertEqual(ticket.model_dump(), VALID_TICKET)

    def test_malformed_json_is_rejected(self):
        with self.assertRaises(ValidationError):
            SupportTicket.model_validate_json('{"category":')

    def test_schema_violations_are_rejected(self):
        missing_field = VALID_TICKET.copy()
        del missing_field["requires_human"]

        cases = {
            "invalid priority": {**VALID_TICKET, "priority": "critical"},
            "missing field": missing_field,
            "extra field": {**VALID_TICKET, "confidence": 0.99},
            "wrong type": {**VALID_TICKET, "requires_human": "yes"},
        }

        for name, payload in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(ValidationError):
                    SupportTicket.model_validate_json(
                        json.dumps(payload)
                    )

if __name__ == "__main__":
    unittest.main()