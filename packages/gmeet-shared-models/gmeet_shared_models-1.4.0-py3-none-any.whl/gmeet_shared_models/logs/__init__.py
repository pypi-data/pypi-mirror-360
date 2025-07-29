from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogMessage(BaseModel):
    level: LogLevel
    message: str
    timestamp: datetime = Field(
        init=False,
        default_factory=datetime.now,
        description="The log message timestamp, defaults to the current time",
    )
