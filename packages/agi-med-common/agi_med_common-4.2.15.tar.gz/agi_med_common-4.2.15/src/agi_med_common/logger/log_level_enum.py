from enum import StrEnum, auto


class LogLevelEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        return name.upper()

    TRACE = auto()  # logger.trace()
    DEBUG = auto()  # logger.debug()
    INFO = auto()  # logger.info()
    SUCCESS = auto()  # logger.success()
    WARNING = auto()  # logger.warning()
    ERROR = auto()  # logger.error()
    CRITICAL = auto()  # logger.critical()
