"""
Playwright-based URL to PDF converter.

Renders a web page (e.g. PayPal invoice link) in headless Chromium
and exports it as PDF bytes for the existing invoice analysis pipeline.
"""

import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

# Timeout for initial page load (ms)
PAGE_TIMEOUT_MS = 45_000
# Time to wait for content to render after load event (ms)
RENDER_WAIT_MS = 5_000


async def _dismiss_cookie_banner(page) -> None:
    """Try to dismiss common cookie/consent banners that may cover invoice content."""
    selectors = [
        "#acceptAllButton",
        "#gdprCookieBanner button",
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

    Uses 'domcontentloaded' instead of 'networkidle' because PayPal keeps
    persistent connections open (analytics/tracking) which prevent networkidle
    from ever firing.
    """
    if not url or not url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL: must start with http:// or https://")

    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 1024},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                java_script_enabled=True,
            )

            # Remove webdriver flag that PayPal may detect
            await context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            page = await context.new_page()

            logger.info(f"Navigating to invoice URL ({len(url)} chars)")

            # Use 'domcontentloaded' - don't wait for networkidle (PayPal never reaches it)
            await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)

            # Wait for JS to render the invoice content
            logger.info("Waiting for page content to render...")
            await page.wait_for_timeout(RENDER_WAIT_MS)

            # Try to dismiss cookie banners
            await _dismiss_cookie_banner(page)

            # Additional wait after dismissing banners
            await page.wait_for_timeout(2000)

            # Log the final URL and title for debugging
            final_url = page.url
            title = await page.title()
            logger.info(f"Final URL: {final_url[:120]}")
            logger.info(f"Page title: {title}")

            # Check if we ended up on a login page
            if "signin" in final_url.lower() or "login" in final_url.lower():
                raise ValueError(
                    "PayPal redirected to login page. This invoice may require authentication."
                )

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
