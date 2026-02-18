import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
from models.schemas import ValidationResult, CheckResult, CheckStatus, OverallStatus, InvoiceType, Language, LayoutSuggestion, ExtractedInvoiceData
from .requirements import get_requirements_as_text

# Ensure .env is loaded
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


# Ideal PayPal invoice layout description
IDEAL_PAYPAL_LAYOUT = """
## IDEELT PAYPAL FAKTURA LAYOUT

En korrekt PayPal faktura skal have følgende struktur og sektioner:

### 1. HEADER (Øverst til højre)
- Titel: "FAKTURERING"
- Afsenders fulde navn (f.eks. "Linus Nordin")
- Komplet adresse med land (f.eks. "Vikingavägen, 194 68 UPPLANDS VÄSBY, SVERIGE")
- Telefonnummer
- Email-adresse

### 2. FAKTURAOPLYSNINGER (Venstre side)
- Faktura-nr.: [nummer]
- Fakturadato: [dato]
- Forfaldsdato: [dato]
- Valgfrit: QR-kode til betaling

### 3. MODTAGER SEKTION
- Overskrift: "SEND FAKTURA TIL"
- Email: info@thelabelsunday.com

### 4. LINJEPOSTER TABEL
- Kolonnehoveder: Nr., VARER OG BESKRIVELSE, ANTAL/TIMER, PRIS, BELØB
- Tydelig beskrivelse af ydelsen (f.eks. "Tiktok promotion / 2 videos")
- Subtotal
- SAMLET PRIS med valuta

### 5. BEMÆRKNINGER TIL KUNDEN (Valgfri sektion)
Denne sektion KAN indeholde (men er ikke påkrævet):
- Modtagers firmaoplysninger (The Label Sunday, adresse, email)
- Creator/Kunstner information med kunstnernavn i parentes (f.eks. "Creator: Linus Nordin (testosteronexxtren)")
- Fødselsdato (f.eks. "Date of birth: 2007-09-07")
- Skattenummer med landekode (f.eks. "Personal tax number (SE): 070907-2672")
- Momsstatus (f.eks. "Not VAT registered.")

### LAYOUT KRAV
- Professionelt og rent design
- Tydelig sektionsopdeling
- Konsistent typografi
- QR-kode anbefales men er ikke påkrævet
"""


