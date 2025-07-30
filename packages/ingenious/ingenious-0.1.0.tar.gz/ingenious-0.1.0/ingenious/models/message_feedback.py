from typing import Optional

from pydantic import BaseModel


class MessageFeedbackRequest(BaseModel):
    thread_id: str
    message_id: str
    user_id: Optional[str]
    positive_feedback: Optional[bool]


class MessageFeedbackResponse(BaseModel):
    message: str
