from llm_client import LLMClient


MODEL_ID = "amazon.nova-micro-v1:0"

llm = LLMClient(model_id=MODEL_ID)

if __name__ == "__main__":
    result = llm.invoke("Explain what a Large Language Model (LLM) is in three sentences.")
    print("Model:", result["model"])
    print(f"Latency: {result['latency_seconds']:.3f} seconds")
    print("Input tokens:", result["input_tokens"])
    print("Output tokens:", result["output_tokens"])
    print("Total tokens:", result["total_tokens"])
    print("Response:", result["text"])