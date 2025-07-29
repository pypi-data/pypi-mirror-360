from typing import List, Optional

from pydantic import BaseModel, Field

from .query import InlineQuery, ChosenInlineResult, CallbackQuery, ShippingAddress, PreCheckoutQuery, Poll, PollAnswer, \
    User


class ChatPhoto(BaseModel):
    small_file_id: Optional[int] = Field(default=None)
    big_file_id: Optional[int] = Field(default=None)


class Chat(BaseModel):
    id: Optional[int] = Field(default=None)
    type: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    photo: Optional[ChatPhoto] = Field(default=None)


class MessageEntity(BaseModel):
    type: Optional[str] = Field(default=None)
    offset: Optional[int] = Field(default=None)
    length: Optional[int] = Field(default=None)
    url: Optional[str] = Field(default=None)
    user: Optional[User] = Field(default=None)


class Message(BaseModel):
    message_id: Optional[int] = Field(default=None)
    from_user: Optional[User] = Field(default=None, alias="from")
    date: Optional[int] = Field(default=None)
    chat: Optional[Chat] = Field(default=None)
    forward_from: Optional[User] = Field(default=None)
    forward_from_chat: Optional[Chat] = Field(default=None)
    forward_from_message_id: Optional[int] = Field(default=None)
    forward_date: Optional[int] = Field(default=None)
    reply_to_message: Optional[int] = Field(default=None)
    edit_date: Optional[int] = Field(default=None)
    text: Optional[str] = Field(default=None)
    entities: Optional[List[MessageEntity]] = Field(default=None)
    caption_entities: Optional[List[MessageEntity]] = Field(default=None)


class Updates(BaseModel):
    update_id: int
    message: Optional[Message] = Field(default=None)
    edited_message: Optional[Message] = Field(default=None)
    channel_post: Optional[Message] = Field(default=None)
    edited_channel_post: Optional[Message] = Field(default=None)
    inline_query: Optional[InlineQuery] = Field(default=None)
    chosen_inline_result: Optional[ChosenInlineResult] = Field(default=None)
    callback_query: Optional[CallbackQuery] = Field(default=None)
    shipping_query: Optional[ShippingAddress] = Field(default=None)
    pre_checkout_query: Optional[PreCheckoutQuery] = Field(default=None)
    poll: Optional[Poll] = Field(default=None)
    poll_answer: Optional[PollAnswer] = Field(default=None)
