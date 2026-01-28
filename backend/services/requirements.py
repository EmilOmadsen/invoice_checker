"""
Invoice requirements for Sunday ApS.

These requirements define what a valid invoice must contain
when submitted to The Label Sunday ApS.

Two invoice types are supported:
1. PayPal Invoice - for payments via PayPal
2. Bank Transfer Invoice - for payments via bank transfer
"""

from typing import Literal

InvoiceType = Literal["paypal", "bank_transfer"]

# Common requirements for all invoice types
COMMON_REQUIREMENTS = {
    "invoice_details": {
        "description": "Basic invoice information (mandatory for all invoices)",
        "items": [
            {
                "id": "invoice_number",
                "name": "Fakturanummer",
                "description": "A unique, sequential invoice number"
            },
            {
                "id": "invoice_date",
                "name": "Fakturadato",
                "description": "The date the invoice was issued"
            },
            {
                "id": "due_date",
                "name": "Forfaldsdato",
                "description": "Payment due date"
            },
            {
                "id": "amount",
                "name": "Beløb",
                "description": "The total amount to be paid"
            },
            {
                "id": "currency",
                "name": "Valuta",
                "description": "The currency of the invoice amount (EUR, SEK, DKK, etc.)"
            },
            {
                "id": "description",
                "name": "Beskrivelse af ydelse/varer",
                "description": "Clear description of what is being invoiced (e.g., 'TikTok promotion / 2 videos')"
            }
        ]
    },
    "seller_info": {
        "description": "Information about the invoice sender/seller",
        "items": [
            {
                "id": "seller_name",
                "name": "Afsenders fulde navn",
                "description": "Full legal name of the person/company sending the invoice"
            },
            {
                "id": "seller_address",
                "name": "Afsenders adresse",
                "description": "Complete address of the seller (street, city, country)"
            },
            {
                "id": "seller_phone",
                "name": "Telefonnummer",
                "description": "Contact phone number"
            },
            {
                "id": "seller_email",
                "name": "Email",
                "description": "Contact email address"
            }
        ]
    },
    "buyer_info": {
        "description": "Information about the buyer (Sunday)",
        "expected_values": {
            "buyer_name": ["The Label Sunday", "The Label Sunday ApS", "Sunday", "Sunday ApS"],
            "buyer_address": "Vognmagergade 7, 6., 1120 Copenhagen K, DENMARK"
        },
        "items": [
            {
                "id": "buyer_name",
                "name": "Modtager (Sunday)",
                "description": "Must be addressed to The Label Sunday or similar"
            },
            {
                "id": "buyer_address",
                "name": "Modtagers adresse",
                "description": "Sunday's address: Vognmagergade 7, 6., 1120 Copenhagen K"
            }
        ]
    }
}

# PayPal specific requirements
PAYPAL_REQUIREMENTS = {
    "description": "Additional requirements for PayPal invoices",
    "personal_info": {
        "description": "Personal/tax information required for PayPal payments",
        "items": [
            {
                "id": "birth_date",
                "name": "Fødselsdato",
                "description": "Date of birth of the invoice sender (format: YYYY-MM-DD or DD-MM-YYYY)"
            },
            {
                "id": "tax_number",
                "name": "Skattenummer (TIN/CPR/Personal tax number)",
                "description": "Tax identification number - can be CPR (Denmark), personnummer (Sweden), TIN, or similar"
            }
        ]
    }
}

