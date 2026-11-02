from unittest.mock import Mock, patch

with patch("boto3.client"):
    import native_structured_output as native

native.bedrock = Mock()
native.bedrock.converse.return_value = {
    "output": {"message": {"content": [{"text": "{}"}]}},
    "ResponseMetadata": {"RequestId": "test-request"},
    "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
}

# Deliberately conflicting global value exposes the original bug.
native.customer_message = "WRONG: global message"

for message in ["Please cancel my subscription.", "My API is down."]:
    native.invoke_structured(message)
    request = native.bedrock.converse.call_args.kwargs
    actual = request["messages"][0]["content"][0]["text"]
    assert actual == "Classify this enterprise support ticket:\n\n" + message

print("PASS: each request uses its function argument")