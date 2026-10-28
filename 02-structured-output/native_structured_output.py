import json
import time

import boto3

from pydantic import ValidationError
from schemas import SupportTicket

REGION = "us-east-1"
MODEL_ID = "qwen.qwen3-32b-v1:0"


bedrock = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
)

def invoke_structured(cusomer_message: str):
    schema = SupportTicket.model_json_schema()
    start = time.perf_counter()
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

    latency = time.perf_counter() - start

    return {
        "text": response[
            "output"
        ]["message"]["content"][0]["text"],
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

    result = invoke_structured(customer_message)

    print("\nRAW BEDROCK OUTPUT:")
    print(result["text"])

    print("\nTELEMETRY:")
    print(f"Request ID: {result['request_id']}")
    print(
        f"Latency: {result['latency_seconds']:.3f} seconds"
    )
    print(f"Input tokens: {result['input_tokens']}")
    print(f"Output tokens: {result['output_tokens']}")
    print(f"Total tokens: {result['total_tokens']}")

    print("\nPYDANTIC VALIDATION:")

    try:
        ticket = SupportTicket.model_validate_json(
            result["text"]
        )

        print(
            ticket.model_dump_json(
                indent=2
            )
        )

    except ValidationError as error:
        print("VALIDATION FAILED")
        print(error)