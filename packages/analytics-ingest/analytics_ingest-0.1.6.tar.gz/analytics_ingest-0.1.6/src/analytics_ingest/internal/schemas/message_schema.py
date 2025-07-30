from pydantic import BaseModel


class MessageSchema(BaseModel):
    name: str
    networkName: str = ""
    ecuName: str
    arbId: str = ""
    ecuId: str
    fileId: str = ""
    messageDate: str = ""
    requestCode: str = ""

    @classmethod
    def from_variables(cls, variables: dict) -> "MessageSchema":
        return cls(
            name=variables["messageName"],
            networkName=variables.get("networkName", ""),
            ecuName=variables["ecuName"],
            arbId=variables.get("arbId", ""),
            ecuId=variables["ecuId"],
            fileId=variables.get("fileId", ""),
            messageDate=variables.get("messageDate", ""),
            requestCode=variables.get("requestCode", ""),
        )

    def cache_key(self) -> str:
        return f"{self.name}|{self.networkName}|{self.ecuName}|{self.arbId}"
