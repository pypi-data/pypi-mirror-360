from typing import Any, Dict, Optional

from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage
from pydantic import BaseModel


class ResponseWrapper(BaseModel):
    """
    A wrapper class for the autogen_agentchat.base.Response class
    that handles serialization and deserialization.
    """

    chat_message_content: str
    chat_message_source: str
    inner_messages: Optional[Any] = None

    @classmethod
    def from_response(cls, response: Response) -> "ResponseWrapper":
        """Create a ResponseWrapper from a Response object"""
        if response is None:
            return None

        return cls(
            chat_message_content=response.chat_message.content,
            chat_message_source=response.chat_message.source,
            inner_messages=response.inner_messages,
        )

    def to_response(self) -> Response:
        """Convert back to a Response object"""
        return Response(
            chat_message=TextMessage(
                content=self.chat_message_content, source=self.chat_message_source
            ),
            inner_messages=self.inner_messages,
        )


class AgentChatWrapper(BaseModel):
    """
    A wrapper class for the AgentChat model that handles
    serialization and deserialization of Response objects.
    """

    chat_name: str
    target_agent_name: str
    source_agent_name: str
    user_message: str
    system_prompt: str
    identifier: Optional[str] = None
    chat_response_wrapper: Optional[ResponseWrapper] = None
    completion_tokens: int = 0
    prompt_tokens: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentChatWrapper":
        """Create an AgentChatWrapper from a dictionary"""
        # Make a copy of the data to avoid modifying the original
        data_copy = data.copy()

        # Extract and wrap the chat_response if it exists
        if "chat_response" in data_copy and data_copy["chat_response"] is not None:
            chat_response = data_copy.pop("chat_response")
            # We need to create a ResponseWrapper from the chat_response data
            # This requires special handling for the TextMessage inside
            try:
                chat_message = chat_response.get("chat_message", {})
                chat_message_content = chat_message.get("content", "")
                chat_message_source = chat_message.get("source", "")
                inner_messages = chat_response.get("inner_messages")

                data_copy["chat_response_wrapper"] = ResponseWrapper(
                    chat_message_content=chat_message_content,
                    chat_message_source=chat_message_source,
                    inner_messages=inner_messages,
                )
            except Exception as e:
                # If anything goes wrong, set to None
                data_copy["chat_response_wrapper"] = None
                print(f"Error wrapping chat_response: {e}")
                print(f"Chat response data: {chat_response}")

        # Handle missing required fields with defaults
        data_copy.setdefault("chat_name", "Unknown")
        data_copy.setdefault("target_agent_name", "Unknown")
        data_copy.setdefault("source_agent_name", "Unknown")
        data_copy.setdefault("user_message", "")
        data_copy.setdefault("system_prompt", "")
        data_copy.setdefault("completion_tokens", 0)
        data_copy.setdefault("prompt_tokens", 0)

        return cls(**data_copy)