# Bank Transfer specific requirements
BANK_TRANSFER_REQUIREMENTS = {
    "description": "Additional requirements for bank transfer invoices",
    "recipient_info": {
        "description": "Information about the payment recipient (the person being paid)",
        "items": [
            {
                "id": "recipient_name",
                "name": "Modtagers fulde navn",
                "description": "Full legal name of the person receiving payment"
            },
            {
                "id": "recipient_address",
                "name": "Modtagers adresse",
                "description": "Complete address including street, city, postal code, and country"
            },
            {
                "id": "birth_date",
                "name": "Fødselsdato",
                "description": "Date of birth of the recipient (required for foreign persons)"
            },
            {
                "id": "tax_number",
                "name": "TIN/Skattenummer",
                "description": "Tax Identification Number - CPR for Danes, TIN/NPWP/etc. for foreigners"
            }
        ]
    },
    "bank_details": {
        "description": "Bank account information required for transfers",
        "items": [
            {
                "id": "bank_name",
                "name": "Banknavn",
                "description": "Name of the recipient's bank"
            },
            {
                "id": "account_number_iban",
                "name": "Kontonummer/IBAN",
                "description": "Bank account number or IBAN for international transfers"
            },
            {
                "id": "swift_bic",
                "name": "SWIFT/BIC",
                "description": "SWIFT or BIC code for international transfers"
            }
        ]
    }
}


def get_requirements_for_type(invoice_type: InvoiceType) -> dict:
    """Get the complete requirements for a specific invoice type."""
    requirements = {
        "common": COMMON_REQUIREMENTS,
        "type_specific": PAYPAL_REQUIREMENTS if invoice_type == "paypal" else BANK_TRANSFER_REQUIREMENTS
    }
    return requirements


def get_requirements_as_text(invoice_type: InvoiceType = "paypal") -> str:
    """Convert requirements to a text format for the AI prompt."""
    lines = []

    # Invoice type header
    type_name = "PayPal" if invoice_type == "paypal" else "Bankoverførsel"
    lines.append(f"# FAKTURAKRAV FOR {type_name.upper()}")
    lines.append("")

    # Common requirements
    lines.append("## GRUNDLÆGGENDE FAKTURAINFORMATION (PÅKRÆVET)")
    lines.append("")

    # Invoice details
    lines.append("### Fakturaoplysninger:")
    for item in COMMON_REQUIREMENTS["invoice_details"]["items"]:
        lines.append(f"- **{item['name']}**: {item['description']}")
    lines.append("")

    # Seller info
    lines.append("### Afsenderoplysninger:")
    for item in COMMON_REQUIREMENTS["seller_info"]["items"]:
        lines.append(f"- **{item['name']}**: {item['description']}")
    lines.append("")

    # Buyer info
    lines.append("### Modtageroplysninger (Sunday):")
    for item in COMMON_REQUIREMENTS["buyer_info"]["items"]:
        lines.append(f"- **{item['name']}**: {item['description']}")
    expected = COMMON_REQUIREMENTS["buyer_info"]["expected_values"]
    lines.append(f"  - Forventede navne: {', '.join(expected['buyer_name'])}")
    lines.append(f"  - Forventet adresse: {expected['buyer_address']}")
    lines.append("")

    # Type-specific requirements
    if invoice_type == "paypal":
        lines.append("## PAYPAL-SPECIFIKKE KRAV (PÅKRÆVET)")
        lines.append("")
        lines.append("### Personlige oplysninger til skatteindberetning:")
        for item in PAYPAL_REQUIREMENTS["personal_info"]["items"]:
            lines.append(f"- **{item['name']}**: {item['description']}")
    else:
        lines.append("## BANKOVERFØRSELS-SPECIFIKKE KRAV (PÅKRÆVET)")
        lines.append("")
        lines.append("### Modtageroplysninger (den person der skal betales):")
        for item in BANK_TRANSFER_REQUIREMENTS["recipient_info"]["items"]:
            lines.append(f"- **{item['name']}**: {item['description']}")
        lines.append("")
        lines.append("### Bankoplysninger:")
        for item in BANK_TRANSFER_REQUIREMENTS["bank_details"]["items"]:
            lines.append(f"- **{item['name']}**: {item['description']}")

    return "\n".join(lines)


# Keep old function for backwards compatibility
INVOICE_REQUIREMENTS = {
    "paypal": get_requirements_for_type("paypal"),
    "bank_transfer": get_requirements_for_type("bank_transfer")
}
