from typing import Annotated
from pydantic import Field, BeforeValidator
from .base import CommandType, BaseCommand
from uuid import UUID


class FindBot(BaseCommand):
    type: Annotated[CommandType, BeforeValidator(lambda _: CommandType.FIND_BOT)] = (
        Field(init=False, default=CommandType.FIND_BOT, frozen=True)
    )

class FindBotResponse(BaseCommand):
    type: Annotated[CommandType, BeforeValidator(lambda _: CommandType.FIND_BOT)] = (
        Field(init=False, default=CommandType.FIND_BOT, frozen=True)
    )
    bot_id: UUID = Field(
        description="The ID of the bot that was found.",
    )
