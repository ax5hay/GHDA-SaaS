"""Python logging configuration using loguru."""

import os
import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level=os.getenv("LOG_LEVEL", "INFO"),
    colorize=True,
)
