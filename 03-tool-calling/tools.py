SERVICE_STATUSES = {
    "inference-gateway": "healthy",
    "model-router": "degraded",
}

def get_service_status(service_name: str) -> dict[str, str]:
    """Return the sample status of a known platform service."""

    if service_name not in SERVICE_STATUSES:
        raise ValueError(f"Unknown service: {service_name}")

    status = SERVICE_STATUSES[service_name]

    return {
        "service_name": service_name,
        "status": status
    }
