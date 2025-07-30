import sys

from loguru import logger

from . import LogLevelEnum


def logger_init(log_level: LogLevelEnum) -> None:
    logger.remove()
    extra = {"request_id": "SYSTEM_LOG"}
    format_ = "{time:DD-MM-YYYY HH:mm:ss} | <level>{level: <8}</level> | {extra[request_id]}"
    format_ = f"{format_} | <level>{{message}}</level>"
    logger.add(sys.stdout, colorize=True, format=format_, level=log_level)
    logger.configure(extra=extra)


def log_llm_error(
    text: str | None = None,
    vector: list[float] | None = None,
    model: str = "gigachat",
) -> None:
    if text is not None and not text:
        logger.error(f"No response from {model}!!!")
        return None
    if vector is not None and all(not item for item in vector):
        logger.error(f"No response from {model} encoder!!!")
        return None
    return None
