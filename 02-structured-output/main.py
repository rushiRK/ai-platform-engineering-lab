import json
import time

import boto3
from pydantic import ValidationError

from schemas import SupportTicket

REGION = "us-east-1"
MODEL_ID = "amazon.nova-micro-v1:0"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def build_prompt(customer_message: str) -> str:
    schema = SupportTicket.model_json_schema()

    return f"""
    You classify enterprise support tickets.

    Analyze the customer message and return ONLY valid JSON.

    Do not include:
    - markdown
    - code fences
    - explanations
    - text before or after the JSON

    The JSON must follow this schema:

    {json.dumps(schema, indent=2)}

    Customer message:

    {customer_message}
    """.strip()

def invoke_model(prompt: str) -> dict:
    start = time.perf_counter()

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{
           "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ],
            }
        ],
        inferenceConfig={
            "temperature": 0.0,
            "maxTokens": 300,
        
    })
    latency = time.perf_counter() - start

    return {
        "text": (response["output"]["message"]["content"][0]["text"]),
        "provider_request_id" : (response["ResponseMetadata"]["RequestId"]),
        "input_tokens": response["usage"]["inputTokens"],
        "output_tokens": response["usage"]["outputTokens"],
        "total_tokens": response["usage"]["totalTokens"],
        "latency_seconds": latency,
    }

def parse_and_validate(raw_text: str) -> SupportTicket:
    parse_json = json.loads(raw_text)
    return SupportTicket.model_validate(parse_json)

if __name__ == "__main__":
    customer_message = """
    Our production API started returning HTTP 500 errors
    after we rotated our credentials this morning.
    This is blocking customer traffic and we need help
    as soon as possible.
    """

    prompt = build_prompt(customer_message)
    result = invoke_model(prompt)

    print("\n RAW MODEL OUTPUT:")
    print(result["text"])

    print("\nTELEMENTRY:")
    print(
        f"Request ID: {result['provider_request_id']}"
    )
    print(
        f"Latency: {result['latency_seconds']:.3f} seconds"
    )
    print(
        f"Input tokens: {result['input_tokens']}"
    )
    print(
        f"Output tokens: {result['output_tokens']}"
    )

    print("\nVALIDATED OUTPUT:")
    try:
        ticket = parse_and_validate(
            result["text"]
        )

        print(
            ticket.model_dump_json(
                indent=2
            )
        )

    except json.JSONDecodeError as error:
        print("JSON PARSING FAILED")
        print(error)

    except ValidationError as error:
        print("SCHEMA VALIDATION FAILED")
        print(error)