def get_validation_prompt(invoice_text: str, invoice_type: InvoiceType, language: Language) -> str:
    """Generate the validation prompt for Claude based on invoice type and language."""
    requirements_text = get_requirements_as_text(invoice_type.value)

    if invoice_type == InvoiceType.PAYPAL:
        # PayPal invoice - no layout validation
        if language == Language.DANISH:
            return f"""Du er en fakturavalidator for The Label Sunday ApS.

Du skal analysere den uploadede faktura og verificere om den opfylder alle krav for en **PayPal**-faktura.

VIGTIGE REGLER:
- Gæt IKKE på manglende information
- Basér din vurdering UDELUKKENDE på den angivne fakturatekst
- Hvis noget ikke er tydeligt angivet, markér det som "missing" eller "unclear"
- Vær striks men fair i din vurdering
- Alle tekster skal være på DANSK
- VIGTIGT: Skattenummer/TIN kan være angivet på flere måder: "skattenummer", "tax number", "TIN", "CPR", "personnummer", "personal tax number", "social security number" osv. Alle disse opfylder kravet om skattenummer.
- VIGTIGT: Fremtidige datoer er acceptable - flager IKKE fakturadatoer i fremtiden som problemer.

## VIGTIGT: RETTELSESANBEFALINGER
For HVERT tjek der er "missing" eller "unclear", SKAL du give en specifik, handlingsrettet fix_recommendation der fortæller brugeren PRÆCIS hvad de skal skrive og hvor. Brug konkrete eksempler med korrekte værdier.

Eksempler på GODE fix_recommendation:
- "Tilføj modtagerens firmanavn 'The Label Sunday ApS' og adresse 'Vognmagergade 7, 6., 1120 Copenhagen K, Denmark' under en 'Send faktura til' sektion."
- "Tilføj din fødselsdato i bemærkninger, f.eks.: 'Fødselsdato: 1995-03-15'"
- "Tilføj dit skattenummer med landekode i bemærkninger, f.eks.: 'Skattenummer (SE): 123456-7890'"

Eksempler på DÅRLIGE fix_recommendation (for vage - GØR IKKE DETTE):
- "Tilføj venligst modtagers firma på fakturaen."
- "Ret eller tydeliggør skattenummeret."

## PÅKRÆVET OUTPUT FORMAT (KUN JSON)

Du SKAL svare med UDELUKKENDE valid JSON i dette præcise format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Navn på kravet",
      "status": "present" | "missing" | "unclear",
      "found_value": "Værdien fundet i fakturaen, eller null hvis ikke fundet",
      "comment": "Kort forklaring på dansk",
      "fix_recommendation": "Specifik, handlingsrettet instruktion med præcise værdier/eksempler på hvordan problemet løses. null hvis status er present."
    }}
  ],
  "missing_items": ["Liste over manglende eller ugyldige felter"],
  "warnings": ["Liste over uklare eller potentielt problematiske elementer"],
  "layout_suggestions": [],
  "summary": "En kort menneskelæselig konklusion på dansk",
  "extracted_data": {{
    "sender_name": "Afsenders fulde navn eller null",
    "sender_address": "Afsenders adresse eller null",
    "sender_email": "Afsenders email eller null",
    "sender_phone": "Afsenders telefon eller null",
    "invoice_number": "Fakturanummer eller null",
    "invoice_date": "Fakturadato eller null",
    "due_date": "Forfaldsdato eller null",
    "recipient_email": "Modtagers email eller null",
    "recipient_company": "Modtagers firmanavn eller null",
    "recipient_address": "Modtagers adresse eller null",
    "service_description": "Beskrivelse af ydelsen eller null",
    "quantity": "Antal eller null",
    "unit_price": "Enhedspris eller null",
    "total_amount": "Totalbeløb eller null",
    "currency": "Valuta (f.eks. EUR, DKK) eller null",
    "creator_name": "Creator/kunstner navn eller null",
    "artist_name": "Kunstnernavn/handle i parentes eller null",
    "birth_date": "Fødselsdato eller null",
    "tax_number": "Skattenummer uden landekode eller null",
    "tax_country": "Landekode for skat (f.eks. SE, DK) eller null",
    "vat_status": "Momsstatus eller null"
  }}
}}

## STATUS DEFINITIONER
- "approved": Alle påkrævede felter er til stede og gyldige
- "missing_information": Nogle påkrævede felter mangler, men fakturaen er ellers gyldig
- "invalid": Kritiske problemer fundet (forkert køber, inkonsistente data, etc.)

## FAKTURAKRAV DER SKAL TJEKKES

{requirements_text}

## FAKTURATEKST TIL ANALYSE

{invoice_text}

---

Analysér nu fakturaen og svar med UDELUKKENDE JSON-resultatet. Inkludér ingen tekst før eller efter JSON."""

        else:  # English
            return f"""You are an invoice validator for The Label Sunday ApS.

You need to analyze the uploaded invoice and verify if it meets all requirements for a **PayPal** invoice.

IMPORTANT RULES:
- Do NOT guess missing information
- Base your evaluation STRICTLY on the provided invoice text
- If something is not clearly stated, mark it as "missing" or "unclear"
- Be strict but fair in your evaluation
- All text responses must be in ENGLISH
- IMPORTANT: Tax number/TIN can be indicated in various ways: "skattenummer", "tax number", "TIN", "CPR", "personnummer", "personal tax number", "social security number", etc. All of these fulfill the tax number requirement.
- IMPORTANT: Future dates are acceptable - do NOT flag invoice dates in the future as issues.

## CRITICAL: FIX RECOMMENDATIONS
For EVERY check that is "missing" or "unclear", you MUST provide a specific, actionable fix_recommendation that tells the creator EXACTLY what to write and where. Use concrete examples with correct values.

Examples of GOOD fix_recommendation:
- "Add the recipient company name 'The Label Sunday ApS' and address 'Vognmagergade 7, 6., 1120 Copenhagen K, Denmark' to the invoice under a 'Bill To' or 'Send Invoice To' section."
- "Add your date of birth in the Notes section, e.g.: 'Date of birth: 1995-03-15'"
- "Add your tax identification number with country code in the Notes section, e.g.: 'Personal tax number (SE): 123456-7890'"
- "Add the recipient email 'info@thelabelsunday.com' in the 'Send Invoice To' field."
- "The invoice is missing a service description. Add a clear description of the work, e.g.: 'TikTok promotion / 2 videos for @brandname'"

Examples of BAD fix_recommendation (too vague - DO NOT do this):
- "Please add recipient company to the invoice."
- "Please correct or clarify the tax number."
- "Add the missing information."

## REQUIRED OUTPUT FORMAT (JSON ONLY)

You MUST respond with ONLY valid JSON in this exact format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Name of the requirement",
      "status": "present" | "missing" | "unclear",
      "found_value": "The value found in the invoice, or null if not found",
      "comment": "Brief explanation in English",
      "fix_recommendation": "Specific, actionable instruction with exact values/examples on how to fix this issue. null if status is present."
    }}
  ],
  "missing_items": ["List of missing or invalid fields"],
  "warnings": ["List of unclear or potentially problematic items"],
  "layout_suggestions": [],
  "summary": "A short human-readable conclusion in English",
  "extracted_data": {{
    "sender_name": "Sender's full name or null",
    "sender_address": "Sender's address or null",
    "sender_email": "Sender's email or null",
    "sender_phone": "Sender's phone or null",
    "invoice_number": "Invoice number or null",
    "invoice_date": "Invoice date or null",
    "due_date": "Due date or null",
    "recipient_email": "Recipient's email or null",
    "recipient_company": "Recipient's company name or null",
    "recipient_address": "Recipient's address or null",
    "service_description": "Description of service or null",
    "quantity": "Quantity or null",
    "unit_price": "Unit price or null",
    "total_amount": "Total amount or null",
    "currency": "Currency (e.g. EUR, DKK) or null",
    "creator_name": "Creator/artist name or null",
    "artist_name": "Artist name/handle in parentheses or null",
    "birth_date": "Date of birth or null",
    "tax_number": "Tax number without country code or null",
    "tax_country": "Tax country code (e.g. SE, DK) or null",
    "vat_status": "VAT status or null"
  }}
}}

## STATUS DEFINITIONS
- "approved": All mandatory fields are present and valid
- "missing_information": Some required fields are missing but invoice is otherwise valid
- "invalid": Critical issues found (wrong buyer, inconsistent data, etc.)

## INVOICE REQUIREMENTS TO CHECK

{requirements_text}

## INVOICE TEXT TO ANALYZE

{invoice_text}

---

Now analyze the invoice and respond with ONLY the JSON result. Do not include any text before or after the JSON."""

    else:
        # Bank transfer invoice - no layout validation
        if language == Language.DANISH:
            return f"""Du er en fakturavalidator for The Label Sunday ApS.

Du skal analysere den uploadede faktura/betalingsanmodning og verificere om den opfylder alle krav for en **Bankoverførsel**.

## VIGTIG KONTEKST FOR BANKOVERFØRSLER
For bankoverførsler er betalingsmodtageren (den person der skal have pengene) OGSÅ fakturaafsenderen.
Der er INGEN separat "afsender/seller" information påkrævet - betalingsmodtagerens oplysninger erstatter dette.

## PÅKRÆVEDE FELTER FOR BANKOVERFØRSEL
1. **Dato** - En dato for dokumentet (kan være "Date", "Dato", "Payment Request Date" eller lignende)
2. **Beskrivelse af ydelse** - Hvad der betales for
3. **Beløb og valuta** - Totalbeløb med valuta
4. **Modtager (Sunday)** - The Label Sunday's navn og adresse
5. **Betalingsmodtager info** - Følgende felter skal tjekkes SEPARAT:
   - Navn (fulde navn)
   - Adresse (gadeadresse) - tjek som SEPARAT felt
   - Postnummer + by - tjek som SEPARAT felt
   - Land
   - Fødselsdato (for udlændinge)
   - TIN/skattenummer
6. **Bankoplysninger** - Banknavn, kontonummer/IBAN, SWIFT/BIC

## IKKE PÅKRÆVET FOR BANKOVERFØRSEL
- Fakturanummer (nice to have, men ikke påkrævet)
- Forfaldsdato (nice to have, men ikke påkrævet)
- Separat afsender/seller info (betalingsmodtageren ER afsenderen)
- Telefonnummer og email (nice to have, men ikke påkrævet)

VIGTIGE REGLER:
- Gæt IKKE på manglende information
- Basér din vurdering UDELUKKENDE på den angivne fakturatekst
- Vær fair i din vurdering - hvis alle PÅKRÆVEDE felter er til stede, skal status være "approved"
- Alle tekster skal være på DANSK
- VIGTIGT: Adresse og Postnummer+by er TO SEPARATE felter. Hvis et af dem mangler, skal det rapporteres som et separat manglende felt i missing_items og checks.

## VIGTIGT: RETTELSESANBEFALINGER
For HVERT tjek der er "missing" eller "unclear", SKAL du give en specifik, handlingsrettet fix_recommendation der fortæller brugeren PRÆCIS hvad de skal skrive og hvor. Brug konkrete eksempler med korrekte værdier.

Eksempler på GODE fix_recommendation:
- "Tilføj 'The Label Sunday ApS, Vognmagergade 7, 6., 1120 Copenhagen K, Denmark' som modtager/køber på fakturaen."
- "Tilføj din fulde gadeadresse (f.eks.: 'Storgatan 123') i betalingsmodtager-sektionen."
- "Tilføj din banks SWIFT/BIC-kode (f.eks.: 'NDEASESS') ved siden af dit IBAN-nummer."

Eksempler på DÅRLIGE fix_recommendation (for vage - GØR IKKE DETTE):
- "Tilføj venligst modtagers adresse."
- "Tilføj bankoplysninger til fakturaen."

## PÅKRÆVET OUTPUT FORMAT (KUN JSON)

Du SKAL svare med UDELUKKENDE valid JSON i dette præcise format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Navn på kravet",
      "status": "present" | "missing" | "unclear",
      "found_value": "Værdien fundet i fakturaen, eller null hvis ikke fundet",
      "comment": "Kort forklaring på dansk",
      "fix_recommendation": "Specifik, handlingsrettet instruktion med præcise værdier/eksempler på hvordan problemet løses. null hvis status er present."
    }}
  ],
  "missing_items": ["Liste over manglende PÅKRÆVEDE felter - ignorer valgfrie felter"],
  "warnings": ["Liste over uklare eller potentielt problematiske elementer"],
  "layout_suggestions": [],
  "summary": "En kort menneskelæselig konklusion på dansk"
}}

## STATUS DEFINITIONER
- "approved": Alle PÅKRÆVEDE felter er til stede og gyldige (ignorer valgfrie felter som fakturanummer, forfaldsdato, telefon, email)
- "missing_information": Nogle PÅKRÆVEDE felter mangler (dato, beløb, beskrivelse, Sunday info, betalingsmodtager info, bankoplysninger)
- "invalid": Kritiske problemer fundet (forkert køber, inkonsistente data, etc.)

## FAKTURATEKST TIL ANALYSE

{invoice_text}

---

Analysér nu fakturaen og svar med UDELUKKENDE JSON-resultatet. Inkludér ingen tekst før eller efter JSON."""

        else:  # English
            return f"""You are an invoice validator for The Label Sunday ApS.

You need to analyze the uploaded invoice/payment request and verify if it meets all requirements for a **Bank Transfer**.

## IMPORTANT CONTEXT FOR BANK TRANSFERS
For bank transfers, the payment recipient (the person receiving the money) IS ALSO the invoice sender.
There is NO separate "sender/seller" information required - the payment recipient's info replaces this.

## REQUIRED FIELDS FOR BANK TRANSFER
1. **Date** - A date for the document (can be "Date", "Payment Request Date" or similar)
2. **Service description** - What is being paid for
3. **Amount and currency** - Total amount with currency
4. **Recipient (Sunday)** - The Label Sunday's name and address
5. **Payment recipient info** - The following fields must be checked SEPARATELY:
   - Name (full name)
   - Address (street address) - check as SEPARATE field
   - Postal code + city - check as SEPARATE field
   - Country
   - Birth date (for foreigners)
   - TIN/tax number
6. **Bank details** - Bank name, account number/IBAN, SWIFT/BIC

## NOT REQUIRED FOR BANK TRANSFER
- Invoice number (nice to have, but not required)
- Due date (nice to have, but not required)
- Separate sender/seller info (the payment recipient IS the sender)
- Phone number and email (nice to have, but not required)

IMPORTANT RULES:
- Do NOT guess missing information
- Base your evaluation STRICTLY on the provided invoice text
- Be fair in your evaluation - if all REQUIRED fields are present, status should be "approved"
- All text responses must be in ENGLISH
- IMPORTANT: Address and Postal code+city are TWO SEPARATE fields. If one is missing, it should be reported as a separate missing item in missing_items and checks.

## CRITICAL: FIX RECOMMENDATIONS
For EVERY check that is "missing" or "unclear", you MUST provide a specific, actionable fix_recommendation that tells the creator EXACTLY what to write and where. Use concrete examples with correct values.

Examples of GOOD fix_recommendation:
- "Add 'The Label Sunday ApS, Vognmagergade 7, 6., 1120 Copenhagen K, Denmark' as the recipient/buyer on the invoice."
- "Add your full street address (e.g.: '123 Main Street') in the payment recipient section."
- "Add your bank's SWIFT/BIC code (e.g.: 'NDEASESS') next to your IBAN number."
- "Add your date of birth, e.g.: 'Date of birth: 1995-03-15'"

Examples of BAD fix_recommendation (too vague - DO NOT do this):
- "Please add the recipient address."
- "Add bank details to the invoice."

## REQUIRED OUTPUT FORMAT (JSON ONLY)

You MUST respond with ONLY valid JSON in this exact format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Name of the requirement",
      "status": "present" | "missing" | "unclear",
      "found_value": "The value found in the invoice, or null if not found",
      "comment": "Brief explanation in English",
      "fix_recommendation": "Specific, actionable instruction with exact values/examples on how to fix this issue. null if status is present."
    }}
  ],
  "missing_items": ["List of missing REQUIRED fields - ignore optional fields"],
  "warnings": ["List of unclear or potentially problematic items"],
  "layout_suggestions": [],
  "summary": "A short human-readable conclusion in English"
}}

## STATUS DEFINITIONS
- "approved": All REQUIRED fields are present and valid (ignore optional fields like invoice number, due date, phone, email)
- "missing_information": Some REQUIRED fields are missing (date, amount, description, Sunday info, payment recipient info, bank details)
- "invalid": Critical issues found (wrong buyer, inconsistent data, etc.)

## INVOICE TEXT TO ANALYZE

{invoice_text}

---

Now analyze the invoice and respond with ONLY the JSON result. Do not include any text before or after the JSON."""


