from pydantic import BaseModel

from salute.common.models.message.payload import Payload


class Suggestion(BaseModel):
    buttons: list[dict] = []


class ResponsePayload(Payload):
    pronounceText: str = ""
    items: list = []
    suggestions: Suggestion = Suggestion()
    auto_listening: bool = False
