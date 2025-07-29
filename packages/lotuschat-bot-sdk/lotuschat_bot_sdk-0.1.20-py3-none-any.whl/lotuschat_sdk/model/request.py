from enum import Enum
from typing import List

from pydantic import BaseModel, Field


# ####################################################################################################
# key reply_markup - api send message
# ####################################################################################################
class BaseKeyboard(BaseModel): pass


class KeyboardMarkup(BaseModel):
    text: str
    callback_data: str


class InlineKeyboardMarkup(BaseKeyboard):
    inline_keyboard: List[List[KeyboardMarkup]] = Field(default=None)


class ReplyKeyboardMarkup(BaseKeyboard):
    keyboard: List[List[KeyboardMarkup]] = Field(default=None)
    resize_keyboard: bool = Field(default=None)
    one_time_keyboard: bool = Field(default=None)
    selective: bool = Field(default=None)


class ReplyKeyboardRemove(BaseKeyboard):
    remove_keyboard: bool = Field(default=None)
    selective: bool = Field(default=None)


class ForceReply(BaseKeyboard):
    force_reply: bool = Field(default=None)
    selective: bool = Field(default=None)


# ####################################################################################################
# other
# ####################################################################################################
class ParseModeType(Enum):
    MARKDOWN = "Markdown"
    HTML = "HTML"


class ChatAction(Enum):
    TYPING = "typing"
    UPLOAD_PHOTO = "upload_photo"
    RECORD_VIDEO = "record_video"
    UPLOAD_VIDEO = "upload_video"
    RECORD_VOICE = "record_voice"
    UPLOAD_VOICE = "upload_voice"
    UPLOAD_DOCUMENT = "upload_document"
    CHOOSE_STICKER = "choose_sticker"
    FIND_LOCATION = "find_location"
    RECORD_VIDEO_NOTE = "record_video_note"
    UPLOAD_VIDEO_NOTE = "upload_video_note"


class Command(BaseModel):
    command: str
    description: str
