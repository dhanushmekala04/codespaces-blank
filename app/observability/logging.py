import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("patientcare")


def log_event(action: str, **metadata: Any) -> None:
    logger.info(action, extra=metadata)