async def validate_invoice(invoice_text: str, invoice_type: InvoiceType, language: Language = Language.DANISH) -> ValidationResult:
    """
    Validate an invoice using Claude AI.

    Args:
        invoice_text: Extracted text from the invoice
        invoice_type: Type of invoice (paypal or bank_transfer)
        language: Language for responses (da or en)

    Returns:
        ValidationResult with all check results
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    client = Anthropic(api_key=api_key)

    prompt = get_validation_prompt(invoice_text, invoice_type, language)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the response text
    response_text = message.content[0].text

    # Parse the JSON response
    try:
        # Try to extract JSON from the response (in case there's extra text)
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result_dict = json.loads(json_str)
        else:
            raise ValueError("No JSON object found in response")
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return an error result
        error_msg = "Der opstod en fejl ved analyse af fakturaen. Prøv igen." if language == Language.DANISH else "An error occurred while analyzing the invoice. Please try again."
        return ValidationResult(
            overall_status=OverallStatus.INVALID,
            invoice_type=invoice_type,
            checks=[],
            missing_items=[],
            warnings=[f"Failed to parse AI response: {str(e)}"],
            layout_suggestions=[],
            summary=error_msg
        )

    # Convert to Pydantic model
    checks = [
        CheckResult(
            requirement=check["requirement"],
            status=CheckStatus(check["status"]),
            found_value=check.get("found_value"),
            comment=check["comment"],
            fix_recommendation=check.get("fix_recommendation")
        )
        for check in result_dict.get("checks", [])
    ]

    layout_suggestions = [
        LayoutSuggestion(
            section=suggestion["section"],
            issue=suggestion["issue"],
            suggestion=suggestion["suggestion"]
        )
        for suggestion in result_dict.get("layout_suggestions", [])
    ]

    # Parse extracted data if present
    extracted_data = None
    if "extracted_data" in result_dict and result_dict["extracted_data"]:
        extracted_data = ExtractedInvoiceData(**result_dict["extracted_data"])

    return ValidationResult(
        overall_status=OverallStatus(result_dict["overall_status"]),
        invoice_type=invoice_type,
        checks=checks,
        missing_items=result_dict.get("missing_items", []),
        warnings=result_dict.get("warnings", []),
        layout_suggestions=layout_suggestions,
        summary=result_dict.get("summary", ""),
        extracted_data=extracted_data
    )


def get_vision_validation_prompt(invoice_type: InvoiceType, language: Language) -> str:
    """Generate the validation prompt for image-based invoice analysis."""
    requirements_text = get_requirements_as_text(invoice_type.value)

    # For PayPal invoices
    if invoice_type == InvoiceType.PAYPAL:
        if language == Language.DANISH:
            return f"""Du er en fakturavalidator for The Label Sunday ApS.

