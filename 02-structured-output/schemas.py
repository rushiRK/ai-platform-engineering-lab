from typing import Literal

from pydantic import BaseModel, ConfigDict

class SupportTicket(BaseModel):
    model_config = ConfigDict(extra="forbid", strict = True,)

    category : Literal["billing", "technical", "account", "other"]

    priority: Literal["low", "medium", "high"]

    summary: str
    requires_human: bool