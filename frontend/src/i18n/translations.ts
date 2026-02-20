import type { Language } from "../types/invoice";

export const translations = {
  da: {
    // Header
    appTitle: "Invoice Checker",
    appSubtitle: "Sunday ApS",

    // Payment method section
    paymentMethod: "Betalingsmetode",
    selectPaymentType: "Vælg betalingstype",
    paypal: "PayPal",
    bankTransfer: "Bankoverførsel",
    paypalRequirements: "Kræver fødselsdato & skattenummer",
    bankRequirements: "Kræver IBAN & SWIFT/BIC",

    // Upload section
    uploadInvoice: "Upload faktura",
    orInvoiceLink: "eller indsæt PayPal faktura-link",
    invoiceLinkPlaceholder: "https://www.paypal.com/invoice/payerView/details/INV2-...",
    analyzeAs: "Analyser som",
    analyzing: "Analyserer...",
    analyzingUrl: "Henter og analyserer faktura fra link...",
    reset: "Nulstil",

    // Results
    results: "Resultat",
    validationChecks: "Valideringstjek",
    missingItems: "Manglende elementer",
    warnings: "Advarsler",
    issues: "Problemer",
    layoutSuggestions: "Layout-forslag",
    summary: "Opsummering",

    // Status
    approved: "Godkendt",
    missingInformation: "Manglende information",
    invalid: "Ugyldig",

    // Check status
    present: "Til stede",
    missing: "Mangler",
    unclear: "Uklar",

    // Errors
    errorOccurred: "Der opstod en fejl",

    // Footer
    footerText: "Invoice Checker bruger AI til at validere fakturaer mod Sunday's krav.",
    footerDisclaimer: "Resultaterne er vejledende og erstatter ikke professionel revision.",

    // Layout suggestions
    section: "Sektion",
    issue: "Problem",
    suggestion: "Forslag",

  },
  en: {
    // Header
    appTitle: "Invoice Checker",
    appSubtitle: "Sunday ApS",

    // Payment method section
    paymentMethod: "Payment Method",
    selectPaymentType: "Select payment type",
    paypal: "PayPal",
    bankTransfer: "Bank Transfer",
    paypalRequirements: "Requires date of birth & tax number",
    bankRequirements: "Requires IBAN & SWIFT/BIC",

    // Upload section
    uploadInvoice: "Upload Invoice",
    orInvoiceLink: "or paste PayPal invoice link",
    invoiceLinkPlaceholder: "https://www.paypal.com/invoice/payerView/details/INV2-...",
    analyzeAs: "Analyze as",
    analyzing: "Analyzing...",
    analyzingUrl: "Fetching and analyzing invoice from link...",
    reset: "Reset",

    // Results
    results: "Results",
    validationChecks: "Validation Checks",
    missingItems: "Missing Items",
    warnings: "Warnings",
    issues: "Issues",
    layoutSuggestions: "Layout Suggestions",
    summary: "Summary",

    // Status
    approved: "Approved",
    missingInformation: "Missing Information",
    invalid: "Invalid",

    // Check status
    present: "Present",
    missing: "Missing",
    unclear: "Unclear",

    // Errors
    errorOccurred: "An error occurred",

    // Footer
    footerText: "Invoice Checker uses AI to validate invoices against Sunday's requirements.",
    footerDisclaimer: "Results are advisory and do not replace professional audit.",

    // Layout suggestions
    section: "Section",
    issue: "Issue",
    suggestion: "Suggestion",

  },
} as const;

export type TranslationKey = keyof typeof translations.da;

export function t(language: Language, key: TranslationKey): string {
  return translations[language][key];
}
