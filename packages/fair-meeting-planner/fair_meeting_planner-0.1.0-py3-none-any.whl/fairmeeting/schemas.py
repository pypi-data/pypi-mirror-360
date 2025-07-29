from pydantic import BaseModel, Field
from typing import List, Optional


class Participant(BaseModel):
    name: str
    tz: str
    work_start: str
    work_end: str
    weight: Optional[float] = 1.0


class Meeting(BaseModel):
    participants: List[Participant]
    duration_minutes: int = Field(..., gt=0)
    allowed_weekdays: List[str]
    horizon: int = Field(..., gt=0)
    min_gap_between_meetings: int = Field(..., ge=0)
