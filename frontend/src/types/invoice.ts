export type CheckStatus = "present" | "missing" | "unclear";
export type OverallStatus = "approved" | "missing_information" | "invalid";
export type InvoiceType = "paypal" | "bank_transfer";
export type Language = "da" | "en";

export interface CheckResult {
  requirement: string;
  status: CheckStatus;
  found_value: string | null;
  comment: string;
}

export interface LayoutSuggestion {
  section: string;
  issue: string;
  suggestion: string;
}

export interface ExtractedInvoiceData {
  // Sender info
  sender_name: string | null;
  sender_address: string | null;
  sender_email: string | null;
  sender_phone: string | null;

  // Invoice details
  invoice_number: string | null;
  invoice_date: string | null;
  due_date: string | null;

  // Recipient info
  recipient_email: string | null;
  recipient_company: string | null;
  recipient_address: string | null;

  // Line items
  service_description: string | null;
  quantity: string | null;
  unit_price: string | null;
  total_amount: string | null;
  currency: string | null;

  // Notes section (critical info)
  creator_name: string | null;
  artist_name: string | null;
  birth_date: string | null;
  tax_number: string | null;
  tax_country: string | null;
  vat_status: string | null;

  // Bank transfer specific
  bank_name: string | null;
  iban: string | null;
  swift_bic: string | null;
  account_holder: string | null;
}

export interface ValidationResult {
  overall_status: OverallStatus;
  invoice_type: InvoiceType;
  checks: CheckResult[];
  missing_items: string[];
  warnings: string[];
  layout_suggestions: LayoutSuggestion[];
  summary: string;
  extracted_data: ExtractedInvoiceData | null;
}
