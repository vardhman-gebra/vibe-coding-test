from pydantic import BaseModel
from typing import List, Optional, Dict


class Message(BaseModel):
    message: str


class URLRequest(BaseModel):
    url: str


class CROBreakdown(BaseModel):
    title: int
    meta_description: int
    h1_tags: int
    ctas: int
    forms: int
    content: int


class CROAnalysis(BaseModel):
    url: str
    score: int
    breakdown: CROBreakdown
    recommendations: List[str]
