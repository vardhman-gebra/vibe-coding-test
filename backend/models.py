from pydantic import BaseModel
from typing import List, Optional, Dict


class Message(BaseModel):
    message: str


class URLRequest(BaseModel):
    url: str


class CompareURLsRequest(BaseModel):
    urls: List[str]


class CROBreakdown(BaseModel):
    title: int
    meta_description: int
    h1_tags: int
    ctas: int
    forms: int
    content: int


class PerformanceMetrics(BaseModel):
    load_time_ms: float
    dom_content_loaded_ms: float
    page_size_kb: Optional[float] = None
    performance_score: int  # 0-100


class CROAnalysis(BaseModel):
    url: str
    score: int
    breakdown: CROBreakdown
    recommendations: List[str]
    performance: Optional[PerformanceMetrics] = None


class ComparisonResult(BaseModel):
    url: str
    score: int
    breakdown: CROBreakdown
    performance: PerformanceMetrics
    rank: int  # Overall ranking


class ComparisonAnalysis(BaseModel):
    timestamp: str
    total_analyzed: int
    results: List[ComparisonResult]
    winner: Dict[str, str]  # category -> url
    insights: List[str]
