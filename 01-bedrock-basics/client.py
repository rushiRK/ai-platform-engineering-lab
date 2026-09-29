from llm_client import LLMClient as BedrockLLMClient
from models import LLMResponse, MODEL_RESIGSTERY, TokenUsage

class LLMClient:
    def __init__(self, model: str, region: str = "us-east-1",):
        if model not in MODEL_RESIGSTERY:
            raise ValueError(f"UNKNOWN MODEL:{model}")

        model_config = MODEL_RESIGSTERY[model]

        self.model_name = model
        self.model_id = model_config["model_id"]
        self.provider = model_config["provider"]

        if self.provider != "bedrock":
            raise ValueError(
                f"UNSUPPORTED PROVIDER: {self.provider}"
            )

        self.client = BedrockLLMClient(model_id=self.model_id, region=region)

    def invoke(self, prompt: str, inference_config: dict | None = None,) -> LLMResponse:
        result = self.client.invoke(prompt=prompt, inference_config = inference_config,)

        return LLMResponse(
            request_id=result["request_id"],

            provider_request_id=result.get(
                "provider_request_id"
            ),

            timestamp=result["timestamp"],

            model=self.model_name,

            status=result["status"],

            response=result.get("response"),

            latency_seconds=result[
                "latency_seconds"
            ],

            time_to_first_content_seconds=None,

            usage=TokenUsage(
                input_tokens=result.get(
                    "input_tokens"
                ),
                output_tokens=result.get(
                    "output_tokens"
                ),
                total_tokens=result.get(
                    "total_tokens"
                ),
            ),

            stop_reason=result.get(
                "stop_reason"
            ),

            error_code=result.get(
                "error_code"
            ),

            error_message=result.get(
                "error_message"
            ),)