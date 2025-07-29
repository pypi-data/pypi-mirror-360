from typing import Annotated
from pydantic import Field, BeforeValidator
from .base import CommandType, BaseCommand


class StartRecording(BaseCommand):
    type: Annotated[CommandType, BeforeValidator(lambda _: CommandType.START_RECORDING)] = (
        Field(init=False, default=CommandType.START_RECORDING, frozen=True)
    )