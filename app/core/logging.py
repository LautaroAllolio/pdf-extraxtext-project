import logging
import sys

from app.core.config import get_settings

_EXTERNAL_LOGGERS = ["uvicorn", "motor", "beanie"]


def configure_logging() -> None:
    settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    for logger_name in _EXTERNAL_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)