from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    strict: bool = True   # tell the model to say "I don't know" when the passages do not answer


class RunAllRequest(BaseModel):
    strict: bool = True
