import json

import aiohttp

from ..model.request import Command


def command_action(cls):
    async def set_command(self, commands: list[Command]):
        url = f"{self._domain}{self._token}/setMyCommands"
        payload = aiohttp.FormData()
        encoded_commands = json.dumps([c.model_dump() for c in commands], ensure_ascii=False)
        payload.add_field("commands", encoded_commands)
        return await self._request(url, payload)

    async def get_command(self):
        url = f"{self._domain}{self._token}/getMyCommands"
        return await self._request(url)

    async def delete_command(self, commands: list[Command]):
        url = f"{self._domain}{self._token}/deleteMyCommands"
        payload = aiohttp.FormData()
        encoded_commands = json.dumps([c.model_dump() for c in commands], ensure_ascii=False)
        payload.add_field("commands", encoded_commands)
        return await self._request(url, payload)

    # Attach async methods to the class
    cls.set_command = set_command
    cls.get_command = get_command
    cls.delete_command = delete_command
    return cls
