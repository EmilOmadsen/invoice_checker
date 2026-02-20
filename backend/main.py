import os
import base64
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx

from services.pdf_parser import extract_text_from_pdf, pdf_to_images_base64
from services.ai_validator import validate_invoice, validate_invoice_with_image
from models.schemas import ValidationResult, InvoiceType, Language, InvoicePayload

logger = logging.getLogger(__name__)

# Load environment variables from .env file in the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

app = FastAPI(
    title="Invoice Checker API",
    description="API for validating invoices against Sunday's requirements",
    version="1.0.0"
)

# Configure CORS for frontend
# Get allowed origins from environment variable, with defaults for local development
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Invoice Checker API is running"}


@app.post("/api/analyze", response_model=ValidationResult)
async def analyze_invoice(
    file: UploadFile = File(...),
    invoice_type: str = Form(default="paypal"),
    language: str = Form(default="da")
):
    """
    Analyze an uploaded invoice PDF.

    - **file**: PDF file to analyze
    - **invoice_type**: Type of invoice ("paypal" or "bank_transfer")
    - **language**: Response language ("da" for Danish, "en" for English)

    Returns a validation result with:
    - Overall status (approved/missing_information/invalid)
    - Invoice type
    - Individual check results
    - List of missing items
    - Warnings
    - Layout suggestions
    - Summary
    """
    # Validate invoice type
    try:
        validated_type = InvoiceType(invoice_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid invoice type. Must be 'paypal' or 'bank_transfer'"
        )

    # Validate language
    try:
        validated_language = Language(language)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language. Must be 'da' or 'en'"
        )
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_extensions = {".pdf"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Extract text from PDF
    try:
        invoice_text = extract_text_from_pdf(content)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

    # Check if it's an image-based PDF
    if invoice_text == "[IMAGE_PDF]":
        # Convert PDF to images and use vision API
        try:
            images = pdf_to_images_base64(content)
            if not images:
                raise HTTPException(
                    status_code=422,
                    detail="Could not convert PDF to images."
                )
            result = await validate_invoice_with_image(images, validated_type, validated_language)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate image-based invoice: {str(e)}"
            )
    else:
        # Validate with AI using text
        try:
            result = await validate_invoice(invoice_text, validated_type, validated_language)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate invoice: {str(e)}"
            )

    return result


