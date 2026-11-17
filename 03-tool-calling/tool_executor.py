from pydantic import ValidationError
from schemas import ServiceStatusArgs
from tools import get_service_status

def execute_tool(tool_name: str, tool_input: dict, allowed_services: set[str],) -> dict[str, str]:
    if tool_name != "get_service_status":
        raise PermissionError(f"Tool is not allowed: {tool_name}")
    arguments = ServiceStatusArgs.model_validate(tool_input)
    if arguments.service_name not in allowed_services:
        raise PermissionError("Caller is not authorized for this service")

    return get_service_status(arguments.service_name)

def build_tool_result(tool_request: dict, allowed_services: set[str],) -> dict:
    tool_use_id = tool_request["toolUseId"]
    tool_name = tool_request["name"]
    tool_input = tool_request["input"]

    try:
        payload = execute_tool(tool_name=tool_name, tool_input=tool_input, allowed_services=allowed_services)
        status = "success"
    except ValidationError:
        payload = {"error": "INVALID_ARGUMENTS"}
        status = "error"

    except PermissionError:
        payload = {"error": "ACCESS_DENIED"}
        status = "error"

    except ValueError:
        payload = {"error": "TOOL_EXECUTION_FAILED"}
        status = "error"
    
    except TimeoutError:
        payload = {"error": "TOOL_TIMEOUT"}
        status = "error"

    return{
        "toolUseId": tool_use_id,
        "content": [{"json": payload}],
        "status": status,
    }