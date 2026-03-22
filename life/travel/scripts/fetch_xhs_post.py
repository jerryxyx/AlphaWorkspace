#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

XHS_SESSION = Path.home() / ".x-reader" / "sessions" / "xhs.json"

async def fetch_xhs_post(url: str):
    """Fetch Xiaohongshu post content using saved session."""
    async with async_playwright() as p:
        # Launch browser with stored session
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        
        # Load saved cookies
        if XHS_SESSION.exists():
            with open(XHS_SESSION) as f:
                session_data = json.load(f)
            cookies = session_data.get("cookies", [])
            await context.add_cookies(cookies)
            print(f"Loaded {len(cookies)} cookies from session")
        
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Wait for content to load
        await page.wait_for_timeout(3000)
        
        # Try to extract title and text
        title = await page.title()
        
        # Try multiple selectors for content
        selectors = [
            "div.note-content",
            "article.note",
            "[data-v-]",
            ".content",
            ".note-container",
            "main",
        ]
        content_text = ""
        for sel in selectors:
            if await page.locator(sel).count() > 0:
                content_text = await page.locator(sel).inner_text()
                if content_text.strip():
                    break
        
        # If still empty, fallback to body
        if not content_text.strip():
            content_text = await page.locator("body").inner_text()
        
        # Extract image URLs
        img_urls = []
        img_elements = await page.locator("img").all()
        for img in img_elements:
            src = await img.get_attribute("src")
            if src and "http" in src:
                img_urls.append(src)
        
        # Try to get post metadata (likes, comments, etc.)
        metadata = {}
        # Common Xiaohongshu selectors
        like_sel = "span.like-count, [data-v-][class*='like']"
        comment_sel = "span.comment-count, [data-v-][class*='comment']"
        if await page.locator(like_sel).count() > 0:
            metadata["likes"] = await page.locator(like_sel).first().inner_text()
        if await page.locator(comment_sel).count() > 0:
            metadata["comments"] = await page.locator(comment_sel).first().inner_text()
        
        # Try to get author
        author_sel = ".author-name, .user-info, [data-v-][class*='author']"
        if await page.locator(author_sel).count() > 0:
            metadata["author"] = await page.locator(author_sel).first().inner_text()
        
        await browser.close()
        
        return {
            "url": url,
            "title": title,
            "content": content_text.strip(),
            "image_urls": img_urls,
            "metadata": metadata,
        }

async def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_xhs_post.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    print(f"Fetching {url}...")
    result = await fetch_xhs_post(url)
    output_file = Path("xhs_post_result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_file}")
    print(f"Title: {result['title']}")
    print(f"Content preview: {result['content'][:200]}...")
    print(f"Images: {len(result['image_urls'])}")

if __name__ == "__main__":
    asyncio.run(main())