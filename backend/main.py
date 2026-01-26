import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from services.pdf_parser import extract_text_from_pdf, pdf_to_images_base64
from services.ai_validator import validate_invoice, validate_invoice_with_image
from models.schemas import ValidationResult, InvoiceType, Language

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
