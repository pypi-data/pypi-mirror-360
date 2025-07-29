from ..control.api_command import command_action
from ..control.api_info import info_action
from ..control.api_message import message_action
from ..control.bot import ChatBot

command_action(ChatBot)
info_action(ChatBot)
message_action(ChatBot)

__all__ = ["ChatBot"]
