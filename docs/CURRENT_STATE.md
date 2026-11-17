# AI Platform Engineering Lab — Current State

**Last reviewed:** November 16, 2026
**Repository:** `rushiRK/ai-platform-engineering-lab`
**Active branch:** `feat/03-tool-calling`
**Implementation checkpoint:** `0a6f4fd` (following `4db3966`)
**Current module:** Day 7 — `03-tool-calling/`
**Status:** Planned implementation and tests complete; guided explanation reviewed. Independent explanation of request correlation and delegated authorization needs reinforcement. Documentation/branch integration remain to be finalized.
**Next implementation milestone:** P0 Inference API and Model Gateway; begin with a Bedrock-backed FastAPI inference endpoint. Next directory name is not yet established.

## Goals and working approach

- Target interview readiness in January–February 2027 for AI Platform / AI Infrastructure roles, with adjacent ML Platform and MLOps coverage.
- Build on backend/distributed systems and AWS experience; do not assume advanced GenAI proficiency.
- Follow Learn → Implement → Test → Explain → Interview and existing P0/P1/P2 priorities.
- Provide small, complete code increments with directory, environment, Git, execution, and testing instructions. Do not give the entire module at once or leave implementation details unexplained.
- GitHub is the implementation source of truth; inspect current files before suggesting changes.
- Protect family time around the December birth and possible January parental leave.

## Day 7 — Completed implementation

- Read-only `get_service_status` tool backed by sample data, with unknown-service errors.
- Strict Pydantic argument validation rejecting missing, non-string, empty, and extra fields; generated JSON Schema used in Converse tool configuration.
- Live Nova Micro tool request and successful two-call round trip demonstrated by user terminal output.
- Tool allowlist and application-supplied service permissions checked before execution.
- Full assistant message preserved; matching `toolUseId` returned in a user-role `toolResult` message.
- Expected tool failures mapped to INVALID_ARGUMENTS, ACCESS_DENIED, TOOL_EXECUTION_FAILED, and TOOL_TIMEOUT without exposing raw exception messages.
- Exactly one requested tool and one execution round allowed; a subsequent tool request stops the workflow.
- Bedrock client created inside the function; connect/read timeouts configured to 5/60 seconds, with one total SDK attempt and no application retry loop.
- CLI reports service, SDK, and workflow failures to stderr and returns exit code 1. Successful conversation completion returns 0, including a conversation that contains a tool-error result.

## Validation evidence

- User supplied full discovery output: eight tests passed, ending in OK.
- Tests cover authorized execution, rejection without execution, unknown service, reported tool timeout without retry, conversation history and ID matching, second tool-request rejection, second Bedrock-call timeout without repeated execution, and CLI timeout failure reporting.
- Assistant fetched the published feature branch and reviewed main.py and tool_executor.py at `0a6f4fd`; push of these code changes is confirmed. No merge into main is established.
- Eight-test results and live AWS results are user-provided evidence; assistant has not independently rerun this Day 7 suite or made live AWS requests.

## Explanation/interview checkpoint

- User described application execution and correctly identified permission denial and its error mapping.
- Clarified that the model generates the tool request; the application validates, authorizes, and executes it.
- Clarified that assistant history provides request context and toolUseId correlates one result with one invocation; it is not a persistent-session identifier or efficiency mechanism.
- Explained tool calling versus MCP: MCP changes discovery/invocation integration, while model orchestration and policy enforcement remain necessary.
- Corrected the assumption that authorization can simply move to the MCP server. An application's broad service identity must not let an end user exceed their own permissions; server enforcement is an additional boundary.
- Independent understanding of correlation and delegated authorization is not yet demonstrated after correction. Revisit briefly during gateway/MCP work rather than restart Day 7.

## Known limitations and deferred work

- Sample statuses are not live health checks; permissions are hardcoded, not derived from authenticated identity.
- No MCP server/client or agent framework is implemented in this module.
- Tool timeout handling translates a raised TimeoutError; it does not impose a deadline, cancel work, or isolate execution.
- SDK socket timeouts are not a workflow deadline; mocked tests do not verify SDK timing/retry enforcement.
- Malformed response envelopes can still cause unhandled KeyError/TypeError. Final answer content is not fully validated.
- First-call end_turn is rejected by this purpose-specific exercise; a general gateway must support normal answers without tool use.
- ValueError is a coarse classification for current lookup failures; remote tools will need explicit error translation.
- CLI prints raw lab responses; production logging needs redaction and an explicit sensitive-data policy.
- No production metrics, durable audit trail, idempotency mechanism, or multi-round runtime is claimed.

