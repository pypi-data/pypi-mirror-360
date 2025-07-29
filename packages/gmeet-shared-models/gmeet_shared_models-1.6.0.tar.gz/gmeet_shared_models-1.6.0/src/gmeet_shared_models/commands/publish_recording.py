from pydantic import Field, BeforeValidator
from typing import Annotated
from .base import CommandType, BaseCommand


class PublishRecording(BaseCommand):
    recording_id: str = Field(
        description="The ID of the recording to be published (passed in start_recording command)",
    )
    s3_key: str | None = Field(
        examples=["gmeet/recording.flac"],
        description="Final recording name to be published, if not provided, the name will be taken from the recording_id",
    )
    type: Annotated[
        CommandType, BeforeValidator(lambda _: CommandType.PUBLISH_RECORDING)
    ] = Field(init=False, default=CommandType.PUBLISH_RECORDING, frozen=True)
