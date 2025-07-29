from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class BotState(Enum):
    def __new__(cls, label: str):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__), label
        return obj

    INITIALIZING = "init"
    READY = "ready"

    LOGGED_GOOGLE = "logged_google"
    WAITING_INVITATION_CONFIRMATION = "waiting_invitation_confirmation"
    CONNECTED_MEET = "connected_meet"

    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"
    RECORDING_PUBLISHED = "recording_published"

    DEAD = "dead"

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def label(self) -> str:
        return self.value[1]

    def __str__(self):
        return self.label

    @classmethod
    def from_code(cls, code: int) -> "BotState":
        for state in cls:
            if state.code == code:
                return state
        raise ValueError(f"Invalid status code: {code}")


class StateMessage(BaseModel):
    state: BotState = Field(..., description="The current state of the bot")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="The timestamp when the state was updated",
    )
