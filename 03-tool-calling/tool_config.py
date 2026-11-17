from schemas import ServiceStatusArgs

def build_tool_config() -> dict:
    return {
        "tools":[
            {
                "toolSpec": {
                    "name": "get_service_status",
                    "description": (
                        "Look up the sample health status of a platform "
                        "service. Known services are inference-gateway "
                        "and model-router. This tool is read-only."
                    ),
                    "inputSchema":{
                        "json": ServiceStatusArgs.model_json_schema(),
                    },
                }
            }
        ]
    }
