## Structured Output

### Objective

Learn how to convert free-form LLM responses into machine-consumable data with an explicit application contract.

### Schema

A `SupportTicket` Pydantic model defines the expected output:

- Category
- Priority
- Summary
- Whether human intervention is required

The Pydantic model can also generate a JSON Schema that describes this contract in a provider-independent format.

### Prompt-Based Structured Output

The first implementation generates JSON Schema from the Pydantic model and includes the schema directly in the model prompt.

The processing flow is:

```text
Customer Message
      ↓
Prompt + JSON Schema
      ↓
LLM
      ↓
Raw JSON Text
      ↓
JSON Parsing
      ↓
Pydantic Validation
      ↓
SupportTicket
```

This approach depends on the model following the prompt correctly.

### Validation

Several failure scenarios were tested locally.

#### Malformed JSON

A trailing comma caused JSON parsing to fail before schema validation occurred.

#### Invalid Enum

A priority value of `critical` was valid JSON but failed schema validation because only `low`, `medium`, and `high` are permitted.

#### Missing Required Field

Removing `requires_human` produced a validation error because the field is required by the schema.

#### Unexpected Field

Adding a `confidence` field failed validation because additional properties are forbidden.

#### Incorrect Type

Providing `"yes"` instead of a boolean for `requires_human` failed because strict type validation is enabled.

These experiments demonstrate that JSON syntax validation and application schema validation solve different problems.

### Native Bedrock Structured Output

A second implementation uses Bedrock's native structured-output capability.

Instead of embedding the JSON Schema in the natural-language prompt, the schema is supplied through the Bedrock API's structured-output configuration.

The flow becomes:

```text
Customer Message
      ↓
Bedrock Converse
      +
JSON Schema
      ↓
Schema-Constrained Generation
      ↓
Structured JSON
      ↓
Pydantic Validation
      ↓
SupportTicket
```

The generated result successfully matched the `SupportTicket` contract.

### Platform Engineering Takeaway

Structured output is a contract between an AI system and downstream software.

Applications should not blindly trust free-form model responses before taking programmatic actions.

A platform may need to support multiple strategies depending on model capabilities:

```text
Model supports native schema enforcement
        ↓
Use provider-native structured output

Model does not support native schema enforcement
        ↓
Prompt with schema
        +
Parse output
        +
Validate output
        +
Potential retry
```

The platform should continue validating responses against its own application schema even when the model provider offers native structured-output enforcement.