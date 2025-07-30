import logging
from abc import ABC, abstractmethod

from fastapi import APIRouter, FastAPI

from ingenious.dependencies import get_chat_history_repository
from ingenious.models.config import Config


class IApiRoutes(ABC):
    def __init__(self, config: Config, app: FastAPI):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.app = app
        # Note: security_service should be obtained via dependency injection in route handlers
        # self.security_service = get_security_service(HTTPBasicCredentials)
        self.chat_history_repository = get_chat_history_repository()

    @abstractmethod
    def add_custom_routes(self) -> APIRouter:
        """
        Adds custom routes to the FastAPI app instance. Always returns the router instance.
        """
        pass
