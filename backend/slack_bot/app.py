import os
import re
import time
import logging
import httpx
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from services.pdf_parser import extract_text_from_pdf, pdf_to_images_base64
from services.ai_validator import validate_invoice, validate_invoice_with_image
from services.url_to_pdf import fetch_pdf_from_url
from models.schemas import InvoiceType, Language, ValidationResult
from slack_bot.formatter import format_validation_result

logger = logging.getLogger(__name__)

# PayPal URL pattern to detect in messages
PAYPAL_URL_PATTERN = re.compile(
    r'https?://(?:www\.)?paypal\.com/invoice/[^\s>|]+'
)

# Simple in-memory cache for PDF bytes between file upload and button click
# Structure: {file_id: (pdf_bytes, timestamp)}
_pdf_cache: dict[str, tuple[bytes, float]] = {}
_CACHE_TTL_SECONDS = 600  # 10 minutes


def _cache_pdf(file_id: str, pdf_bytes: bytes) -> None:
    """Store PDF bytes in cache and clean expired entries."""
    now = time.time()
    # Clean expired entries
    expired = [k for k, (_, ts) in _pdf_cache.items() if now - ts > _CACHE_TTL_SECONDS]
    for k in expired:
        del _pdf_cache[k]
    _pdf_cache[file_id] = (pdf_bytes, now)


def _get_cached_pdf(file_id: str) -> bytes | None:
    """Retrieve PDF bytes from cache if not expired."""
    entry = _pdf_cache.get(file_id)
    if entry is None:
        return None
    pdf_bytes, ts = entry
    if time.time() - ts > _CACHE_TTL_SECONDS:
        del _pdf_cache[file_id]
        return None
    return pdf_bytes


def _get_allowed_channels() -> set[str] | None:
    """Get allowed channel IDs from env var. Returns None if not configured (allow all)."""
    channels = os.environ.get("SLACK_ALLOWED_CHANNELS", "").strip()
    if not channels:
        return None
    return {ch.strip() for ch in channels.split(",") if ch.strip()}


def _is_allowed_channel(channel_id: str) -> bool:
    """Check if channel is in the allowed list."""
    allowed = _get_allowed_channels()
    if allowed is None:
        return True  # No restriction configured
    return channel_id in allowed


