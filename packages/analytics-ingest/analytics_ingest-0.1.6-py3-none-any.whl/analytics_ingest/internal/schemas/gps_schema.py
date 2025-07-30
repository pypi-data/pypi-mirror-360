# analytics_ingest/src/analytics_ingest/internal/schemas/gps_schema.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AvailableSchema(BaseModel):
    accuracy: Optional[bool] = None
    altitude: Optional[bool] = None
    bearing: Optional[bool] = None
    latitude: Optional[bool] = None
    longitude: Optional[bool] = None
    speed: Optional[bool] = None
    time: Optional[bool] = None


class GPSSchema(BaseModel):
    time: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None
    available: Optional[AvailableSchema] = None

    @classmethod
    def from_variables(cls, variables: dict) -> list["GPSSchema"]:
        data = variables.get("data", [])
        if not data:
            raise ValueError("Missing required field: 'data'")
        return [cls(**item) for item in data]
