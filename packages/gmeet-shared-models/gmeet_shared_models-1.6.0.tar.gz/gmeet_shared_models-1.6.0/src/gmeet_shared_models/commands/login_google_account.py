from pydantic import Field, BeforeValidator
from typing import Annotated
from .base import CommandType, BaseCommand


class LoginGoogleAccount(BaseCommand):
    email: str = Field(
        examples=["user@example.com"],
        description="The email of the Google account, needs to check if value from env is correct",
    )
    type: Annotated[
        CommandType, BeforeValidator(lambda _: CommandType.LOGIN_GOOGLE_ACCOUNT)
    ] = Field(init=False, default=CommandType.LOGIN_GOOGLE_ACCOUNT, frozen=True)
