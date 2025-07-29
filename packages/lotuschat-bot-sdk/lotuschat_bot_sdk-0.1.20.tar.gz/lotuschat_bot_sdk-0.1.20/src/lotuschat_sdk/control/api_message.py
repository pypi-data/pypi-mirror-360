import json
import os

import aiohttp

from ..model.message import MessageEntity
from ..model.request import ParseModeType, BaseKeyboard, ChatAction


def message_action(cls):
    async def get_messages(self, offset: int, limit: int, timeout: int = None, allowed_updates: list[str] = None):
        url = f"{self._domain}{self._token}/getUpdates"
        payload = aiohttp.FormData()
        if offset < 0:
            offset = 0
        payload.add_field("offset", offset)
        if limit < 0:
            limit = 10
        payload.add_field("limit", limit)
        if timeout:
            if timeout < 0: timeout = 0
            payload.add_field("timeout", timeout)
        if allowed_updates:
            payload.add_field("allowed_updates", allowed_updates)
        return await self._request(url, payload)

    async def send_message(self, chat_id: int, text: str,
                           parse_mode: ParseModeType = None,
                           reply_to_message_id: int = None,
                           peer_id: int = None,
                           disable_web_page_preview: bool = None,
                           disable_notification: bool = None,
                           reply_markup: BaseKeyboard = None,
                           entities: list[MessageEntity] = None):
        url = f"{self._domain}{self._token}/sendMessage"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        payload.add_field("text", text)
        if parse_mode:
            payload.add_field("parse_mode", parse_mode.value)
        if reply_to_message_id:
            payload.add_field("reply_to_message_id", reply_to_message_id)
        if peer_id:
            payload.add_field("peer_id", peer_id)
        if disable_web_page_preview:
            payload.add_field("disable_web_page_preview", disable_web_page_preview)
        if disable_notification:
            payload.add_field("disable_notification", disable_notification)
        if reply_markup and reply_markup is not BaseKeyboard:
            payload.add_field("reply_markup", reply_markup.model_dump())
        if entities:
            encoded_entities = json.dumps([entity.model_dump() for entity in entities], ensure_ascii=False)
            payload.add_field("entities", encoded_entities)
        return await self._request(url, payload)

    async def send_document(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                            disable_notification: bool = None):
        return await self._send_media("sendDocument", chat_id, file_path, caption, reply_id, disable_notification)

    async def send_photo(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        return await self._send_media("sendPhoto", chat_id, file_path, caption, reply_id, disable_notification)

    async def send_video(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        return await self._send_media("sendVideo", chat_id, file_path, caption, reply_id, disable_notification)

    async def send_audio(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        return await self._send_media("sendAudio", chat_id, file_path, caption, reply_id, disable_notification)

    async def send_voice(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        return await self._send_media("sendVoice", chat_id, file_path, caption, reply_id, disable_notification)

    async def send_animation(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                             disable_notification: bool = None):
        return await self._send_media("sendAnimation", chat_id, file_path, caption, reply_id, disable_notification)

    async def _send_media(self, path_name: str, chat_id: int, file_path: str, caption: str = None,
                          reply_id: int = None, disable_notification: bool = None):
        url = f"{self._domain}{self._token}/{path_name}"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", f"{chat_id}")
        payload.add_field("file", open(file_path, "rb"), filename=os.path.basename(file_path),
                          content_type="application/octet-stream")
        if caption:
            payload.add_field("caption", f"{caption}")
        if reply_id:
            payload.add_field("reply_to_message_id", f"{reply_id}")
        if reply_id:
            payload.add_field("disable_notification", f"{disable_notification}")
        return await self._request(url, payload)

    async def send_chat_action(self, chat_id: int, action: ChatAction):
        url = f"{self._domain}{self._token}/sendChatAction"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        payload.add_field("action", action.value)
        return await self._request(url, payload)

    async def edit_message(self, chat_id: int, message_id: int, text: str):
        url = f"{self._domain}{self._token}/editMessageText"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        payload.add_field("message_id", message_id)
        payload.add_field("text", text)
        return await self._request(url, payload)

    async def edit_message_media(self, chat_id: int, message_id: int, file_path: str):
        url = f"{self._domain}{self._token}/editMessageMedia"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", f"{chat_id}")
        payload.add_field("message_id", f"{message_id}")
        payload.add_field("media", open(file_path, "rb"), filename=os.path.basename(file_path),
                          content_type="application/octet-stream")
        return await self._request(url, payload)

    async def forward_message(self, chat_id: int, from_chat_id: int, message_id: int,
                              disable_notification: bool = None):
        url = f"{self._domain}{self._token}/forwardMessage"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        payload.add_field("from_chat_id", from_chat_id)
        payload.add_field("message_id", message_id)
        if disable_notification:
            payload.add_field("disable_notification", disable_notification)
        return await self._request(url, payload)

    async def delete_message(self, chat_id: int, message_id: int):
        url = f"{self._domain}{self._token}/deleteMessage"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        payload.add_field("message_id", message_id)
        return await self._request(url, payload)

    # Attach async methods to the class
    cls.get_messages = get_messages
    cls.send_message = send_message
    cls.send_document = send_document
    cls.send_photo = send_photo
    cls.send_video = send_video
    cls.send_audio = send_audio
    cls.send_voice = send_voice
    cls._send_media = _send_media
    cls.send_animation = send_animation
    cls.send_chat_action = send_chat_action
    cls.edit_message = edit_message
    cls.edit_message_media = edit_message_media
    cls.forward_message = forward_message
    cls.delete_message = delete_message
    return cls
