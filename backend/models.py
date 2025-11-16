from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    message: str


class URLRequest(BaseModel):
    url: str
