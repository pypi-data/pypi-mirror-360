import logging

from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from ingenious.dependencies import get_message_feedback_service
from ingenious.models.http_error import HTTPError
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)
from ingenious.services.message_feedback_service import MessageFeedbackService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.put(
    "/messages/{message_id}/feedback",
    responses={400: {"model": HTTPError, "description": "Bad Request"}},
)
async def submit_message_feedback(
    message_id: str,
    message_feedback_request: MessageFeedbackRequest,
    feedback_service: Annotated[
        MessageFeedbackService, Depends(get_message_feedback_service)
    ],
) -> MessageFeedbackResponse:
    try:
        return await feedback_service.update_message_feedback(
            message_id, message_feedback_request
        )
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
