import sys
import json
import time

import boto3

from pydantic import ValidationError
from schemas import SupportTicket
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    ConnectTimeoutError,
    ReadTimeoutError,
)

REGION = "us-east-1"
MODEL_ID = "qwen.qwen3-32b-v1:0"


bedrock = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
)

class BedrockServiceError(RuntimeError):
    def __init__(self, code:str, request_id: str):
        self.code = code
        self.request_id = request_id
        super().__init__(f"Bedrock service error: {code}; request_id={request_id}")

class BedrockTransportError(RuntimeError):
    pass

class BedrockGenerationError(RuntimeError):
    pass

class BedrockResponseError(RuntimeError):
    pass

def check_stop_reason(response: dict) -> None:
    stop_reason = response.get("stopReason")
    if stop_reason != "end_turn":
        raise BedrockGenerationError(
            f"Expected completed generation; stopReason={stop_reason!r}"
        )

def extract_text(response: dict) -> str:
    try:
        content = response["output"]["message"]["content"]
    except (KeyError, TypeError) as error:
        raise BedrockResponseError(
            "Response is missing message content"
        ) from error

    if not isinstance(content, list):
        raise BedrockResponseError("Message content must be a list")

    texts = [
        block["text"]
        for block in content
        if isinstance(block, dict) and "text" in block
    ]

    if len(texts) != 1:
        raise BedrockResponseError(
            "Expected exactly one text block"
        )

    text = texts[0]
    if not isinstance(text, str) or not text.strip():
        raise BedrockResponseError("Response text is empty or invalid")

    return text
def invoke_structured(customer_message: str):
    schema = SupportTicket.model_json_schema()
    start = time.perf_counter()
    try:

        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": (
                                "Classify this enterprise support ticket:\n\n"
                                + customer_message
                            )
                        }
                    ],
                }
            ],
            inferenceConfig={
                "temperature": 0.0,
                "maxTokens": 300,
            },
            outputConfig={
                "textFormat": {
                    "type": "json_schema",
                    "structure": {
                        "jsonSchema": {
                            "name": "support_ticket",
                            "description": (
                                "Classification of an enterprise "
                                "support ticket"
                            ),
                            "schema": json.dumps(schema),
                        }
                    },
                }
            },
        )
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "Unknown")
        request_id = error.response.get("ResponseMetadata", {}).get("RequestId", "unknown")
        raise BedrockServiceError(code, request_id) from error
    except (EndpointConnectionError,ConnectTimeoutError,ReadTimeoutError,) as error:
        raise BedrockTransportError(
            f"Bedrock connection or timeout failure: {type(error).__name__}"
        ) from error
    latency = time.perf_counter() - start
    check_stop_reason(response)

    return {
        "text": extract_text(response),
        "request_id": response[
            "ResponseMetadata"
        ]["RequestId"],
        "input_tokens": response["usage"]["inputTokens"],
        "output_tokens": response["usage"]["outputTokens"],
        "total_tokens": response["usage"]["totalTokens"],
        "latency_seconds": latency,
    }


if __name__=="__main__":
    customer_message = """
    Our production API started returning HTTP 500 errors
    after we rotated our credentials this morning.
    This is blocking customer traffic and we need help
    as soon as possible.
    """

    try:
        result = invoke_structured(customer_message)
        ticket = SupportTicket.model_validate_json(result["text"])

    except BedrockServiceError as error:
        print(f"SERVICE FAILED: {error}", file=sys.stderr)
        sys.exit(1)

    except BedrockTransportError as error:
        print(f"TRANSPORT FAILED: {error}", file=sys.stderr)
        sys.exit(1)

    except BedrockGenerationError as error:
        print(f"GENERATION FAILED: {error}", file=sys.stderr)
        sys.exit(1)

    except BedrockResponseError as error:
        print(f"RESPONSE FAILED: {error}", file=sys.stderr)
        sys.exit(1)

    except ValidationError as error:
        print(
            f"VALIDATION FAILED: {error.error_count()} error(s)",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\nVALIDATED TICKET:")
    print(ticket.model_dump_json(indent=2))

    print("\nTELEMETRY:")
    print(f"Request ID: {result['request_id']}")
    print(f"Latency: {result['latency_seconds']:.3f} seconds")
    print(f"Input tokens: {result['input_tokens']}")
    print(f"Output tokens: {result['output_tokens']}")
    print(f"Total tokens: {result['total_tokens']}")