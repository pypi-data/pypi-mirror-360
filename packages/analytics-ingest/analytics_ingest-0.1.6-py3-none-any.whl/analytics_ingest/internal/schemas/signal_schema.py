from typing import List, Optional

from pydantic import BaseModel


class SignalSchema(BaseModel):
    configurationId: int
    data: List[dict]
    messageId: int
    name: str
    paramId: Optional[str] = ""
    paramType: Optional[str] = ""
    signalType: Optional[str] = ""
    unit: str

    @classmethod
    def from_variables(cls, config_id, message_id, batch, variables):
        return cls(
            configurationId=config_id,
            data=batch,
            messageId=message_id,
            name=variables["name"],
            paramId=variables.get("paramId", ""),
            paramType=variables.get("paramType", ""),
            signalType=variables.get("signalType", ""),
            unit=variables["unit"],
        )
