from typing import Optional

from pydantic import BaseModel, HttpUrl


class Image(BaseModel):
    url: Optional[HttpUrl] = None
    b64_json: Optional[str] = None
    metadata: dict


class Text(BaseModel):
    content: str
    metadata: dict


__all__ = ["Image", "Text"]
