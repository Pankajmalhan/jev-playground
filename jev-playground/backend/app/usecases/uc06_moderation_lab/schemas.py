from pydantic import BaseModel, Field


class TryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