Du skal analysere det uploadede fakturabillede og verificere om den opfylder alle krav for en **PayPal**-faktura.

VIGTIGE REGLER:
- Læs al tekst fra billedet omhyggeligt
- Gæt IKKE på manglende information
- Hvis noget ikke er tydeligt synligt, markér det som "missing" eller "unclear"
- Vær striks men fair i din vurdering
- Alle tekster skal være på DANSK
- VIGTIGT: Skattenummer/TIN kan være angivet på flere måder: "skattenummer", "tax number", "TIN", "CPR", "personnummer", "personal tax number", "social security number" osv. Alle disse opfylder kravet om skattenummer.
- VIGTIGT: Fremtidige datoer er acceptable - flager IKKE fakturadatoer i fremtiden som problemer.

## VIGTIGT: RETTELSESANBEFALINGER
For HVERT tjek der er "missing" eller "unclear", SKAL du give en specifik, handlingsrettet fix_recommendation der fortæller brugeren PRÆCIS hvad de skal skrive og hvor. Brug konkrete eksempler med korrekte værdier.

## PÅKRÆVET OUTPUT FORMAT (KUN JSON)

Du SKAL svare med UDELUKKENDE valid JSON i dette præcise format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Navn på kravet",
      "status": "present" | "missing" | "unclear",
      "found_value": "Værdien fundet i fakturaen, eller null hvis ikke fundet",
      "comment": "Kort forklaring på dansk",
      "fix_recommendation": "Specifik, handlingsrettet instruktion med præcise værdier/eksempler. null hvis status er present."
    }}
  ],
  "missing_items": ["Liste over manglende eller ugyldige felter"],
  "warnings": ["Liste over uklare eller potentielt problematiske elementer"],
  "layout_suggestions": [],
  "summary": "En kort menneskelæselig konklusion på dansk",
  "extracted_data": {{
    "sender_name": "Afsenders fulde navn eller null",
    "sender_address": "Afsenders adresse eller null",
    "sender_email": "Afsenders email eller null",
    "sender_phone": "Afsenders telefon eller null",
    "invoice_number": "Fakturanummer eller null",
    "invoice_date": "Fakturadato eller null",
    "due_date": "Forfaldsdato eller null",
    "recipient_email": "Modtagers email eller null",
    "recipient_company": "Modtagers firmanavn eller null",
    "recipient_address": "Modtagers adresse eller null",
    "service_description": "Beskrivelse af ydelsen eller null",
    "quantity": "Antal eller null",
    "unit_price": "Enhedspris eller null",
    "total_amount": "Totalbeløb eller null",
    "currency": "Valuta (f.eks. EUR, DKK) eller null",
    "creator_name": "Creator/kunstner navn eller null",
    "artist_name": "Kunstnernavn/handle i parentes eller null",
    "birth_date": "Fødselsdato eller null",
    "tax_number": "Skattenummer uden landekode eller null",
    "tax_country": "Landekode for skat (f.eks. SE, DK) eller null",
    "vat_status": "Momsstatus eller null"
  }}
}}

