import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from typing_extensions import Annotated

import ingenious.dependencies as igen_deps
import ingenious.utils.namespace_utils as ns_utils
from ingenious.dependencies import get_chat_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.models.http_error import HTTPError
from ingenious.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter()

import os
import sys

parent_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../../../..")
)
sys.path.append(parent_dir)


@router.post(
    "/chat",
    responses={
        400: {"model": HTTPError, "description": "Bad Request"},
        406: {"model": HTTPError, "description": "Not Acceptable"},
        413: {"model": HTTPError, "description": "Payload Too Large"},
    },
)
async def chat(
    chat_request: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_conditional_security)
    ],
) -> ChatResponse:
    try:
        ns_utils.print_namespace_modules(
            "ingenious.services.chat_services.multi_agent.conversation_flows"
        )
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")
        return await chat_service.get_chat_response(chat_request)
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
    except ContentFilterError as cfe:
        logger.exception(cfe)
        raise HTTPException(status_code=406, detail=ContentFilterError.DEFAULT_MESSAGE)
    except TokenLimitExceededError as tle:
        logger.exception(tle)
        raise HTTPException(
            status_code=413, detail=TokenLimitExceededError.DEFAULT_MESSAGE
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
