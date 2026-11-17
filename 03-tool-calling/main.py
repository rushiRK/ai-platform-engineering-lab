import json

import boto3
from botocore.config import Config

from tool_config import build_tool_config
from tool_executor import build_tool_result

REGION = "us-east-1"
MODEL_ID = "amazon.nova-micro-v1:0"

def request_service_status() -> dict:
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name = REGION,
        config = Config(
                connect_timeout=5,
                read_timeout=60,
                retries={"mode": "standard","total_max_attempts": 1,},
        ),
    )
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": (
                        "Use the get_service_status tool to check "
                        "the status of inference-gateway."
                    )
                }
            ],
        }
    ]

    tool_config = build_tool_config()
    inference_config = {"temperature": 0, "maxTokens": 300}

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=messages,
        toolConfig=tool_config,
        inferenceConfig=inference_config,
    )

    if response.get("stopReason") != "tool_use":
        raise RuntimeError(
            f"Expected tool_use; got {response.get('stopReason')!r}"
        )

    assistant_message = response["output"]["message"]

    tool_requests = [
        block["toolUse"]
        for block in assistant_message["content"]
        if "toolUse" in block
    ]

    if len(tool_requests) != 1:
        raise RuntimeError("This exercise expects exactly one tool request")

    tool_request = tool_requests[0]

    tool_result = build_tool_result(
       tool_request=tool_request,
        allowed_services={"inference-gateway"},
    )

    print("TOOL RESULT:")
    print(json.dumps(tool_result, indent=2))

    messages.append(assistant_message)
    messages.append(
        {
            "role": "user",
            "content": [{"toolResult": tool_result}],
        }
    )

    final_response = bedrock.converse(
        modelId=MODEL_ID,
        messages=messages,
        toolConfig=tool_config,
        inferenceConfig=inference_config,
    )

    if final_response.get("stopReason") != "end_turn":
        raise RuntimeError(
            "Expected a final answer after one tool round; "
            f"got {final_response.get('stopReason')!r}"
        )

    return final_response

if __name__=="__main__":
    response = request_service_status()
    print("STOP REASON:")
    print(response.get("stopReason"))

    print("\nASSISTANT MESSAGE:")
    print(json.dumps(response.get("output", {}).get("message"), indent=2))