async def _download_slack_file(url: str, token: str) -> bytes:
    """Download a file from Slack using the bot token for auth."""
    async with httpx.AsyncClient(timeout=30.0) as http:
        response = await http.get(
            url, headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.content


async def _process_pdf_bytes(
    pdf_bytes: bytes, invoice_type: InvoiceType
) -> ValidationResult:
    """
    Core processing pipeline - reuses existing services.
    Mirrors the logic in main.py's analyze endpoints.
    """
    invoice_text = extract_text_from_pdf(pdf_bytes)

    if invoice_text == "[IMAGE_PDF]":
        images = pdf_to_images_base64(pdf_bytes)
        if not images:
            raise ValueError("Kunne ikke konvertere PDF til billeder.")
        return await validate_invoice_with_image(
            images, invoice_type, Language.DANISH
        )
    else:
        return await validate_invoice(
            invoice_text, invoice_type, Language.DANISH
        )


def _extract_message_ts(shares: dict, channel_id: str) -> str | None:
    """Extract the message timestamp from file shares for threading."""
    for share_type in ("public", "private"):
        channel_shares = shares.get(share_type, {}).get(channel_id, [])
        if channel_shares:
            return channel_shares[0].get("ts")
    return None


def _build_type_selection_blocks(file_id: str, filename: str) -> list[dict]:
    """Build Block Kit message with invoice type selection buttons."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":page_facing_up: *{filename}* modtaget!\nHvilken type faktura er det?",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "PayPal faktura", "emoji": True},
                    "style": "primary",
                    "action_id": "invoice_type_paypal",
                    "value": file_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Bankoverførsel", "emoji": True},
                    "action_id": "invoice_type_bank",
                    "value": file_id,
                },
            ],
        },
    ]


def create_slack_app() -> AsyncApp:
    """Create and configure the Slack Bolt async app."""
    slack_app = AsyncApp(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    )
    _register_handlers(slack_app)
    return slack_app


def _register_handlers(slack_app: AsyncApp) -> None:
    """Register all Slack event and action handlers."""

    @slack_app.event("file_shared")
    async def handle_file_shared(event, client, say):
        """Handle PDF files shared in channels/DMs."""
        file_id = event.get("file_id")
        channel_id = event.get("channel_id")

        if not _is_allowed_channel(channel_id):
            return

        # Get file info
        file_info = await client.files_info(file=file_id)
        file_data = file_info["file"]

        filename = file_data.get("name", "")
        mimetype = file_data.get("mimetype", "")

        # Only process PDFs
        if not filename.lower().endswith(".pdf") and mimetype != "application/pdf":
            return

        # Find the message timestamp for threading
        shares = file_data.get("shares", {})
        message_ts = _extract_message_ts(shares, channel_id)

        try:
            # Download file
            url_private = file_data.get("url_private_download") or file_data.get("url_private")
            if not url_private:
                return

            pdf_bytes = await _download_slack_file(
                url_private, os.environ["SLACK_BOT_TOKEN"]
            )

            # Cache PDF for when user clicks a button
            _cache_pdf(file_id, pdf_bytes)

            # Send type selection buttons
            blocks = _build_type_selection_blocks(file_id, filename)
            await say(
                text=f"{filename} modtaget! Hvilken type faktura er det?",
                blocks=blocks,
                channel=channel_id,
                thread_ts=message_ts,
            )
        except Exception as e:
            logger.exception(f"Error handling file {file_id}")
            await say(
                text=f":x: Fejl ved behandling af fil: {str(e)}",
                channel=channel_id,
                thread_ts=message_ts,
            )

    @slack_app.action("invoice_type_paypal")
    async def handle_paypal_selected(ack, body, client):
        """Handle PayPal button click."""
        await ack()
        await _process_with_type(body, client, InvoiceType.PAYPAL)

    @slack_app.action("invoice_type_bank")
    async def handle_bank_selected(ack, body, client):
        """Handle Bank Transfer button click."""
        await ack()
        await _process_with_type(body, client, InvoiceType.BANK_TRANSFER)

    async def _process_with_type(body: dict, client, invoice_type: InvoiceType):
        """Process a cached PDF with the selected invoice type."""
        file_id = body["actions"][0]["value"]
        channel_id = body["channel"]["id"]
        message_ts = body["message"]["ts"]
        thread_ts = body["message"].get("thread_ts", message_ts)
        user_id = body["user"]["id"]

        type_label = "PayPal faktura" if invoice_type == InvoiceType.PAYPAL else "Bankoverførsel"

        # Update the button message to show processing status
        await client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=f":hourglass_flowing_sand: Analyserer som {type_label}...",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":hourglass_flowing_sand: <@{user_id}> valgte *{type_label}* — analyserer...",
                    },
                }
            ],
        )

        try:
            pdf_bytes = _get_cached_pdf(file_id)
            if pdf_bytes is None:
                await client.chat_update(
                    channel=channel_id,
                    ts=message_ts,
                    text=":x: PDF'en er udløbet fra cache. Upload filen igen.",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": ":x: PDF'en er udløbet fra cache. Upload filen igen.",
                            },
                        }
                    ],
                )
                return

            result = await _process_pdf_bytes(pdf_bytes, invoice_type)

            # Format result as Block Kit
            blocks = format_validation_result(result, type_label)
            await client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=result.summary,
                blocks=blocks,
            )

            # Clean up cache
            _pdf_cache.pop(file_id, None)

        except Exception as e:
            logger.exception(f"Error processing file {file_id} as {invoice_type.value}")
            await client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=f":x: Fejl ved analyse: {str(e)}",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f":x: Fejl ved analyse: {str(e)}",
                        },
                    }
                ],
            )

    @slack_app.event("message")
    async def handle_message(event, client, say):
        """Handle messages that may contain PayPal invoice URLs."""
        # Ignore bot messages, edits, etc.
        if event.get("subtype"):
            return

        channel_id = event.get("channel")
        if not _is_allowed_channel(channel_id):
            return

        text = event.get("text", "")
        message_ts = event.get("ts")

        # Check for PayPal URLs
        urls = PAYPAL_URL_PATTERN.findall(text)
        if not urls:
            return

        for url in urls:
            # Clean Slack auto-link formatting
            url = url.strip("<>").split("|")[0]

            processing_msg = await say(
                text=":hourglass_flowing_sand: Henter og analyserer PayPal faktura...",
                channel=channel_id,
                thread_ts=message_ts,
            )

            try:
                pdf_bytes = await fetch_pdf_from_url(url)
                result = await _process_pdf_bytes(pdf_bytes, InvoiceType.PAYPAL)

                blocks = format_validation_result(result, "PayPal faktura (link)")
                await client.chat_update(
                    channel=channel_id,
                    ts=processing_msg["ts"],
                    text=result.summary,
                    blocks=blocks,
                )
            except Exception as e:
                logger.exception(f"Error processing URL: {url[:80]}")
                await client.chat_update(
                    channel=channel_id,
                    ts=processing_msg["ts"],
                    text=f":x: Fejl ved behandling af PayPal link: {str(e)}",
                )
