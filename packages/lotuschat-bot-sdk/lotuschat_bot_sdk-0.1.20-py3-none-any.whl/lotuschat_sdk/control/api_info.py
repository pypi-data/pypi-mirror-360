import aiohttp


def info_action(cls):
    async def get_chat(self, chat_id: int):
        url = f"{self._domain}{self._token}/getChat"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        return await self._request(url, payload)

    async def get_chat_administrators(self, chat_id: int):
        url = f"{self._domain}{self._token}/getChatAdministrators"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        return await self._request(url, payload)

    async def get_chat_member(self, chat_id: int, user_id: int):
        url = f"{self._domain}{self._token}/getChatMember"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        payload.add_field("user_id", user_id)
        return await self._request(url, payload)

    async def get_chat_member_count(self, chat_id: int):
        url = f"{self._domain}{self._token}/getChatMemberCount"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        return await self._request(url, payload)

    async def leave_chat(self, chat_id: int):
        url = f"{self._domain}{self._token}/leaveChat"
        payload = aiohttp.FormData()
        payload.add_field("chat_id", chat_id)
        return await self._request(url, payload)

    # Attach async methods to the class
    cls.get_chat = get_chat
    cls.get_chat_administrators = get_chat_administrators
    cls.get_chat_member = get_chat_member
    cls.get_chat_member_count = get_chat_member_count
    cls.leave_chat = leave_chat
    return cls
