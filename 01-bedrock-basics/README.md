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

## Day 3 — Streaming Inference

### Objective

Understand how streaming changes the lifecycle of an LLM inference request and what additional telemetry an AI platform should capture.

### Streaming Flow

A synchronous inference request waits for the full model response before returning content.

A streaming request returns generated content incrementally:

```text
Application
    |
    v
LLMClient
    |
    v
Amazon Bedrock ConverseStream
    |
    +--> content chunk
    +--> content chunk
    +--> content chunk
    |
    v
Final metadata
```

### Captured Streaming Metrics

Each streaming request captures:

- Request ID
- Provider request ID
- Timestamp
- Model ID
- Status
- Streaming flag
- Time to first content
- Total latency
- Input tokens
- Output tokens
- Total tokens
- Stop reason
- Reconstructed response
- Error information

### Time to First Content

Streaming introduces an important latency metric:

`time_to_first_content_seconds`

This measures how long the application waits before receiving the first generated content from the model.

This is different from total inference latency.

For example, one test produced approximately:

```text
Time to first content: 1.27 seconds
Total latency:         1.52 seconds
```

The model still required the full 1.52 seconds to complete generation, but the user began receiving content earlier.

Streaming therefore primarily improves perceived responsiveness rather than necessarily reducing total inference time.

### Streaming Events

Amazon Bedrock streaming responses contain multiple event types.

Generated text arrives through content delta events, while usage metadata is provided later in the stream.

The application must process the stream incrementally while also collecting enough information to reconstruct the complete response and produce final telemetry.

### Partial Failures

Streaming introduces a failure mode that does not exist in the same way with ordinary synchronous requests.

A provider may successfully deliver part of a response and then encounter an error.

For example:

```text
chunk 1
chunk 2
chunk 3
ERROR
```

The client has already received part of the model output.

The platform therefore needs to distinguish between states such as:

```text
success
error
partial_error
```

A partial failure is different from a request that fails before any content is delivered.

### Platform Engineering Takeaway

An AI Gateway cannot treat streaming inference exactly like a traditional synchronous REST request.

The gateway must:

- Forward generated chunks without waiting for the full response
- Measure time to first content
- Track total latency
- Reconstruct responses when needed
- Capture final token usage
- Detect mid-stream failures
- Preserve request and provider correlation IDs
- Handle cases where final metadata is unavailable

This makes streaming an important architectural concern for a production AI platform.
## Day 4 — Model Comparison

### Objective

Compare multiple foundation models using the same workloads and begin identifying the information an AI platform needs for model selection and routing.

### Models

The experiment compared:

- Amazon Nova Micro
- Amazon Nova Lite

The same prompts and inference configuration were used for both models.

### Workloads

Three types of prompts were tested:

1. Simple explanation
2. Technical platform-engineering explanation
3. AI gateway architecture design

For each request, the experiment captured:

- Model
- Latency
- Input tokens
- Output tokens
- Total tokens
- Generated response
- Estimated inference cost

### Observations

Model behavior differed even when both models received identical prompts.

In this small experiment, Nova Lite had lower latency for two of the three workloads, while Nova Micro had slightly lower latency for the architecture workload. Because only a few requests were executed, these measurements are not sufficient to establish general latency characteristics.

The models also differed substantially in output length. For the technical prompt, Nova Micro generated 570 output tokens while Nova Lite generated 389. For the architecture task, Nova Micro generated 268 output tokens while Nova Lite generated 211.

Both models produced useful responses for the tested text workloads, but Nova Lite was generally more concise in the more complex prompts.

### Cost

Inference cost depends on both the model's token pricing and the number of tokens consumed.

A model that generates fewer tokens is not necessarily the least expensive model because different models may have different per-token prices.

Therefore, an AI platform should capture both token consumption and model identity for every request.

### Model Routing

Model selection should not be based on a single characteristic such as latency.

A future routing decision may consider:

- Input modality
- Model capability
- Latency requirements
- Cost
- Request complexity
- Context size
- Availability
- Quality requirements

For example, a text-only request may be eligible for Nova Micro, while an image-based request requires a model that supports image input such as Nova Lite.

### Platform Engineering Takeaway

An AI gateway should separate applications from specific model providers and model IDs.

Applications should express what they need, while the platform can eventually determine which model satisfies those requirements based on capability, performance, reliability, and cost.

The Day 4 comparison provides the first data needed to build that model-routing layer.

## Day 5 — Reusable LLM Client

### Objective

Create a small application-facing LLM client that hides provider-specific implementation details and exposes a consistent response contract.

### Public Client API

Applications can invoke a model using a logical model name:

```python
client = LLMClient(
    model="nova-micro"
)

result = client.invoke(
    "Explain what an AI platform is in three sentences."
)
```

Applications do not need to know the underlying Amazon Bedrock model identifier or Bedrock response format.

### Model Registry

Logical model names are mapped to provider-specific configuration through a model registry.

For example:

```text
nova-micro
    ↓
Amazon Bedrock
    ↓
amazon.nova-micro-v1:0
```

This creates a boundary between application code and provider-specific configuration.

### Normalized Response

The public client returns a structured `LLMResponse` containing:

- Request ID
- Provider request ID
- Timestamp
- Logical model name
- Status
- Generated response
- Latency
- Token usage
- Stop reason
- Error information

Token usage is represented separately through a `TokenUsage` structure.

This gives applications a predictable contract instead of requiring them to parse provider-specific response objects.

### Model Switching

The same application code was successfully tested with:

- `nova-micro`
- `nova-lite`

Only the logical model name changed.

The application did not need changes to its Bedrock request construction, response parsing, authentication, or telemetry handling.

### Local Validation

An unsupported logical model such as:

```text
gpt-super-ultra
```

is rejected by the client before a request reaches Amazon Bedrock.

This allows the platform layer to validate supported models independently of the underlying provider.

### Platform Engineering Takeaway

Applications should depend on a stable platform contract rather than directly depending on provider APIs and model identifiers.

A platform abstraction allows provider-specific implementation details to change while minimizing changes required in application code.

This client is intentionally small, but it establishes the boundary that can later evolve into provider abstraction, model routing, centralized policy enforcement, observability, and an AI Gateway.