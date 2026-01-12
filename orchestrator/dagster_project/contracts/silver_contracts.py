from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ValidationError


class MeasurementRecord(BaseModel):
    location_id: int = Field(alias="locationId")
    city: Optional[str] = None
    country: Optional[str] = None

    parameter: str
    value: float
    unit: Optional[str] = None

    # OpenAQ costuma trazer datetime em string ISO
    datetime: datetime

    class Config:
        populate_by_name = True
