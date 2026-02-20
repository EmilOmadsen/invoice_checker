"""
Playwright-based URL to PDF converter.

Renders a web page (e.g. PayPal invoice link) in headless Chromium
and exports it as PDF bytes for the existing invoice analysis pipeline.
"""

import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

# Timeout for page load (ms) - PayPal pages can be slow with redirects
PAGE_TIMEOUT_MS = 60_000
# Additional wait after network idle for JS-heavy pages
SETTLE_DELAY_MS = 3_000


async def _dismiss_cookie_banner(page) -> None:
    """Try to dismiss common cookie/consent banners that may cover invoice content."""
    selectors = [
        "#acceptAllButton",           # PayPal cookie accept
        "#gdprCookieBanner button",   # PayPal GDPR banner
        "[data-testid='accept-cookies']",
        "button:has-text('Accept')",
        "button:has-text('Accept All')",
        "button:has-text('OK')",
    ]
    for selector in selectors:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=1000):
                await btn.click()
                logger.info(f"Dismissed cookie banner via: {selector}")
                await page.wait_for_timeout(500)
                return
        except Exception:
            continue


async def fetch_pdf_from_url(url: str) -> bytes:
    """
    Open a URL in headless Chromium, wait for full render, and return PDF bytes.

    Args:
        url: The invoice URL to render (e.g. PayPal invoice link)

    Returns:
        PDF content as bytes

    Raises:
        ValueError: If the URL is invalid or the page cannot be rendered
    """
    if not url or not url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL: must start with http:// or https://")

    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 1024},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="en-US",
            )
            page = await context.new_page()

            logger.info(f"Navigating to invoice URL ({len(url)} chars)")
            await page.goto(url, wait_until="networkidle", timeout=PAGE_TIMEOUT_MS)

            # Try to dismiss cookie banners
            await _dismiss_cookie_banner(page)

            # Extra settle time for JS-rendered content (PayPal is heavy)
            await page.wait_for_timeout(SETTLE_DELAY_MS)

            # Log the final URL (PayPal may redirect)
            final_url = page.url
            if final_url != url:
                logger.info(f"Page redirected to: {final_url[:100]}")

            # Log page title for debugging
            title = await page.title()
            logger.info(f"Page title: {title}")

            logger.info("Generating PDF from rendered page")
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
            )

            if not pdf_bytes or len(pdf_bytes) < 100:
                raise ValueError("Generated PDF is empty or too small")

            logger.info(f"PDF generated: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except PlaywrightTimeout:
            raise ValueError(
                f"Page load timed out after {PAGE_TIMEOUT_MS // 1000}s. "
                "The URL may be inaccessible or require authentication."
            )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to render page as PDF: {str(e)}")
        finally:
            if browser:
                await browser.close()
