from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1500)
    # Turn the code rule off to see what Jev catches on its own.
    hard_rule: bool = True


class StressRequest(BaseModel):
    runs: int = Field(default=3, ge=1, le=5)
    hard_rule: bool = True
