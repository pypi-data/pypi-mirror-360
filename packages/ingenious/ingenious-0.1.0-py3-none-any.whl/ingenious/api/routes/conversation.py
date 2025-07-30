import logging

from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.dependencies import get_chat_history_repository
from ingenious.models.http_error import HTTPError
from ingenious.models.message import Message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/conversations/{thread_id}",
    responses={400: {"model": HTTPError, "description": "Bad Request"}},
)
async def get_conversation(
    thread_id: str,
    chat_history_repository: Annotated[
        ChatHistoryRepository, Depends(get_chat_history_repository)
    ],
) -> list[Message]:
    try:
        messages = await chat_history_repository.get_thread_messages(thread_id)
        return messages
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
