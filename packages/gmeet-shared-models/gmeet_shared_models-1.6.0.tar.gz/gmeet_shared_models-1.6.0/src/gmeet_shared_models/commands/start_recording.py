from pydantic import Field, BeforeValidator
from typing import Annotated
from .base import CommandType, BaseCommand


class StartRecording(BaseCommand):
    recording_id: str = Field(description="The ID of the recording to start")
    type: Annotated[
        CommandType, BeforeValidator(lambda _: CommandType.START_RECORDING)
    ] = Field(init=False, default=CommandType.START_RECORDING, frozen=True)
