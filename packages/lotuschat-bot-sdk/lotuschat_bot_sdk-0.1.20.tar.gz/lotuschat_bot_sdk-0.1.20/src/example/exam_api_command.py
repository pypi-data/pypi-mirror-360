import asyncio

from exam_other_const import TOKEN_STICKER_DOWNLOAD_BOT, CHAT_ID_GROUP
from src.lotuschat_sdk.control.bot import ChatBot
from src.lotuschat_sdk.model.request import Command
from src.lotuschat_sdk.utility.logger import log_verbose

bot = ChatBot(
    name="Python Bot - Test command event",
    token=TOKEN_STICKER_DOWNLOAD_BOT,
    is_vpn=True
)


async def command():
    set_command = bot.set_command(
        commands=[
            Command(command="mute", description="Im lang"),
            Command(command="unmute", description="Bo im lang")
        ]
    )
    get_command = bot.get_command()
    delete_command = bot.delete_command(
        commands=[
            Command(command="mute", description="Im lang"),
        ]
    )

    results = await asyncio.gather(
        set_command,
        get_command,
        delete_command,
        return_exceptions=True
    )
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log_verbose(f"Task {i + 1} failed: {result}")
        else:
            log_verbose(f"Task {i + 1} success: {result}")


asyncio.run(command())
