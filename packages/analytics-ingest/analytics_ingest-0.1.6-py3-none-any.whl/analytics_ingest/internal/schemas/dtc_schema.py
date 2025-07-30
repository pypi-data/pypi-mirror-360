from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BytesInput(BaseModel):
    bytes: str


class DTCSchema(BaseModel):
    description: str
    dtcId: str
    extended: Optional[BytesInput] = None
    snapshot: Optional[BytesInput] = None
    status: str
    time: datetime

    @classmethod
    def from_variables(cls, variables: dict) -> list["DTCSchema"]:
        return [cls(**item) for item in variables.get("data", [])]
