from typing import Annotated
from pydantic import Field, BeforeValidator
from .base import CommandType, BaseCommand


class StopRecording(BaseCommand):
    type: Annotated[CommandType, BeforeValidator(lambda _: CommandType.STOP_RECORDING)] = (
        Field(init=False, default=CommandType.STOP_RECORDING, frozen=True)
    )