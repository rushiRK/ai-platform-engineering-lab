import json

from pydantic import ValidationError

from schemas import SupportTicket


def parse_and_validate(raw_text: str) -> SupportTicket:
    parsed_json = json.loads(raw_text)

    return SupportTicket.model_validate(
        parsed_json
    )


def run_test(name: str, raw_text: str):
    print("\n" + "=" * 70)
    print(f"TEST: {name}")
    print("=" * 70)

    print("\nINPUT:")
    print(raw_text)

    try:
        ticket = parse_and_validate(raw_text)

        print("\nRESULT: SUCCESS")
        print(
            ticket.model_dump_json(
                indent=2
            )
        )

    except json.JSONDecodeError as error:
        print("\nRESULT: JSON PARSING FAILED")
        print(error)

    except ValidationError as error:
        print("\nRESULT: SCHEMA VALIDATION FAILED")
        print(error)


if __name__ == "__main__":

    valid_ticket = """
    {
        "category": "technical",
        "priority": "high",
        "summary": "Production API is returning HTTP 500 errors.",
        "requires_human": true
    }
    """

    malformed_json = """
    {
        "category": "technical",
        "priority": "high",
        "summary": "Production API is returning HTTP 500 errors.",
        "requires_human": true,
    }
    """

    invalid_schema = """
    {
        "category": "technical",
        "priority": "critical",
        "summary": "Production API is returning HTTP 500 errors.",
        "requires_human": true
    }
    """
    missing_field = """
    {
        "category": "technical",
        "priority": "high",
        "summary": "Production API is returning HTTP 500 errors."
    }
    """
    extra_field = """
    {
        "category": "technical",
        "priority": "high",
        "summary": "Production API is returning HTTP 500 errors.",
        "requires_human": true,
        "confidence": 0.99
    }
    """
    wrong_type = """
    {
    "category": "technical",
    "priority": "high",
    "summary": "Production API is returning HTTP 500 errors.",
    "requires_human": "yes"
    }
    """

    run_test(
        "Valid JSON + Valid Schema",
        valid_ticket,
    )

    run_test(
        "Malformed JSON",
        malformed_json,
    )

    run_test(
        "Valid JSON + Invalid Schema",
        invalid_schema,
    )
    run_test(
        "Missing Required Field",
        missing_field,
    )
    run_test(
        "Unexpected Extra Field",
        extra_field,
    )

    run_test(
        "Wrong Field Type",
        wrong_type,
    )