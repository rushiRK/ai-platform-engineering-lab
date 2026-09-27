from llm_client import LLMClient

MODELS = {
    "nova-micro": "amazon.nova-micro-v1:0",
    "nova-lite": "amazon.nova-lite-v1:0",
}

PROMPTS = [
    {
    "name": "simple",
    "prompt":( "Explain what an API gateway is in exactly two sentences." ),
    },
    {
        "name": "technical",
        "prompt":( "You are a senior platform engineer. "
                "Explain three reasons why an enterprise AI platform "
                "should place a gateway between applications and LLM providers." ),
    },
    {
        "name": "architecture",
        "prompt":( "Design a high-level enterprise AI gateway architecture "
            "supporting authentication, authorization, rate limiting, "
            "model routing, observability, and multiple LLM providers. "
            "Keep the answer under 250 words." ),
    },
]

MODEL_PRICING = {
    "nova-micro": {
        "input_per_million": 0.035,
        "output_per_million": 0.14,
    },
    "nova-lite": {
        "input_per_million": 0.06,
        "output_per_million": 0.24,
    },
}

INFERENCE_CONFIG = {
    "maxTokens" : 600,
    "temperature": 0.0,
}

def calculate_cost(model_name: str, input_token: int, output_token: int) -> float:
    pricing = MODEL_PRICING[model_name]
    input_cost = (input_token/1_000_000) * pricing["input_per_million"]
    output_cost = (output_token/1_000_000) * pricing["output_per_million"]

    return input_cost + output_cost



def print_result(model_name: str, result: dict):
    print(f"Model:          {model_name}")
    print(f"Status:         {result['status']}")
    print(f"Latency:        {result['latency_seconds']:.3f} sec")
    print(f"Input tokens:   {result['input_tokens']}")
    print(f"Output tokens:  {result['output_tokens']}")
    print(f"Total tokens:   {result['total_tokens']}")
    print()
    print("RESPONSE:")
    print(result["response"])

    cost = calculate_cost(model_name=model_name, input_token=result["input_tokens"], output_token=result["output_tokens"])
    print(f"Estimated cost: ${cost:.8f}")


if __name__ == "__main__":
    for test in PROMPTS:

        print("\n" + "=" * 80)
        print(f"PROMPT TYPE: {test['name']}")
        print("=" * 80)
        print(test["prompt"])

        for model_name, model_id in MODELS.items():
            print("\n" + "-" * 80)
            llm = LLMClient(model_id=model_id)
            result = llm.invoke(prompt=test["prompt"], inference_config=INFERENCE_CONFIG)
            print_result(model_name=model_name, result=result)
