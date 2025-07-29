import asyncio

from exam_other_const import TOKEN_STICKER_DOWNLOAD_BOT, CHAT_ID_SINGLE, CHAT_ID_GROUP
from src.lotuschat_sdk.control.bot import ChatBot
from src.lotuschat_sdk.model.message import MessageEntity
from src.lotuschat_sdk.model.request import InlineKeyboardMarkup, KeyboardMarkup, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, \
    ForceReply, ParseModeType, ChatAction
from src.lotuschat_sdk.utility.logger import log_info
from src.lotuschat_sdk.utility.logger import log_verbose

bot = ChatBot(
    name="Python Bot - Test message event",
    token=TOKEN_STICKER_DOWNLOAD_BOT,
    is_vpn=True
)


async def message_get():
    log_info("get messages")
    get_default = bot.get_messages(
        offset=0, limit=10
    )
    get_timeout_30 = bot.get_messages(
        offset=0, limit=10, timeout=30
    )
    get_timeout_0 = bot.get_messages(
        offset=0, limit=10, timeout=0
    )
    get_allow_updates = bot.get_messages(
        offset=0, limit=10, allowed_updates=["message"]
    )

    results = await asyncio.gather(
        get_default,
        get_timeout_30, get_timeout_0,
        get_allow_updates,
        return_exceptions=True
    )
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log_verbose(f"Task {i + 1} failed: {result}")
        else:
            log_verbose(f"Task {i + 1} success: {result}")


async def message_send():
    log_info("send message to person")
    send_person_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person"
    )
    send_person_html_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="<b>python bot</b> send html message to <i>person</i>",
        parse_mode=ParseModeType.HTML
    )
    send_person_md_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="*python bot* send markdown message to _person_",
        parse_mode=ParseModeType.MARKDOWN
    )
    send_person_reply_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person with reply",
        reply_to_message_id=365
    )

    keyboard = [
        [
            KeyboardMarkup(text="Yes", callback_data="vote_yes"),
            KeyboardMarkup(text="No", callback_data="vote_no")
        ]
    ]
    send_inline_keyboard_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person with InlineKeyboardMarkup",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    send_reply_keyboard_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person with ReplyKeyboardMarkup",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    )

    send_reply_keyboard_clear_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person with clear ReplyKeyboardMarkup",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[]], resize_keyboard=True, one_time_keyboard=True)
    )
    send_reply_keyboard_remove_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person with ReplyKeyboardRemove",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True)
    )
    send_force_reply_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person with force_reply",
        reply_markup=ForceReply(force_reply=True)
    )

    entities = [
        MessageEntity(
            offset=17, length=7, type="bold"
        ),
        MessageEntity(
            offset=34, length=6, type="text_link", url="https://example.com"
        )
    ]
    send_entities_task = bot.send_message(
        chat_id=CHAT_ID_SINGLE,
        text="python bot send default message to person with entities",
        entities=entities
    )

    log_info("send message to group")
    send_group = bot.send_message(
        chat_id=CHAT_ID_GROUP,
        text="python bot send message to group"
    )
    send_group_reply = bot.send_message(
        chat_id=CHAT_ID_GROUP,
        text="python bot send message to group with reply",
        reply_to_message_id=365
    )

    results = await asyncio.gather(
        send_person_task, send_person_html_task, send_person_md_task, send_person_reply_task,
        send_inline_keyboard_task,
        send_reply_keyboard_task, send_reply_keyboard_clear_task, send_reply_keyboard_remove_task,
        send_entities_task, send_force_reply_task,
        send_group, send_group_reply,
        return_exceptions=True
    )
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log_verbose(f"Task {i + 1} failed: {result}")
        else:
            log_verbose(f"Task {i + 1} success: {result}")


async def message_send_file():
    dir_root = "/Users/yuriko/Work/Vccorp/PythonLotusChatBotSdk"
    send_document = bot.send_document(
        chat_id=CHAT_ID_GROUP,
        file_path=f"{dir_root}/assets/generateDB.zip",
        caption="caption with document"
    )
    send_photo = bot.send_photo(
        chat_id=CHAT_ID_GROUP,
        file_path=f"{dir_root}/assets/2B.webp",
        caption="caption with document"
    )

    results = await asyncio.gather(
        send_document,
        send_photo,
        return_exceptions=True
    )
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log_verbose(f"Task {i + 1} failed: {result}")
        else:
            log_verbose(f"Task {i + 1} success: {result}")


async def message_other():
    send_chat_action = bot.send_chat_action(chat_id=-2226446, action=ChatAction.CHOOSE_STICKER)
    # edit_message = bot.edit_message(
    #     chat_id=-2226446,
    #     message_id=409,
    #     text="change content 409"
    # )
    # edit_message_media = bot.edit_message_media(
    #     chat_id=-2226446,
    #     message_id=869,
    #     file_path="/Users/yuriko/Work/Vccorp/PythonLotusChatBotSdk/assets/generateDB.zip"
    # )
    # delete_group = bot.delete_message(
    #     chat_id=CHAT_ID_GROUP,
    #     message_id=142
    # )
    # forward_group = bot.forward_message(
    #     chat_id=CHAT_ID_GROUP,
    #     from_chat_id=-2890550,
    #     message_id=41
    # )

    results = await asyncio.gather(
        send_chat_action,
        # edit_message,
        # edit_message_media,
        # delete_group,
        # forward_group,
        return_exceptions=True
    )
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            log_verbose(f"Task {i + 1} failed: {result}")
        else:
            log_verbose(f"Task {i + 1} success: {result}")


# asyncio.run(message_get())
# asyncio.run(message_send())
# asyncio.run(message_send_file())
asyncio.run(message_other())
