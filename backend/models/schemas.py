from pydantic import BaseModel
from typing import Literal, Optional, List
from enum import Enum


class InvoiceType(str, Enum):
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class Language(str, Enum):
    DANISH = "da"
    ENGLISH = "en"


class CheckStatus(str, Enum):
    PRESENT = "present"
    MISSING = "missing"
    UNCLEAR = "unclear"


class OverallStatus(str, Enum):
    APPROVED = "approved"
    MISSING_INFORMATION = "missing_information"
    INVALID = "invalid"


class CheckResult(BaseModel):
    requirement: str
    status: CheckStatus
    found_value: Optional[str] = None
    comment: str
    fix_recommendation: Optional[str] = None


class LayoutSuggestion(BaseModel):
    section: str
    issue: str
    suggestion: str


class ExtractedInvoiceData(BaseModel):
    """Structured data extracted from the invoice for preview display."""
    # Sender info
    sender_name: Optional[str] = None
    sender_address: Optional[str] = None
    sender_email: Optional[str] = None
    sender_phone: Optional[str] = None

    # Invoice details
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None

    # Recipient info
    recipient_email: Optional[str] = None
    recipient_company: Optional[str] = None
    recipient_address: Optional[str] = None

    # Line items
    service_description: Optional[str] = None
    quantity: Optional[str] = None
    unit_price: Optional[str] = None
    total_amount: Optional[str] = None
    currency: Optional[str] = None

    # Notes section (critical info)
    creator_name: Optional[str] = None
    artist_name: Optional[str] = None
    birth_date: Optional[str] = None
    tax_number: Optional[str] = None
    tax_country: Optional[str] = None
    vat_status: Optional[str] = None

    # Bank transfer specific
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    account_holder: Optional[str] = None


class ValidationResult(BaseModel):
    overall_status: OverallStatus
    invoice_type: InvoiceType
    checks: List[CheckResult]
    missing_items: List[str]
    warnings: List[str]
    layout_suggestions: List[LayoutSuggestion]
    summary: str
    extracted_data: Optional[ExtractedInvoiceData] = None


class AnalyzeRequest(BaseModel):
    invoice_type: InvoiceType = InvoiceType.PAYPAL


class InvoicePayload(BaseModel):
    """Payload for Copilot Agent Flow JSON file transfer."""
    contentBytes: str = ""  # Base64-encoded PDF content (optional if contentUrl is provided)
    contentUrl: Optional[str] = None  # URL to download the PDF from (e.g. Copilot Studio attachment URL)
    name: str = "invoice.pdf"  # Filename
    invoice_type: InvoiceType = InvoiceType.PAYPAL
    language: Language = Language.ENGLISH
