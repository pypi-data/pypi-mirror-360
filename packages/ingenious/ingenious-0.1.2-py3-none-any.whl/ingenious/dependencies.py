import logging
import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status

# Load environment variables from .env file
load_dotenv()
# Import mock service for testing
import sys
from typing import Optional

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

import ingenious.config.config as Config
from ingenious.db.chat_history_repository import (
    ChatHistoryRepository,
    DatabaseClientType,
)
from ingenious.external_services.openai_service import OpenAIService
from ingenious.files.files_repository import FileStorage
from ingenious.services.chat_service import ChatService
from ingenious.services.message_feedback_service import MessageFeedbackService

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

logger = logging.getLogger(__name__)
security = HTTPBasic()


def get_config():
    """Get config dynamically to ensure environment variables are loaded"""
    return Config.get_config()


def get_profile():
    """Get profile dynamically to ensure environment variables are loaded"""
    import ingenious.config.profile as Profile

    return Profile.Profiles(os.getenv("INGENIOUS_PROFILE_PATH", ""))


def get_openai_service():
    config = get_config()
    model = config.models[0]
    return OpenAIService(
        azure_endpoint=str(model.base_url),
        api_key=str(model.api_key),
        api_version=str(model.api_version),
        open_ai_model=str(model.model),
    )


def get_chat_history_repository():
    config = get_config()
    db_type_val = config.chat_history.database_type.lower()
    try:
        db_type = DatabaseClientType(db_type_val)

    except ValueError:
        raise ValueError(f"Unknown database type: {db_type_val}")

    chr = ChatHistoryRepository(db_type=db_type, config=config)

    return chr


def get_security_service(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)] = None,
):
    config = get_config()
    if not config.web_configuration.authentication.enable:
        # Authentication is disabled, allow access without checking credentials
        logger.warning(
            "Authentication is disabled. This is not recommended for production use."
        )
        return "anonymous"  # Return something that indicates no auth

    # Authentication is enabled, validate credentials
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = config.web_configuration.authentication.username.encode(
        "utf-8"
    )
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = config.web_configuration.authentication.password.encode(
        "utf-8"
    )
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def get_security_service_optional(
    credentials: Optional[HTTPBasicCredentials] = None,
):
    """Optional security service that doesn't require credentials when auth is disabled"""
    config = get_config()
    if not config.web_configuration.authentication.enable:
        # Authentication is disabled, don't require credentials
        logger.warning(
            "Authentication is disabled. This is not recommended for production use."
        )
        return None

    # Authentication is enabled, require credentials
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = config.web_configuration.authentication.username.encode(
        "utf-8"
    )
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = config.web_configuration.authentication.password.encode(
        "utf-8"
    )
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def get_chat_service(
    chat_history_repository: Annotated[
        ChatHistoryRepository, Depends(get_chat_history_repository)
    ],
    conversation_flow: str = "",
):
    config = get_config()
    cs_type = config.chat_service.type
    return ChatService(
        chat_service_type=cs_type,
        chat_history_repository=chat_history_repository,
        conversation_flow=conversation_flow,
        config=config,
    )


def get_message_feedback_service(
    chat_history_repository: Annotated[
        ChatHistoryRepository, Depends(get_chat_history_repository)
    ],
):
    return MessageFeedbackService(chat_history_repository)


def sync_templates():
    config = get_config()
    if config.file_storage.storage_type == "local":
        return
    else:
        fs = FileStorage(config)
        working_dir = os.getcwd()
        template_path = os.path.join(working_dir, "ingenious", "templates")
        template_files = fs.list_files(file_path=template_path)
        for file in template_files:
            file_name = os.path.basename(file)
            file_contents = fs.read_file(file_name=file_name, file_path=template_path)
            file_path = os.path.join(working_dir, "ingenious", "templates", file_name)
            with open(file_path, "w") as f:
                f.write(file_contents)


def get_file_storage_data() -> FileStorage:
    config = get_config()
    return FileStorage(config, Category="data")


def get_file_storage_revisions() -> FileStorage:
    config = get_config()
    return FileStorage(config, Category="revisions")


def get_project_config():
    return get_config()


def get_auth_user(request: Request) -> str:
    """Get authenticated user - bypasses credentials check when auth is disabled"""
    config = get_config()

    if not config.web_configuration.authentication.enable:
        # Authentication is disabled, allow access
        logger.warning(
            "Authentication is disabled. This is not recommended for production use."
        )
        return "anonymous"

    # Authentication is enabled, extract and validate Basic Auth
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Basic "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    import base64

    try:
        credentials_str = base64.b64decode(auth_header[6:]).decode("utf-8")
        username, password = credentials_str.split(":", 1)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication format",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Validate credentials
    current_username_bytes = username.encode("utf8")
    correct_username_bytes = config.web_configuration.authentication.username.encode(
        "utf-8"
    )
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )

    current_password_bytes = password.encode("utf8")
    correct_password_bytes = config.web_configuration.authentication.password.encode(
        "utf-8"
    )
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return username


def get_conditional_security(request: Request) -> str:
    """Get authenticated user - wrapper around get_auth_user for compatibility"""
    return get_auth_user(request)
