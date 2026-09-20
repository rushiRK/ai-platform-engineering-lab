# Bedrock Basics

## Objective

Understand the lifecycle of an LLM inference request using Amazon Bedrock.

## Architecture

Application
    |
    v
LLMClient
    |
    v
Amazon Bedrock
    |
    v
Foundation Model

## Model

Amazon Nova Micro

Model ID:

`amazon.nova-micro-v1:0`

## Captured Metrics

- Model ID
- Input tokens
- Output tokens
- Total tokens
- Client-side latency
- Generated response

## Authentication

AWS authentication is handled through IAM Identity Center using temporary
credentials and a PowerUserAccess permission set.

No AWS credentials are stored in the application code.

## Questions

1. What happens during an inference request?
2. What metadata should an enterprise AI gateway capture?
3. Why should applications use an abstraction layer instead of directly calling a model provider?
4. What happens if the model provider is unavailable?
5. How could we route requests between multiple models?

Day 2 — Model API Observations
Request and Response

Each LLM invocation sends a structured request to Amazon Bedrock using the Converse API. The response contains the generated model output along with usage and request metadata.

Platform Telemetry

Each inference request captures:

Request ID
Provider request ID
Timestamp
Model ID
Status
Client-side latency
Input tokens
Output tokens
Total tokens
Response
Error code and error message when applicable
Prompt Behavior

Different prompts can produce significantly different token usage and response characteristics even when they ask about the same topic.

For example, asking for a one-sentence explanation generated far fewer output tokens than asking for an explanation targeted at a child or requesting a detailed engineering explanation.

Token usage therefore depends not only on the size of the input prompt but also on the instructions given to the model and the amount of output it generates.

Latency

Inference latency varies between requests.

Longer outputs can increase latency, but latency is also affected by factors outside token count, including network overhead and provider-side processing. Individual requests are not sufficient for drawing conclusions about latency performance; production systems should measure latency distributions across many requests.

Error Handling

An invalid model identifier produced a Bedrock ValidationException.

The failed request completed much faster than a successful inference because Bedrock rejected the request before model generation occurred.

Not all failures happen at the same layer. For example, an expired AWS SSO token can fail during credential resolution before a request ever reaches Bedrock, while an invalid model ID is rejected by Bedrock itself.

Platform Engineering Takeaway

An AI platform should capture standardized metadata for every inference request rather than allowing each application to implement its own telemetry.

A consistent request record provides the foundation for future capabilities such as observability, cost tracking, debugging, rate limiting, model routing, reliability monitoring, and auditing.