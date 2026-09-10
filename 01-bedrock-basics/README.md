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