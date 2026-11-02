# AI Platform Engineering Lab — Current State

**Last reviewed:** November 1, 2026  
**Repository:** `rushiRK/ai-platform-engineering-lab`  
**Active milestone:** Day 6  
**Active module:** `02-structured-output/`  
**Status:** Implementation and planned tests complete for Day 6; explanation/interview checkpoint pending.

## What is known so far

- The September learning roadmap is being reorganized around the January–February 2027 interview target.
- The active learning topic is structured output using Amazon Bedrock, JSON, Pydantic validation, and error handling.
- Broader role targets: AI Platform Engineer, ML Platform Engineer, MLOps Engineer.
- Relevant strengths: backend services, distributed systems, AWS/platform engineering.
- Learning assumption: limited enterprise GenAI integration experience; do not equate exposure with proficiency.
- Important constraint: family priorities around a December 2026 birth and a *possible* 12-week parental leave starting January 4, 2027.

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

## Validation evidence

- Assistant independently ran the nine-test native suite at `de1e87d`: all passed.
- Full discovery at that commit exposed the stale input fixture; subsequent fixes were guided in this session.
- Latest user-provided discovery output: 10 named tests, each `ok`, in 0.003 seconds. The pasted excerpt omits the final OK line; no failure is shown.
- Latest input-test cleanup has not been independently fetched/reviewed after the user's local run. Push status of that cleanup is not established.
- No live AWS requests were made by the assistant. Live inference evidence comes from the user's terminal output earlier in this session.

## Current blocker

- No implementation failure shown in the latest local results.
- Explain/interview answers remain pending; do not infer mastery from passing tests.

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

## Next concrete task

Answer briefly in your own words:
1. How does native structured output differ from asking for JSON in a prompt?
2. Why retain Pydantic validation when native structured output is enabled?
3. Why should access denied, read timeout, and max_tokens have different recovery behavior?

Then commit the final input-test cleanup and this CURRENT_STATE.md to GitHub. After the explanation checkpoint, close Day 6 and scope the next tool-calling exercise before implementation. Do not restart Bedrock basics or add further hardening merely to delay progress.
