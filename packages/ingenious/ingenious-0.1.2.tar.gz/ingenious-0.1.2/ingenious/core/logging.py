import logging
import logging.handlers
import os
import sys

import colorlog


def setup_logging(app_module_name: str | None) -> None:
    root_log_level = os.environ.get("ROOTLOGLEVEL", "WARNING")
    log_level = os.environ.get("LOGLEVEL", "WARNING")

    # Create a stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(asctime)s - %(log_color)s[%(levelname)s]%(reset)s - %(name)s - %(message)s"
        )
    )

    # Handlers
    handlers = [stream_handler]

    # Root logger
    if root_log_level:
        root_logger = logging.getLogger()
        root_logger.setLevel(root_log_level)
        root_logger.handlers = handlers  # type: ignore

    # App logger
    logger = logging.getLogger(app_module_name)
    logger.setLevel(log_level)
    logger.handlers = handlers  # type: ignore

    # Get uvicorn access logger
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.setLevel(log_level)
    access_logger.handlers = handlers  # type: ignore

    # Get uvicorn error logger
    error_logger = logging.getLogger("uvicorn.error")
    error_logger.setLevel(log_level)
    error_logger.handlers = handlers  # type: ignore
