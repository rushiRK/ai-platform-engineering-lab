from client import LLMClient

client = LLMClient(model="nova-micro")

if __name__=="__main__":
    result = client.invoke("Explain what an AI platform is in three sentences.")
    print("Status:", result.status)
    print("Model:", result.model)
    print(
        f"Latency: {result.latency_seconds:.3f} seconds"
    )

    print(
        "Input tokens:",
        result.usage.input_tokens,
    )

    print(
        "Output tokens:",
        result.usage.output_tokens,
    )

    print(
        "Total tokens:",
        result.usage.total_tokens,
    )

    print()
    print("Response:")
    print(result.response)





#from llm_client import LLMClient
#MODEL_ID = "amazon.nova-micro-v1:0"

#llm = LLMClient(model_id=MODEL_ID)

#if __name__ == "__main__":
#     result = llm.stream(
#          "Explain why streaming is useful"
#          "for an interactive LLM chatbot in three sentences."
#          )

#     print("\n STREAM METRICS:")
#     print(json.dumps(result, indent=2))
    # prompts = [
    #     "Explain what a distributed system is in one sentence.",
    #     "Explain what a distributed system is to a 10-year-old.",
    #     """
    #     You are a senior distributed systems engineer.
    #     Explain three major challenges in distributed systems
    #     and give one example of each.
    #     """,
    # ]
    # for prompt in prompts:
    #     print("\n" + "=" * 80)
    #     print(prompt.strip())
    #     result = llm.invoke(prompt)
    #     print("\n RESULT :")
    #     print(json.dumps(result, indent=2))

    # print("\n" + "=" * 80)
    # print("ERROR TEST: Invalid Model")

    # invalid_llm = LLMClient(model_id="this-model-does-not-exist")

    # result = invalid_llm.invoke("Explain distributed systems.")

    # print("\n RESULT:")
    # print(json.dumps(result, indent=2))
