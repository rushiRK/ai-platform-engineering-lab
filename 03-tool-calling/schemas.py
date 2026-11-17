from pydantic import BaseModel, ConfigDict, Field

class ServiceStatusArgs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid",)

    service_name: str = Field(min_length=1, description="Name of the platform service to inspect.")