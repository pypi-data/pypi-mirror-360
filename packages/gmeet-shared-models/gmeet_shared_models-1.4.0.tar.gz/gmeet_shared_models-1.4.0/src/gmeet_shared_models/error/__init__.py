from enum import StrEnum
from pydantic import BaseModel, Field


class ExceptionType(StrEnum):
    UNKNOWN = "unknown"
    BOT_IS_NOT_READY = "bot_is_not_ready"
    UNKNOWN_MESSAGE = "unknown_message"

    # Google login errors
    EMAIL_FROM_ENV_AND_FROM_MESSAGE_DOES_NOT_MATCH = (
        "email_from_env_and_from_message_does_not_match"
    )
    ## Elements not found
    EMAIL_FIELD_NOT_FOUND = "email_field_not_found"
    NEXT_BUTTON_NOT_FOUND = "next_button_not_found"
    PASSWORD_FIELD_NOT_FOUND = "password_field_not_found"
    SUBMIT_BUTTON_NOT_FOUND = "submit_button_not_found"
    LOGIN_FAILED = "login_failed"

    # Join meet errors
    CANNOT_LOAD_MEET_PAGE = "cannot_load_meet_page"
    JOIN_BUTTON_NOT_FOUND = "join_button_not_found"
    JOIN_TIMEOUT = "join_timeout"
    FAILED_JOIN_MEET = "failed_join_meet"

    # Start recording error
    BOT_IS_NOT_CONNECTED_MEET = "bot_is_not_connected_meet"
    RECORDING_ALREADY_STARTED = "recording_already_started"

    # Stop recording errors
    RECORDING_NOT_STARTED = "recording_not_started"

    # Publish recording errors
    RECORDING_NOT_FOUND = "recording_not_found"

    # Leave meet errors
    BOT_IS_NOT_IN_MEET = "bot_is_not_in_meet"


class ErrorMessage(BaseModel):
    exception_type: ExceptionType = Field(
        ...,
        description="Type of the exception that occurred",
    )
    message: str | None = Field(
        default=None,
        description="Detailed message describing the error",
    )
