from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    # True: plain code looks the order up first and hands it to Jev and the
    # language model. The agent always has to fetch it itself.
    with_order: bool = False
