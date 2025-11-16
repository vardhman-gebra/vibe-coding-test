from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from fastapi import HTTPException
import re
import logging

logger = logging.getLogger(__name__)


async def extract_html_content(url: str) -> dict:
    """Extract HTML content from URL using Playwright"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, wait_until="networkidle", timeout=15000)
            content = await page.content()
            title = await page.title()

            await browser.close()

            # Parse HTML
            soup = BeautifulSoup(content, "lxml")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Extract key elements
            h1_tags = [h1.get_text().strip() for h1 in soup.find_all("h1")]
            meta_desc = soup.find("meta", attrs={"name": "description"})
            meta_description = (
                meta_desc["content"] if meta_desc and meta_desc.get("content") else None
            )

            # Check for CTAs
            buttons = soup.find_all(
                ["button", "a"], class_=re.compile(r"(btn|button|cta)", re.I)
            )
            cta_texts = [btn.get_text().strip() for btn in buttons[:5]]

            # Check for forms
            forms = soup.find_all("form")
            has_forms = len(forms) > 0

            return {
                "title": title,
                "text": text[:5000],  # Limit text for processing
                "h1_tags": h1_tags,
                "meta_description": meta_description,
                "cta_texts": cta_texts,
                "has_forms": has_forms,
                "content_length": len(text),
            }
    except PlaywrightTimeout:
        raise HTTPException(
            status_code=408, detail="Request timeout while loading the page"
        )
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to extract content: {str(e)}"
        )
