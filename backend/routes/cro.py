from fastapi import APIRouter, HTTPException, Query
from models import (
    URLRequest, 
    CROAnalysis, 
    CROBreakdown, 
    CompareURLsRequest, 
    ComparisonAnalysis,
    ComparisonResult,
    PerformanceMetrics
)
from services.scraper import extract_html_content
from services.performance_analyzer import measure_performance, get_performance_recommendations
import logging
import asyncio
from datetime import datetime

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
async def get_cro_recommendations(
    request: URLRequest,
    include_performance: bool = Query(True, description="Include performance metrics")
):
    """Analyze a URL and return CRO score with recommendations and performance metrics"""
    try:
        # Extract HTML content and measure performance in parallel
        if include_performance:
            content_data, performance_data = await asyncio.gather(
                extract_html_content(request.url),
                measure_performance(request.url),
                return_exceptions=True
            )
            
            # Handle performance measurement errors gracefully
            if isinstance(performance_data, Exception):
                logger.warning(f"Performance measurement failed: {performance_data}")
                performance_data = None
        else:
            content_data = await extract_html_content(request.url)
            performance_data = None
        
        # Handle content extraction errors
        if isinstance(content_data, Exception):
            raise content_data
        
        # Calculate CRO score
        score, breakdown, recommendations = calculate_cro_score(content_data)
        
        # Add performance recommendations if available
        if performance_data:
            perf_recommendations = get_performance_recommendations(performance_data)
            recommendations.extend(perf_recommendations)
            performance_metrics = PerformanceMetrics(**performance_data)
        else:
            performance_metrics = None
        
        # Return analysis
        return CROAnalysis(
            url=request.url,
            score=score,
            breakdown=breakdown,
            recommendations=recommendations,
            performance=performance_metrics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing URL {request.url}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze URL: {str(e)}"
        )


@router.post("/compare", response_model=ComparisonAnalysis)
async def compare_competitors(request: CompareURLsRequest):
    """
    Compare multiple URLs side-by-side for CRO and performance metrics.
    Analyzes all URLs in parallel and provides competitive insights.
    """
    if not request.urls or len(request.urls) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least 2 URLs for comparison"
        )
    
    if len(request.urls) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 URLs allowed for comparison"
        )
    
    try:
        logger.info(f"Starting comparison analysis for {len(request.urls)} URLs")
        
        # Analyze all URLs in parallel
        analysis_tasks = []
        for url in request.urls:
            analysis_tasks.append(analyze_single_url(url))
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Filter out failed analyses
        successful_results = []
        failed_urls = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to analyze {request.urls[i]}: {result}")
                failed_urls.append(request.urls[i])
            else:
                successful_results.append(result)
        
        if not successful_results:
            raise HTTPException(
                status_code=500,
                detail="All URL analyses failed. Please check the URLs and try again."
            )
        
        # Rank results by combined score (CRO score + performance score)
        for result in successful_results:
            result['combined_score'] = result['cro_score'] + result['performance_score']
        
        successful_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Assign ranks
        comparison_results = []
        for rank, result in enumerate(successful_results, 1):
            comparison_results.append(ComparisonResult(
                url=result['url'],
                score=result['cro_score'],
                breakdown=result['breakdown'],
                performance=result['performance'],
                rank=rank
            ))
        
        # Determine winners by category
        winner = determine_winners(successful_results)
        
        # Generate insights
        insights = generate_comparison_insights(successful_results, failed_urls)
        
        return ComparisonAnalysis(
            timestamp=datetime.utcnow().isoformat(),
            total_analyzed=len(successful_results),
            results=comparison_results,
            winner=winner,
            insights=insights
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comparison analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete comparison: {str(e)}"
        )


async def analyze_single_url(url: str) -> dict:
    """Analyze a single URL for comparison"""
    try:
        # Extract content and measure performance in parallel
        content_data, performance_data = await asyncio.gather(
            extract_html_content(url),
            measure_performance(url),
            return_exceptions=True
        )
        
        # Handle errors
        if isinstance(content_data, Exception):
            raise content_data
        if isinstance(performance_data, Exception):
            logger.warning(f"Performance measurement failed for {url}: {performance_data}")
            performance_data = {
                "load_time_ms": 0,
                "dom_content_loaded_ms": 0,
                "page_size_kb": None,
                "performance_score": 0
            }
        
        # Calculate CRO score
        cro_score, breakdown, _ = calculate_cro_score(content_data)
        
        return {
            "url": url,
            "cro_score": cro_score,
            "breakdown": breakdown,
            "performance": PerformanceMetrics(**performance_data),
            "performance_score": performance_data['performance_score']
        }
    
    except Exception as e:
        logger.error(f"Error analyzing {url}: {e}")
        raise


def determine_winners(results: list) -> dict:
    """Determine the winner in each category"""
    if not results:
        return {}
    
    winner = {}
    
    # Overall winner (highest combined score)
    overall_winner = max(results, key=lambda x: x['combined_score'])
    winner['overall'] = overall_winner['url']
    
    # CRO score winner
    cro_winner = max(results, key=lambda x: x['cro_score'])
    winner['cro_score'] = cro_winner['url']
    
    # Performance winner
    perf_winner = max(results, key=lambda x: x['performance_score'])
    winner['performance'] = perf_winner['url']
    
    # Individual breakdown categories
    breakdown_categories = ['title', 'meta_description', 'h1_tags', 'ctas', 'forms', 'content']
    for category in breakdown_categories:
        category_winner = max(results, key=lambda x: getattr(x['breakdown'], category))
        winner[category] = category_winner['url']
    
    return winner


def generate_comparison_insights(results: list, failed_urls: list) -> list:
    """Generate insights from comparison analysis"""
    insights = []
    
    if not results:
        return ["No successful analyses to compare"]
    
    # Overall performance insight
    avg_cro = sum(r['cro_score'] for r in results) / len(results)
    avg_perf = sum(r['performance_score'] for r in results) / len(results)
    
    insights.append(
        f"📊 Average CRO Score: {avg_cro:.0f}/100 | Average Performance Score: {avg_perf:.0f}/100"
    )
    
    # Best and worst performers
    best = results[0]
    worst = results[-1]
    
    insights.append(
        f"🏆 Top Performer: {best['url']} (Combined Score: {best['combined_score']:.0f}/200)"
    )
    
    if len(results) > 1:
        score_gap = best['combined_score'] - worst['combined_score']
        insights.append(
            f"📉 Score Gap: {score_gap:.0f} points between best and worst performers"
        )
    
    # Category-specific insights
    cro_scores = [r['cro_score'] for r in results]
    perf_scores = [r['performance_score'] for r in results]
    
    if max(cro_scores) - min(cro_scores) > 30:
        insights.append(
            "⚠️ Large CRO score variance detected. Focus on bringing lower performers up to standards."
        )
    
    if max(perf_scores) - min(perf_scores) > 30:
        insights.append(
            "⚡ Significant performance differences found. Slower sites may benefit from CDN and optimization."
        )
    
    # Load time insights
    load_times = [r['performance'].load_time_ms / 1000 for r in results]
    avg_load_time = sum(load_times) / len(load_times)
    
    if avg_load_time > 3:
        insights.append(
            f"🐌 Average load time is {avg_load_time:.2f}s. Target: < 3s for all pages."
        )
    
    # Failed URLs
    if failed_urls:
        insights.append(
            f"❌ {len(failed_urls)} URL(s) failed to analyze: {', '.join(failed_urls[:3])}"
        )
    
    # Opportunities
    insights.append(
        "💡 Opportunity: Benchmark against top performer and implement their best practices."
    )
    
    return insights