## FAKTURAKRAV DER SKAL TJEKKES

{requirements_text}

Analysér nu fakturabilledet og svar med UDELUKKENDE JSON-resultatet."""

        else:  # English for PayPal
            return f"""You are an invoice validator for The Label Sunday ApS.

You need to analyze the uploaded invoice image and verify if it meets all requirements for a **PayPal** invoice.

IMPORTANT RULES:
- Read all text from the image carefully
- Do NOT guess missing information
- If something is not clearly visible, mark it as "missing" or "unclear"
- Be strict but fair in your evaluation
- All text responses must be in ENGLISH
- IMPORTANT: Tax number/TIN can be indicated in various ways: "skattenummer", "tax number", "TIN", "CPR", "personnummer", "personal tax number", "social security number", etc. All of these fulfill the tax number requirement.
- IMPORTANT: Future dates are acceptable - do NOT flag invoice dates in the future as issues.

## CRITICAL: FIX RECOMMENDATIONS
For EVERY check that is "missing" or "unclear", you MUST provide a specific, actionable fix_recommendation that tells the creator EXACTLY what to write and where. Use concrete examples with correct values.

## REQUIRED OUTPUT FORMAT (JSON ONLY)

You MUST respond with ONLY valid JSON in this exact format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Name of the requirement",
      "status": "present" | "missing" | "unclear",
      "found_value": "The value found in the invoice, or null if not found",
      "comment": "Brief explanation in English",
      "fix_recommendation": "Specific, actionable instruction with exact values/examples on how to fix this. null if status is present."
    }}
  ],
  "missing_items": ["List of missing or invalid fields"],
  "warnings": ["List of unclear or potentially problematic items"],
  "layout_suggestions": [],
  "summary": "A short human-readable conclusion in English",
  "extracted_data": {{
    "sender_name": "Sender's full name or null",
    "sender_address": "Sender's address or null",
    "sender_email": "Sender's email or null",
    "sender_phone": "Sender's phone or null",
    "invoice_number": "Invoice number or null",
    "invoice_date": "Invoice date or null",
    "due_date": "Due date or null",
    "recipient_email": "Recipient's email or null",
    "recipient_company": "Recipient's company name or null",
    "recipient_address": "Recipient's address or null",
    "service_description": "Description of service or null",
    "quantity": "Quantity or null",
    "unit_price": "Unit price or null",
    "total_amount": "Total amount or null",
    "currency": "Currency (e.g. EUR, DKK) or null",
    "creator_name": "Creator/artist name or null",
    "artist_name": "Artist name/handle in parentheses or null",
    "birth_date": "Date of birth or null",
    "tax_number": "Tax number without country code or null",
    "tax_country": "Tax country code (e.g. SE, DK) or null",
    "vat_status": "VAT status or null"
  }}
}}

