from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from fastapi import HTTPException
import logging
from typing import Dict

logger = logging.getLogger(__name__)


async def measure_performance(url: str) -> Dict:
    """
    Measure page performance metrics using Playwright
    Returns load time, DOM content loaded time, and calculates performance score
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigation timing metrics
            navigation_start = None
            load_time = None
            dom_content_loaded_time = None
            
            # Start navigation and measure timing
            start_time = 0
            
            # Use Performance API to get accurate metrics
            await page.goto(url, wait_until="load", timeout=30000)
            
            # Get performance timing data
            performance_timing = await page.evaluate("""() => {
                const perfData = window.performance.timing;
                const navigation = window.performance.getEntriesByType('navigation')[0];
                
                return {
                    loadTime: perfData.loadEventEnd - perfData.navigationStart,
                    domContentLoadedTime: perfData.domContentLoadedEventEnd - perfData.navigationStart,
                    domInteractive: perfData.domInteractive - perfData.navigationStart,
                    firstPaint: navigation ? navigation.responseStart - navigation.fetchStart : 0,
                    transferSize: navigation ? navigation.transferSize : 0
                };
            }""")
            
            load_time_ms = performance_timing.get('loadTime', 0)
            dom_content_loaded_ms = performance_timing.get('domContentLoadedTime', 0)
            dom_interactive_ms = performance_timing.get('domInteractive', 0)
            transfer_size_bytes = performance_timing.get('transferSize', 0)
            
            # Calculate page size in KB
            page_size_kb = transfer_size_bytes / 1024 if transfer_size_bytes > 0 else None
            
            await browser.close()
            
            # Calculate performance score (0-100)
            performance_score = calculate_performance_score(
                load_time_ms,
                dom_content_loaded_ms,
                page_size_kb
            )
            
            return {
                "load_time_ms": round(load_time_ms, 2),
                "dom_content_loaded_ms": round(dom_content_loaded_ms, 2),
                "page_size_kb": round(page_size_kb, 2) if page_size_kb else None,
                "performance_score": performance_score,
            }
            
    except PlaywrightTimeout:
        raise HTTPException(
            status_code=408,
            detail="Request timeout while measuring performance"
        )
    except Exception as e:
        logger.error(f"Error measuring performance for {url}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to measure performance: {str(e)}"
        )


def calculate_performance_score(
    load_time_ms: float,
    dom_content_loaded_ms: float,
    page_size_kb: float = None
) -> int:
    """
    Calculate performance score (0-100) based on metrics
    
    Scoring criteria:
    - Load time: 40 points (< 2s: 40, < 3s: 30, < 5s: 20, < 7s: 10, >= 7s: 0)
    - DOM Content Loaded: 30 points (< 1s: 30, < 2s: 20, < 3s: 10, >= 3s: 0)
    - Page size: 30 points (< 500KB: 30, < 1MB: 20, < 2MB: 10, >= 2MB: 0)
    """
    score = 0
    
    # Load time scoring (40 points)
    load_time_s = load_time_ms / 1000
    if load_time_s < 2:
        score += 40
    elif load_time_s < 3:
        score += 30
    elif load_time_s < 5:
        score += 20
    elif load_time_s < 7:
        score += 10
    
    # DOM Content Loaded scoring (30 points)
    dcl_time_s = dom_content_loaded_ms / 1000
    if dcl_time_s < 1:
        score += 30
    elif dcl_time_s < 2:
        score += 20
    elif dcl_time_s < 3:
        score += 10
    
    # Page size scoring (30 points)
    if page_size_kb is not None:
        if page_size_kb < 500:
            score += 30
        elif page_size_kb < 1024:
            score += 20
        elif page_size_kb < 2048:
            score += 10
    else:
        # If we can't measure page size, give partial credit
        score += 15
    
    return min(score, 100)


def get_performance_recommendations(metrics: Dict) -> list:
    """Generate performance recommendations based on metrics"""
    recommendations = []
    
    load_time_s = metrics['load_time_ms'] / 1000
    dcl_time_s = metrics['dom_content_loaded_ms'] / 1000
    page_size_kb = metrics.get('page_size_kb')
    
    # Load time recommendations
    if load_time_s >= 5:
        recommendations.append(
            f"⚠️ Page load time is slow ({load_time_s:.2f}s). Target: < 3s for optimal user experience."
        )
    elif load_time_s >= 3:
        recommendations.append(
            f"⚡ Page load time is moderate ({load_time_s:.2f}s). Consider optimization to get under 2s."
        )
    
    # DOM Content Loaded recommendations
    if dcl_time_s >= 2:
        recommendations.append(
            f"⚠️ DOM Content Loaded time is high ({dcl_time_s:.2f}s). Optimize critical rendering path."
        )
    
    # Page size recommendations
    if page_size_kb and page_size_kb >= 2048:
        recommendations.append(
            f"📦 Page size is large ({page_size_kb:.0f}KB). Compress images, minify CSS/JS, use lazy loading."
        )
    elif page_size_kb and page_size_kb >= 1024:
        recommendations.append(
            f"📦 Page size is moderate ({page_size_kb:.0f}KB). Consider additional optimization."
        )
    
    # General recommendations based on score
    score = metrics.get('performance_score', 0)
    if score < 50:
        recommendations.append(
            "🚀 Critical: Implement CDN, enable compression, optimize images, and minimize render-blocking resources."
        )
    elif score < 75:
        recommendations.append(
            "💡 Consider: Browser caching, code splitting, and async loading of non-critical resources."
        )
    else:
        recommendations.append(
            "✅ Great performance! Maintain current optimization practices."
        )
    
    return recommendations