@app.post("/api/analyze-invoice")
async def analyze_invoice_json(payload: InvoicePayload):
    """
    Analyze an invoice PDF sent as JSON with base64-encoded content.

    This endpoint is designed for Microsoft Copilot Agent Flow integration.

    Request body (Content-Type: application/json):
    - **contentBytes**: Base64-encoded PDF file content
    - **name**: Filename (e.g., "invoice.pdf")
    - **invoice_type**: Type of invoice ("paypal" or "bank_transfer"), defaults to "paypal"
    - **language**: Response language ("da" or "en"), defaults to "da"

    Returns:
    - **status**: "pass" or "fail"
    - **logs**: Detailed validation results
    """
    # Get PDF content from either contentBytes or contentUrl
    content = b""

    if payload.contentBytes:
        # Decode base64 content
        try:
            content = base64.b64decode(payload.contentBytes)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid base64 file content"
            )

    if not content and payload.contentUrl:
        # Download file from URL (e.g. Copilot Studio attachment URL)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(payload.contentUrl)
                response.raise_for_status()
                content = response.content
                logger.info(f"Downloaded {len(content)} bytes from contentUrl")
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download file from URL (HTTP {e.response.status_code})"
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download file from URL: {str(e)}"
            )

    # If no PDF content yet, try rendering invoiceUrl via Playwright
    if not content and payload.invoiceUrl:
        from services.url_to_pdf import fetch_pdf_from_url
        try:
            logger.info(f"Rendering invoice URL to PDF: {payload.invoiceUrl[:100]}")
            content = await fetch_pdf_from_url(payload.invoiceUrl)
            logger.info(f"Rendered PDF from URL: {len(content)} bytes")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to render invoice URL as PDF: {str(e)}"
            )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="No file content provided. Supply 'contentBytes' (base64), 'contentUrl', or 'invoiceUrl'."
        )

    # Validate file extension (skip for invoiceUrl since we generated the PDF)
    if not payload.invoiceUrl:
        allowed_extensions = {".pdf"}
        file_ext = os.path.splitext(payload.name)[1].lower() if payload.name else ""

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )

    # Extract text from PDF
    try:
        invoice_text = extract_text_from_pdf(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

    # Validate the invoice
    try:
        if invoice_text == "[IMAGE_PDF]":
            # Convert PDF to images and use vision API
            images = pdf_to_images_base64(content)
            if not images:
                raise HTTPException(
                    status_code=500,
                    detail="Could not convert PDF to images."
                )
            result = await validate_invoice_with_image(images, payload.invoice_type, payload.language)
        else:
            # Validate with AI using text
            result = await validate_invoice(invoice_text, payload.invoice_type, payload.language)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate invoice: {str(e)}"
        )

    # Transform result to Copilot-compatible format
    status = "pass" if result.overall_status.value == "approved" else "fail"

    # Build readable logs for Copilot Studio chat display
    present_checks = [c for c in result.checks if c.status.value == "present"]
    missing_checks = [c for c in result.checks if c.status.value == "missing"]
    unclear_checks = [c for c in result.checks if c.status.value == "unclear"]

    # Collect issues: each issue paired with its fix
    issues = []

    for check in missing_checks:
        fix = check.fix_recommendation or f"Add {check.requirement.lower()} to the invoice"
        issues.append({
            "icon": "❌",
            "label": f"Missing: {check.requirement}",
            "fix": fix
        })

    for check in unclear_checks:
        label = check.requirement
        if check.found_value:
            label += f" (found: {check.found_value})"
        fix = check.fix_recommendation or f"Correct {check.requirement.lower()} on the invoice"
        issues.append({
            "icon": "⚠️",
            "label": f"Incorrect: {label}",
            "fix": fix
        })

    for warning in (result.warnings or []):
        issues.append({
            "icon": "⚠️",
            "label": warning,
            "fix": None
        })

    # Build clean output
    total_checked = len(present_checks) + len(missing_checks) + len(unclear_checks)
    passed = len(present_checks)

    if issues:
        parts = []
        parts.append(f"✅ {passed}/{total_checked} checks passed")
        parts.append("")

        # Issues section - each on its own line with blank line between
        parts.append(f"🚨 Issues found:")
        parts.append("")
        for issue in issues:
            parts.append(f"  {issue['icon']}  {issue['label']}")
            parts.append("")

        # Fixes section - numbered, each on its own line
        fixes = [issue for issue in issues if issue["fix"]]
        if fixes:
            parts.append(f"🔧 How to fix:")
            parts.append("")
            for i, issue in enumerate(fixes, 1):
                parts.append(f"  {i}.  {issue['fix']}")
                parts.append("")

        logs_text = "\n".join(parts)
    else:
        logs_text = f"✅ All {total_checked} checks passed!\n\nInvoice looks good — no issues found."

    # Build short summary
    if issues:
        summary_text = f"{len(issues)} issues found. {passed}/{total_checked} checks passed."
    else:
        summary_text = f"All {total_checked} checks passed."

    return {
        "status": status,
        "logs": logs_text,
        "summary": summary_text
    }


@app.post("/api/test-connection")
async def test_connection(payload: InvoicePayload):
    """
    Debug endpoint to test connectivity from Power Automate.
    Returns info about what was received without calling AI.
    """
    return {
        "status": "ok",
        "received": {
            "has_contentBytes": bool(payload.contentBytes),
            "contentBytes_length": len(payload.contentBytes) if payload.contentBytes else 0,
            "has_contentUrl": bool(payload.contentUrl),
            "contentUrl": payload.contentUrl[:100] if payload.contentUrl else None,
            "has_invoiceUrl": bool(payload.invoiceUrl),
            "invoiceUrl": payload.invoiceUrl[:100] if payload.invoiceUrl else None,
            "name": payload.name,
            "invoice_type": payload.invoice_type.value,
            "language": payload.language.value,
        }
    }


@app.get("/api/requirements")
async def get_requirements(invoice_type: str = "paypal"):
    """Get the list of invoice requirements for a specific type."""
    from services.requirements import get_requirements_for_type
    if invoice_type not in ["paypal", "bank_transfer"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid invoice type. Must be 'paypal' or 'bank_transfer'"
        )
    return get_requirements_for_type(invoice_type)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
