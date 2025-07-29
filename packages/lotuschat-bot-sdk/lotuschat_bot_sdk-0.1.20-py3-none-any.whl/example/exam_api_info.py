import asyncio

from exam_other_const import TOKEN_STICKER_DOWNLOAD_BOT, CHAT_ID_GROUP
from src.example.exam_other_const import CHAT_ID_SINGLE
from src.lotuschat_sdk.control.bot import ChatBot
from src.lotuschat_sdk.utility.logger import log_verbose

bot = ChatBot(
    name="Python Bot - Test command event",
    token=TOKEN_STICKER_DOWNLOAD_BOT,
    is_vpn=True
)


async def command():
    get_chat = bot.get_chat(chat_id=CHAT_ID_GROUP)
    get_administrators = bot.get_chat_administrators(chat_id=CHAT_ID_GROUP)
    get_member = bot.get_chat_member(chat_id=CHAT_ID_GROUP, user_id=CHAT_ID_SINGLE)
    get_member_count = bot.get_chat_member_count(chat_id=CHAT_ID_GROUP)

    results = await asyncio.gather(
        get_chat,
        get_administrators,
        get_member,
        get_member_count,
        return_exceptions=True
    )
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log_verbose(f"Task {i + 1} failed: {result}")
        else:
            log_verbose(f"Task {i + 1} success: {result}")


asyncio.run(command())
