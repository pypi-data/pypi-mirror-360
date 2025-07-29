from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from ..model.message import MessageEntity

# ####################################################################################################
# const
# ####################################################################################################
FAILED_REQUEST = "Api[{}] request failed. Error: {}}"

TYPE_BOT_COMMAND = "bot_command"
TYPE_UNKNOWN = "unknown"
TYPE_TEXT = "text"

CODE_SUCCESS = 200
CODE_FAIL_BOT = 500
CODE_FAIL_MESSAGE = 501


# ####################################################################################################
# class for event listener
# ####################################################################################################
class ErrorType(Enum):
    BOT = "Bot"
    MESSAGE = "Message"


class Argument(BaseModel):
    text: str
    type: str
    entity: Optional[MessageEntity] = Field(default=None)
