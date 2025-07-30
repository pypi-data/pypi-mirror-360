from enum import Enum
from typing import Any

from pydantic import BaseModel


class MessageStatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class MessageResponse(BaseModel):
    status: MessageStatusEnum
    error: str
    data: Any


class MessageResponseSuccess(MessageResponse):
    status: MessageStatusEnum = MessageStatusEnum.SUCCESS
    error: str = ""


class MessageResponseError(MessageResponse):
    status: MessageStatusEnum = MessageStatusEnum.ERROR
    data: Any = None
