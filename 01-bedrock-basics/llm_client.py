import time
import boto3

class LLMClient:
    def __init__(self, model_id: str, region: str = "us-east-1"):
        self.model_id = model_id
        self.region = region

        self.client = boto3.client(
            "bedrock-runtime",
            region_name = self.region
        )

    def invoke(self, prompt: str):
        statrt = time.perf_counter()

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
            "model": self.model_id,
            "latency_seconds": latency,
            "input_tokens": response["usage"]["inputTokens"],
            "output_tokens": response["usage"]["outputTokens"],
            "total_tokens": response["usage"]["totalTokens"],
            "text": response["output"]["message"]["content"][0]["text"],
            "response": response,
        }