## INVOICE REQUIREMENTS TO CHECK

{requirements_text}

Now analyze the invoice image and respond with ONLY the JSON result."""

    # For Bank Transfer invoices
    else:
        if language == Language.DANISH:
            return f"""Du er en fakturavalidator for The Label Sunday ApS.

Du skal analysere det uploadede faktura/betalingsanmodning-billede og verificere om den opfylder alle krav for en **Bankoverførsel**.

## VIGTIG KONTEKST FOR BANKOVERFØRSLER
For bankoverførsler er betalingsmodtageren (den person der skal have pengene) OGSÅ fakturaafsenderen.
Der er INGEN separat "afsender/seller" information påkrævet - betalingsmodtagerens oplysninger erstatter dette.

## PÅKRÆVEDE FELTER FOR BANKOVERFØRSEL
1. **Dato** - En dato for dokumentet (kan være "Date", "Dato", "Payment Request Date" eller lignende)
2. **Beskrivelse af ydelse** - Hvad der betales for
3. **Beløb og valuta** - Totalbeløb med valuta
4. **Modtager (Sunday)** - The Label Sunday's navn og adresse
5. **Betalingsmodtager info** - Følgende felter skal tjekkes SEPARAT:
   - Navn (fulde navn)
   - Adresse (gadeadresse) - tjek som SEPARAT felt
   - Postnummer + by - tjek som SEPARAT felt
   - Land
   - Fødselsdato (for udlændinge)
   - TIN/skattenummer
