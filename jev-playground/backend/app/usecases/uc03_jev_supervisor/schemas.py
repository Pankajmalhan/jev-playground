from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ResumeRequest(BaseModel):
    thread_id: str
    # a specialist, or "close" to end without a reply
    choice: str
