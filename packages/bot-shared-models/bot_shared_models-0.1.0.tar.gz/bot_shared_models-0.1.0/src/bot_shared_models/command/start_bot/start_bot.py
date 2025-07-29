from typing import Annotated
from pydantic import Field, BeforeValidator
from ..base import CommandType, BaseCommand
from .parameters import GmeetBotParameters


class StartBot(BaseCommand):
    type: Annotated[CommandType, BeforeValidator(lambda _: CommandType.START_BOT)] = (
        Field(init=False, default=CommandType.START_BOT, frozen=True)
    )
    
    bot_parameters: GmeetBotParameters = Field(
        description="Parameters for starting the bot, such as meeting ID."
    )