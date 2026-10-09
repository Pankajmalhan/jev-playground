from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    size: int = Field(default=200, ge=10, le=1000)