6. **Bankoplysninger** - Banknavn, kontonummer/IBAN, SWIFT/BIC

## IKKE PÅKRÆVET FOR BANKOVERFØRSEL
- Fakturanummer (nice to have, men ikke påkrævet)
- Forfaldsdato (nice to have, men ikke påkrævet)
- Separat afsender/seller info (betalingsmodtageren ER afsenderen)
- Telefonnummer og email (nice to have, men ikke påkrævet)

VIGTIGE REGLER:
- Læs al tekst fra billedet omhyggeligt
- Gæt IKKE på manglende information
- Vær fair i din vurdering - hvis alle PÅKRÆVEDE felter er til stede, skal status være "approved"
- Alle tekster skal være på DANSK
- VIGTIGT: Adresse og Postnummer+by er TO SEPARATE felter. Hvis et af dem mangler, skal det rapporteres som et separat manglende felt i missing_items og checks.

## VIGTIGT: RETTELSESANBEFALINGER
For HVERT tjek der er "missing" eller "unclear", SKAL du give en specifik, handlingsrettet fix_recommendation der fortæller brugeren PRÆCIS hvad de skal skrive og hvor. Brug konkrete eksempler med korrekte værdier.

## PÅKRÆVET OUTPUT FORMAT (KUN JSON)

Du SKAL svare med UDELUKKENDE valid JSON i dette præcise format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Navn på kravet",
      "status": "present" | "missing" | "unclear",
      "found_value": "Værdien fundet i fakturaen, eller null hvis ikke fundet",
      "comment": "Kort forklaring på dansk",
      "fix_recommendation": "Specifik, handlingsrettet instruktion med præcise værdier/eksempler. null hvis status er present."
    }}
  ],
  "missing_items": ["Liste over manglende PÅKRÆVEDE felter - ignorer valgfrie felter"],
  "warnings": ["Liste over uklare eller potentielt problematiske elementer"],
  "layout_suggestions": [],
  "summary": "En kort menneskelæselig konklusion på dansk"
}}

## STATUS DEFINITIONER
- "approved": Alle PÅKRÆVEDE felter er til stede og gyldige (ignorer valgfrie felter som fakturanummer, forfaldsdato, telefon, email)
- "missing_information": Nogle PÅKRÆVEDE felter mangler (dato, beløb, beskrivelse, Sunday info, betalingsmodtager info, bankoplysninger)
- "invalid": Kritiske problemer fundet (forkert køber, inkonsistente data, etc.)

Analysér nu fakturabilledet og svar med UDELUKKENDE JSON-resultatet."""

        else:  # English for Bank Transfer
            return f"""You are an invoice validator for The Label Sunday ApS.

You need to analyze the uploaded invoice/payment request image and verify if it meets all requirements for a **Bank Transfer**.

## IMPORTANT CONTEXT FOR BANK TRANSFERS
For bank transfers, the payment recipient (the person receiving the money) IS ALSO the invoice sender.
There is NO separate "sender/seller" information required - the payment recipient's info replaces this.

## REQUIRED FIELDS FOR BANK TRANSFER
1. **Date** - A date for the document (can be "Date", "Payment Request Date" or similar)
2. **Service description** - What is being paid for
3. **Amount and currency** - Total amount with currency
4. **Recipient (Sunday)** - The Label Sunday's name and address
5. **Payment recipient info** - The following fields must be checked SEPARATELY:
   - Name (full name)
   - Address (street address) - check as SEPARATE field
   - Postal code + city - check as SEPARATE field
   - Country
   - Birth date (for foreigners)
   - TIN/tax number
