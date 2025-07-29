from enum import StrEnum


class CommandType(StrEnum):
    FIND_BOT = "find_bot"
    START_BOT = "start_bot"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
