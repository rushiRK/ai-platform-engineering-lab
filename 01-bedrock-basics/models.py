from dataclasses import dataclass
from typing import Optional

@dataclass
class TokenUsage:
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]

@dataclass
class LLMResponse:
    request_id: str
    provider_request_id: Optional[str]
    timestamp: str

    model: str
    status: str

    response: Optional[str]

    latency_seconds: float
    time_to_first_content_seconds: Optional[float]

    usage: TokenUsage

    stop_reason: Optional[str]

    error_code: Optional[str]
    error_message: Optional[str]

MODEL_RESIGSTERY = {
    "nova-micro": {
        "provider": "bedrock",
        "model_id": "amazon.nova-micro-v1:0",
    },
    "nova-lite": {
        "provider": "bedrock",
        "model_id": "amazon.nova-lite-v1:0",
    },    
}
