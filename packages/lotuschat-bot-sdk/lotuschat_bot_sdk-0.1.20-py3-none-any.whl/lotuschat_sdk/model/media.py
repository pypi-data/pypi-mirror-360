from typing import Optional

from pydantic import BaseModel, Field


class BaseMedia(BaseModel):
    file_id: Optional[str] = Field(default=None)
    file_size: Optional[int] = Field(default=None)
    link_cdn: Optional[str] = Field(default=None)


class PhotoSize(BaseMedia):
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    caption: Optional[str] = Field(default=None)


class Video(BaseMedia):
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    duration: Optional[int] = Field(default=None)
    mime_type: Optional[str] = Field(default=None)


class Animation(BaseMedia):
    thumb: Optional[PhotoSize] = Field(default=None)
    file_name: Optional[str] = Field(default=None)
    mime_type: Optional[str] = Field(default=None)
