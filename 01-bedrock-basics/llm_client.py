import time
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

class LLMClient:
    def __init__(
            self,
            model_id: str,
            region: str = "us-east-1",
    ):
        self.model_id = model_id
        self.region = region

        self.client = boto3.client(
            "bedrock-runtime",
            region_name = self.region
        )

    def invoke(self, prompt: str):
        request_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        statrt = time.perf_counter()
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            latency = time.perf_counter() - statrt

            return {
                "request_id": request_id,
                "provider_request_id": response["ResponseMetadata"]["RequestId"],
                "timestamp": timestamp,
                "model": self.model_id,
                "status": "success",
                "latency_seconds": latency,
                "input_tokens": response["usage"]["inputTokens"],
                "output_tokens": response["usage"]["outputTokens"],
                "total_tokens": response["usage"]["totalTokens"],
                "text": response["output"]["message"]["content"][0]["text"],
                "response": response["output"]["message"]["content"][0]["text"],
                "error_code": None,
                "error_message": None,
            }
        except ClientError as error:
            latency = time.perf_counter() - statrt
            return {
                "request_id": request_id,
                "provider_request_id": error.response.get("ResponseMetadata",{}).get("RequestId"),
                "timestamp": timestamp,
                "model": self.model_id,
                "status": "error",
                "latency_seconds": latency,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "response": None,
                "error_code": error.response["Error"]["Code"],
                "error_message": error.response["Error"]["Message"],
            }

    def stream(self, prompt: str):
        status = "success"
        error_code = None
        error_message = None
        request_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        start = time.perf_counter()
        first_content_latency = None

        input_tokens = None
        output_tokens = None
        total_tokens = None
        stop_response = None

        chunks = []

        response = self.client.converse_stream(
            modelId = self.model_id,
            messages = [{
                "role": "user",
                "content" : [
                    {
                        "text": prompt
                    }
                ]
            }],
        )
        provider_request_id = response["ResponseMetadata"]["RequestId"]
        for event in response["stream"]:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]

                if "text" in delta:
                    if first_content_latency is None:
                        first_content_latency = time.perf_counter() - start
                    text = delta["text"]
                    chunks.append(text)
                    print(text, end="", flush=True,)
            elif "messageStop" in event:
                stop_reason = event["messageStop"]["stopReason"]

            elif "metadata" in event:
                usage = event["metadata"]["usage"]
                input_tokens = usage["inputTokens"]
                output_tokens = usage["outputTokens"]
                total_tokens = usage["totalTokens"]

            elif "modelStreamErrorException" in event:
                status = "Error"
                error_code = "modelStreamErrorException"
                error_message = event["modelStreamErrorException"].get("message")

            elif "internalServerException" in event:
                status = "error"
                error_code = "InternalServerException"
                error_message = event["internalServerException"].get("message")

            elif "serviceUnavailableException" in event:
                status = "error"
                error_code = "ServiceUnavailableException"
                error_message = event[
                    "serviceUnavailableException"
                ].get("message")

            elif "throttlingException" in event:
                status = "error"
                error_code = "ThrottlingException"
                error_message = event[
                    "throttlingException"
                ].get("message")

            elif "validationException" in event:
                status = "error"
                error_code = "ValidationException"
                error_message = event[
                    "validationException"
                ].get("message")

        total_latency = time.perf_counter() - start
        full_response = "".join(chunks)
        if status == "error" and full_response:
            status = "partial_error"

        return{
            "request_id": request_id,
            "provider_request_id": provider_request_id,
            "timestamp": timestamp,
            "model": self.model_id,
            "status": status,
            "streaming": True,
            "time_to_first_content_seconds": first_content_latency,
            "latency_seconds": total_latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "stop_reason": stop_reason,
            "response": "".join(chunks),
            "error_code": error_code,
            "error_message": error_message,
        }