## Environment notes

- User's active interpreter was in `01-bedrock-basics/.venv`, even while running Module 03; directory changes do not change the active environment.
- Missing Pydantic was resolved in that interpreter. Confirm module dependency declarations before setting up a fresh environment.
- Default AWS credentials failed STS validation. Guidance used `ai-platform-dev` and explicit AWS_PROFILE selection; later live Bedrock inference succeeded. Do not store credentials in the repository.

## Next concrete tasks

1. Commit this state update on the feature branch and push it; review/merge the branch before starting the next implementation branch.
2. Begin the P0 Inference API milestone: validated HTTP request/response contracts around Bedrock, useful errors, and basic latency/token telemetry.
3. Add routing, authentication, quotas, and later MCP/tool permissions incrementally according to the roadmap.
4. Reinforce correlation and end-user-versus-service authorization during those implementations.

## Day 6 — Prior checkpoint record

The following preserves the historical Day 6 record. Its validation and limitation notes refer to Module 02 at that time, not Module 03. The input-test cleanup was subsequently confirmed present during this conversation's initial repository review at `70b950b`.

## Completed since last update

- Reviewed repository implementation at commit `de1e87d`, including schema, native inference, CLI handling, and tests.
- Fixed the native inference function to use its argument instead of a global customer message.
- User demonstrated a live Bedrock Qwen response followed by successful Pydantic validation.
- Strict SupportTicket contract rejects extra fields, missing required fields, invalid priority values, and coerced boolean strings.
- Native path accepts only `end_turn` and requires exactly one nonempty text block.
- Distinct service, transport, generation, and response exceptions; service failures preserve code/request ID and chained cause.
- CLI catches these failures and validation errors, reports to stderr, and exits with code 1. Mocked timeout CLI behavior was verified in the session.
- Added reusable success, extraction, failure, schema, and input-forwarding tests.
- Fixed a stale input-test fixture missing stopReason, then converted its import-time assertions into a unittest method with scoped patches.
- Reviewed interview explanations covering native versus prompt-based
  structured output, application-side validation, and failure-specific recovery.
- Clarified a misconception: an allowed but incorrect category passes the
  current schema. Schema validity does not guarantee semantic correctness.
  Revisit this distinction during future exercises; mastery is not assumed.
## Validation evidence

- Assistant independently ran the nine-test native suite at `de1e87d`: all passed.
- Full discovery at that commit exposed the stale input fixture; subsequent fixes were guided in this session.
- Latest user-provided discovery output: 10 named tests, each `ok`, in 0.003 seconds. The pasted excerpt omits the final OK line; no failure is shown.
- Latest input-test cleanup has not been independently fetched/reviewed after the user's local run. Push status of that cleanup is not established.
- No live AWS requests were made by the assistant. Live inference evidence comes from the user's terminal output earlier in this session.

## Current blocker

- No blocker to beginning Module 03.
- Final input-test cleanup push status remains unverified.

## Architecture/implementation decisions

- Keep prompt-based JSON as a comparison demo and native schema-constrained generation as the hardened path.
- Continue application-side Pydantic validation; syntactic/schema validity does not establish classification accuracy.
- Reject incomplete generation before parsing. Single-text-block acceptance is a conservative classifier policy.
- Preserve structured error details and exception causes instead of silently returning a fallback ticket.
- No application retry loop added. SDK retries/timeouts are not explicitly configured or verified by mocked tests.
- Access denial calls for configuration/permission correction; a timeout leaves processing outcome uncertain; max_tokens calls for reviewing output budget rather than blindly repeating the same request. Never automatically bypass a guardrail rejection.

## Known limitations (deferred; not new Day 6 requirements)

- AWS client initializes at import; credential/setup errors are not normalized by the CLI handlers.
- Native response telemetry fields are assumed present; missing metadata/usage can still raise KeyError.
- Prompt-based main.py has not received the native path's reliability improvements.
- Mock tests do not verify live model/API compatibility, SDK retries, classification accuracy, or production security.
- CLI timeout behavior was tested interactively but is not yet a persistent test in the reviewed suite.
- CLI displays validated ticket content for the lab; production logging needs an explicit sensitive-data policy.
