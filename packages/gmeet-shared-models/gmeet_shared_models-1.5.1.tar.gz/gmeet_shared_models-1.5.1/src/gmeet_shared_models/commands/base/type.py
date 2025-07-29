from enum import StrEnum


class CommandType(StrEnum):
    LOGIN_GOOGLE_ACCOUNT = "login_google_account"
    JOIN_MEET = "join_meet"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
    PUBLISH_RECORDING = "publish_recording"
    LEAVE_MEET = "leave_meet"
