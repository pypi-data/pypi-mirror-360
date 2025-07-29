from typing import Annotated
from pydantic import Field, BeforeValidator
from .base import CommandType, BaseCommand


class JoinMeet(BaseCommand):
    meeting_id: str = Field(
        ..., examples=["abc-defg-hij"], description="The ID of the meeting to join"
    )
    type: Annotated[CommandType, BeforeValidator(lambda _: CommandType.JOIN_MEET)] = (
        Field(init=False, default=CommandType.JOIN_MEET, frozen=True)
    )
