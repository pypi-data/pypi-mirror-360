from enum import StrEnum
from pydantic import BaseModel, Field
from datetime import datetime


class BotState(StrEnum):
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
        return list(self.__class__).index(self)

    @property
    def label(self) -> str:
        return self.value

    def __str__(self):
        return self.label

    @classmethod
    def from_code(cls, code: int) -> "BotState":
        try:
            return BotState(list(cls)[code])
        except IndexError:
            raise ValueError(f"Invalid status code: {code}")


class StateMessage(BaseModel):
    state: BotState = Field(..., description="The current state of the bot")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="The timestamp when the state was updated",
    )
