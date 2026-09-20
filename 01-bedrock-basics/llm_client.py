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