6. **Bank details** - Bank name, account number/IBAN, SWIFT/BIC

## NOT REQUIRED FOR BANK TRANSFER
- Invoice number (nice to have, but not required)
- Due date (nice to have, but not required)
- Separate sender/seller info (the payment recipient IS the sender)
- Phone number and email (nice to have, but not required)

IMPORTANT RULES:
- Read all text from the image carefully
- Do NOT guess missing information
- Be fair in your evaluation - if all REQUIRED fields are present, status should be "approved"
- All text responses must be in ENGLISH
- IMPORTANT: Address and Postal code+city are TWO SEPARATE fields. If one is missing, it should be reported as a separate missing item in missing_items and checks.

## CRITICAL: FIX RECOMMENDATIONS
For EVERY check that is "missing" or "unclear", you MUST provide a specific, actionable fix_recommendation that tells the creator EXACTLY what to write and where. Use concrete examples with correct values.

## REQUIRED OUTPUT FORMAT (JSON ONLY)

You MUST respond with ONLY valid JSON in this exact format:

{{
  "overall_status": "approved" | "missing_information" | "invalid",
  "checks": [
    {{
      "requirement": "Name of the requirement",
      "status": "present" | "missing" | "unclear",
      "found_value": "The value found in the invoice, or null if not found",
      "comment": "Brief explanation in English",
      "fix_recommendation": "Specific, actionable instruction with exact values/examples on how to fix this. null if status is present."
    }}
  ],
  "missing_items": ["List of missing REQUIRED fields - ignore optional fields"],
  "warnings": ["List of unclear or potentially problematic items"],
  "layout_suggestions": [],
  "summary": "A short human-readable conclusion in English"
}}

## STATUS DEFINITIONS
- "approved": All REQUIRED fields are present and valid (ignore optional fields like invoice number, due date, phone, email)
- "missing_information": Some REQUIRED fields are missing (date, amount, description, Sunday info, payment recipient info, bank details)
- "invalid": Critical issues found (wrong buyer, inconsistent data, etc.)

Now analyze the invoice image and respond with ONLY the JSON result."""


async def validate_invoice_with_image(images_base64: list[str], invoice_type: InvoiceType, language: Language = Language.DANISH) -> ValidationResult:
    """
    Validate an invoice using Claude AI with vision capabilities.

    Args:
        images_base64: List of base64-encoded PNG images of the invoice pages
        invoice_type: Type of invoice (paypal or bank_transfer)
        language: Language for responses (da or en)

    Returns:
        ValidationResult with all check results
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    client = Anthropic(api_key=api_key)

    prompt = get_vision_validation_prompt(invoice_type, language)

    # Build content with images
    content = []
    for i, img_base64 in enumerate(images_base64):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img_base64
            }
        })

    content.append({
        "type": "text",
        "text": prompt
    })

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": content}
        ]
    )

    # Extract the response text
    response_text = message.content[0].text

    # Parse the JSON response
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result_dict = json.loads(json_str)
        else:
            raise ValueError("No JSON object found in response")
    except json.JSONDecodeError as e:
        error_msg = "Der opstod en fejl ved analyse af fakturaen. Prøv igen." if language == Language.DANISH else "An error occurred while analyzing the invoice. Please try again."
        return ValidationResult(
            overall_status=OverallStatus.INVALID,
            invoice_type=invoice_type,
            checks=[],
            missing_items=[],
            warnings=[f"Failed to parse AI response: {str(e)}"],
            layout_suggestions=[],
            summary=error_msg
        )

    # Convert to Pydantic model
    checks = [
        CheckResult(
            requirement=check["requirement"],
            status=CheckStatus(check["status"]),
            found_value=check.get("found_value"),
            comment=check["comment"],
            fix_recommendation=check.get("fix_recommendation")
        )
        for check in result_dict.get("checks", [])
    ]

    layout_suggestions = [
        LayoutSuggestion(
            section=suggestion["section"],
            issue=suggestion["issue"],
            suggestion=suggestion["suggestion"]
        )
        for suggestion in result_dict.get("layout_suggestions", [])
    ]

    # Parse extracted data if present
    extracted_data = None
    if "extracted_data" in result_dict and result_dict["extracted_data"]:
        extracted_data = ExtractedInvoiceData(**result_dict["extracted_data"])

    return ValidationResult(
        overall_status=OverallStatus(result_dict["overall_status"]),
        invoice_type=invoice_type,
        checks=checks,
        missing_items=result_dict.get("missing_items", []),
        warnings=result_dict.get("warnings", []),
        layout_suggestions=layout_suggestions,
        summary=result_dict.get("summary", ""),
        extracted_data=extracted_data
    )
