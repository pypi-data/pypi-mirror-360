from pydantic import Field, BeforeValidator
from typing import Annotated
from .base import CommandType, BaseCommand


class LeaveMeet(BaseCommand):
    type: Annotated[CommandType, BeforeValidator(lambda _: CommandType.LEAVE_MEET)] = (
        Field(init=False, default=CommandType.LEAVE_MEET, frozen=True)
    )
