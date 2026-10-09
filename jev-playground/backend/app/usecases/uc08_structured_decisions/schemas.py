from pydantic import BaseModel, Field


class DecideRequest(BaseModel):
    expense: dict
    policy: str = Field(min_length=1, max_length=4000)
    calculate: bool = True   # let plain code work out per-person and per-night amounts first


class BatchRequest(BaseModel):
    policy: str = Field(min_length=1, max_length=4000)
    calculate: bool = True
