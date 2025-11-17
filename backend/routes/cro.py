from fastapi import APIRouter, HTTPException
from models import URLRequest, CROAnalysis, CROBreakdown
from services.scraper import extract_html_content
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cro", tags=["CRO"])


def calculate_cro_score(content_data: dict) -> tuple[int, CROBreakdown, list[str]]:
    """Calculate CRO score based on content analysis"""
    breakdown = {
        "title": 0,
        "meta_description": 0,
        "h1_tags": 0,
        "ctas": 0,
        "forms": 0,
        "content": 0,
    }
    recommendations = []
    
    # Title Quality (20 points)
    title = content_data.get("title", "")
    if title:
        breakdown["title"] += 10
        title_length = len(title)
        if 30 <= title_length <= 60:
            breakdown["title"] += 10
        else:
            if title_length < 30:
                recommendations.append(
                    f"Title is too short ({title_length} characters). Recommended: 30-60 characters for better SEO."
                )
            else:
                recommendations.append(
                    f"Title is too long ({title_length} characters). Recommended: 30-60 characters for better SEO."
                )
    else:
        recommendations.append("Add a title tag to your page for better SEO and user experience.")
    
    # Meta Description (15 points)
    meta_desc = content_data.get("meta_description", "")
    if meta_desc:
        breakdown["meta_description"] += 10
        meta_length = len(meta_desc)
        if 120 <= meta_length <= 160:
            breakdown["meta_description"] += 5
        else:
            if meta_length < 120:
                recommendations.append(
                    f"Meta description is too short ({meta_length} characters). Recommended: 120-160 characters."
                )
            else:
                recommendations.append(
                    f"Meta description is too long ({meta_length} characters). Recommended: 120-160 characters."
                )
    else:
        recommendations.append("Add a meta description to improve search engine results and click-through rates.")
    
    # H1 Tags (15 points)
    h1_tags = content_data.get("h1_tags", [])
    h1_count = len(h1_tags)
    if h1_count >= 1:
        breakdown["h1_tags"] += 10
        if h1_count == 1:
            breakdown["h1_tags"] += 5
        else:
            recommendations.append(
                f"Multiple H1 tags detected ({h1_count}). Stick to one H1 tag for better SEO."
            )
    else:
        recommendations.append("Add an H1 tag to clearly define your page's main heading.")
    
    # Call-to-Action CTAs (25 points)
    cta_texts = content_data.get("cta_texts", [])
    cta_count = len(cta_texts)
    if cta_count >= 1:
        breakdown["ctas"] += 15
        if cta_count >= 2:
            breakdown["ctas"] += 10
        else:
            recommendations.append(
                "Consider adding more CTA buttons to increase conversion opportunities (currently: 1)."
            )
    else:
        recommendations.append("Add clear call-to-action buttons to guide users toward conversion.")
    
    # Forms (15 points)
    has_forms = content_data.get("has_forms", False)
    if has_forms:
        breakdown["forms"] += 15
    else:
        recommendations.append("Consider adding a form to capture leads or enable user interaction.")
    
    # Content Length (10 points)
    content_length = content_data.get("content_length", 0)
    word_count = content_length // 6  # Rough estimate: average word length ~6 characters
    if content_length > 1800:  # ~300 words
        breakdown["content"] += 10
    else:
        recommendations.append(
            f"Add more content to your page (current: ~{word_count} words, recommended: 300+ words)."
        )
    
    # Calculate total score
    total_score = sum(breakdown.values())
    
    # Add congratulations if score is good
    if total_score >= 80:
        recommendations.insert(0, "🎉 Excellent! Your page follows most CRO best practices.")
    elif total_score >= 60:
        recommendations.insert(0, "👍 Good job! A few improvements can make your page even better.")
    
    return total_score, CROBreakdown(**breakdown), recommendations


@router.post("/recommendations", response_model=CROAnalysis)
async def get_cro_recommendations(request: URLRequest):
    """Analyze a URL and return CRO score with recommendations"""
    try:
        # Extract HTML content using the scraper
        content_data = await extract_html_content(request.url)
        
        # Calculate CRO score
        score, breakdown, recommendations = calculate_cro_score(content_data)
        
        # Return analysis
        return CROAnalysis(
            url=request.url,
            score=score,
            breakdown=breakdown,
            recommendations=recommendations,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing URL {request.url}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze URL: {str(e)}"
        )

