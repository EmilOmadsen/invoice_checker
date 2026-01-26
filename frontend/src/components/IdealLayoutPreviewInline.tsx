import type { Language, InvoiceType, ExtractedInvoiceData } from "../types/invoice";

interface IdealLayoutPreviewInlineProps {
  language: Language;
  invoiceType: InvoiceType;
  extractedData?: ExtractedInvoiceData | null;
}

// Helper component for displaying a field with missing highlight
function Field({
  value,
  placeholder,
  isRequired = false
}: {
  value: string | null;
  placeholder: string;
  isRequired?: boolean;
}) {
  const hasValue = value && value.trim() !== "";

  if (hasValue) {
    return <span className="text-gray-800 font-medium">{value}</span>;
  }

  return (
    <span className={`
      ${isRequired ? "bg-red-100 text-red-600 border border-red-300" : "bg-yellow-50 text-yellow-600 border border-yellow-200"}
      px-1 rounded text-[9px] italic
    `}>
      {placeholder}
    </span>
  );
}

export function IdealLayoutPreviewInline({ language, invoiceType, extractedData }: IdealLayoutPreviewInlineProps) {
  const hasData = extractedData !== null && extractedData !== undefined;

  const texts = {
    da: {
      title: hasData ? "Din Faktura i Korrekt Format" : "Ideelt Faktura Layout",
      subtitle: hasData ? "Røde felter mangler og skal udfyldes" : "Upload en faktura for at se dine data",
      header: "HEADER",
      headerDesc: "Øverst til højre",
      invoiceTitle: "FAKTURA",
      senderName: "Dit fulde navn",
      address: "Din adresse med land",
      phone: "Telefonnummer",
      email: "Email-adresse",
      invoiceDetails: "FAKTURAOPLYSNINGER",
      invoiceNo: "Faktura-nr.:",
      invoiceDate: "Fakturadato:",
      dueDate: "Forfaldsdato:",
      recipient: "MODTAGER",
      sendTo: "SEND FAKTURA TIL",
      lineItems: "LINJEPOSTER",
      columnHeaders: "BESKRIVELSE | ANTAL | PRIS | BELØB",
      serviceDesc: "Beskrivelse af ydelsen",
      total: "TOTAL",
      notes: "BEMÆRKNINGER",
      notesDesc: "Vigtig!",
      companyInfo: "Sunday's firmaoplysninger:",
      creatorLabel: "Creator:",
      birthDateLabel: "Fødselsdato:",
      taxNumberLabel: "Skattenummer",
      vatStatusLabel: "Momsstatus:",
      required: "Påkrævet",
      missing: "Mangler",
      bankInfo: "Bankoplysninger",
      bankName: "Bank:",
      iban: "IBAN:",
      swift: "SWIFT/BIC:",
      accountHolder: "Kontoindehaver:",
    },
    en: {
      title: hasData ? "Your Invoice in Correct Format" : "Ideal Invoice Layout",
      subtitle: hasData ? "Red fields are missing and must be filled" : "Upload an invoice to see your data",
      header: "HEADER",
      headerDesc: "Top right",
      invoiceTitle: "INVOICE",
      senderName: "Your full name",
      address: "Your address with country",
      phone: "Phone number",
      email: "Email address",
      invoiceDetails: "INVOICE DETAILS",
      invoiceNo: "Invoice no.:",
      invoiceDate: "Invoice date:",
      dueDate: "Due date:",
      recipient: "RECIPIENT",
      sendTo: "SEND INVOICE TO",
      lineItems: "LINE ITEMS",
      columnHeaders: "DESCRIPTION | QTY | PRICE | AMOUNT",
      serviceDesc: "Description of service",
      total: "TOTAL",
      notes: "NOTES",
      notesDesc: "Important!",
      companyInfo: "Sunday's company info:",
      creatorLabel: "Creator:",
      birthDateLabel: "Date of birth:",
      taxNumberLabel: "Tax number",
      vatStatusLabel: "VAT status:",
      required: "Required",
      missing: "Missing",
      bankInfo: "Bank Details",
      bankName: "Bank:",
      iban: "IBAN:",
      swift: "SWIFT/BIC:",
      accountHolder: "Account holder:",
    },
  };

  const t = texts[language];

  // Default placeholder values
  const placeholders = {
    da: {
      name: "Dit fulde navn",
      address: "Din adresse",
      email: "din@email.com",
      phone: "+XX XXX XXX",
      invoiceNo: "001",
      invoiceDate: "ÅÅÅÅ-MM-DD",
      dueDate: "ÅÅÅÅ-MM-DD",
      recipientEmail: "info@thelabelsunday.com",
      recipientCompany: "The Label Sunday",
      service: "Beskrivelse af ydelsen",
      qty: "1",
      price: "€XXX",
      total: "€XXX",
      creatorName: "Dit navn",
      artistName: "kunstnernavn",
      birthDate: "ÅÅÅÅ-MM-DD",
      taxNumber: "XXXXXX-XXXX",
      taxCountry: "XX",
      vatStatus: "Ikke momsregistreret",
      bankName: "Dit banknavn",
      iban: "XXXX XXXX XXXX XXXX",
      swift: "XXXXXXXX",
      accountHolder: "Dit navn",
    },
    en: {
      name: "Your full name",
      address: "Your address",
      email: "your@email.com",
      phone: "+XX XXX XXX",
      invoiceNo: "001",
      invoiceDate: "YYYY-MM-DD",
      dueDate: "YYYY-MM-DD",
      recipientEmail: "info@thelabelsunday.com",
      recipientCompany: "The Label Sunday",
      service: "Description of service",
      qty: "1",
      price: "€XXX",
      total: "€XXX",
      creatorName: "Your name",
      artistName: "artist name",
      birthDate: "YYYY-MM-DD",
      taxNumber: "XXXXXX-XXXX",
      taxCountry: "XX",
      vatStatus: "Not VAT registered",
      bankName: "Your bank name",
      iban: "XXXX XXXX XXXX XXXX",
      swift: "XXXXXXXX",
      accountHolder: "Your name",
    },
  };

  const p = placeholders[language];

  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">{t.title}</h2>
        <p className="text-xs text-gray-500">{t.subtitle}</p>
      </div>

      {/* Invoice Preview */}
      <div className="border border-gray-200 rounded-lg bg-white shadow-sm overflow-hidden">
        <div className="p-4 space-y-3 text-xs">

          {/* Top Section - Header and Invoice Details */}
          <div className="flex justify-between gap-3">
            {/* Left - Invoice Details */}
            <div className="flex-1">
              <div className="border-2 border-dashed border-blue-300 rounded p-2 bg-blue-50">
                <p className="font-bold text-blue-800 text-[10px] mb-1">{t.invoiceDetails}</p>
                <div className="text-gray-600 space-y-0.5 text-[10px]">
                  <p>{t.invoiceNo} <Field value={extractedData?.invoice_number ?? null} placeholder={p.invoiceNo} /></p>
                  <p>{t.invoiceDate} <Field value={extractedData?.invoice_date ?? null} placeholder={p.invoiceDate} isRequired /></p>
                  <p>{t.dueDate} <Field value={extractedData?.due_date ?? null} placeholder={p.dueDate} /></p>
                </div>
              </div>
            </div>

            {/* Right - Header/Sender Info */}
            <div className="flex-1 text-right">
              <div className="border-2 border-dashed border-green-300 rounded p-2 bg-green-50">
                <p className="text-sm font-bold text-gray-800 mb-1">{t.invoiceTitle}</p>
                <div className="text-[10px] text-gray-600 space-y-0.5">
                  <p><Field value={extractedData?.sender_name ?? null} placeholder={p.name} isRequired /></p>
                  <p><Field value={extractedData?.sender_address ?? null} placeholder={p.address} isRequired /></p>
                  <p><Field value={extractedData?.sender_email ?? null} placeholder={p.email} /></p>
                </div>
              </div>
            </div>
          </div>

          {/* Recipient Section */}
          <div className="border-2 border-dashed border-purple-300 rounded p-2 bg-purple-50">
            <p className="font-bold text-purple-800 text-[10px] mb-1">{t.sendTo}</p>
            <p className="text-[10px] text-gray-600">
              <Field value={extractedData?.recipient_email ?? null} placeholder={p.recipientEmail} isRequired />
            </p>
            <p className="text-[10px] text-gray-500">
              <Field value={extractedData?.recipient_company ?? null} placeholder={p.recipientCompany} />
            </p>
          </div>

          {/* Line Items Table */}
          <div className="border-2 border-dashed border-orange-300 rounded p-2 bg-orange-50">
            <p className="font-bold text-orange-800 text-[10px] mb-1">{t.lineItems}</p>
            <div className="bg-white rounded border border-gray-200 overflow-hidden text-[10px]">
              <div className="bg-gray-100 px-2 py-1 font-medium text-gray-600">
                {t.columnHeaders}
              </div>
              <div className="px-2 py-1 text-gray-600 border-t border-gray-200">
                <Field value={extractedData?.service_description ?? null} placeholder={p.service} isRequired /> | {" "}
                <Field value={extractedData?.quantity ?? null} placeholder={p.qty} /> | {" "}
                <Field value={extractedData?.unit_price ?? null} placeholder={p.price} /> | {" "}
                <Field value={extractedData?.total_amount ?? null} placeholder={p.total} isRequired />
              </div>
              <div className="px-2 py-1 border-t border-gray-200 flex justify-between font-bold bg-gray-50">
                <span>{t.total}</span>
                <span>
                  <Field value={extractedData?.total_amount ?? null} placeholder={p.total} isRequired />
                  {" "}
                  <Field value={extractedData?.currency ?? null} placeholder="EUR" />
                </span>
              </div>
            </div>
          </div>

          {/* Notes Section - Critical */}
          <div className="border-2 border-dashed border-red-300 rounded p-2 bg-red-50">
            <div className="flex items-center gap-1 mb-1">
              <p className="font-bold text-red-800 text-[10px]">{t.notes}</p>
              <span className="bg-red-200 text-red-800 text-[8px] px-1 rounded">{t.notesDesc}</span>
            </div>
            <div className="bg-white rounded border border-gray-200 p-2 text-[10px] text-gray-600 space-y-1">
              <p className="font-medium text-gray-700">{t.companyInfo}</p>
              <p className="text-gray-500">The Label Sunday, Vognmagergade 7, 6., 1120 Copenhagen K</p>

              <div className="border-t border-gray-100 pt-1 mt-1 space-y-0.5">
                <p>
                  {t.creatorLabel} {" "}
                  <Field value={extractedData?.creator_name ?? null} placeholder={p.creatorName} isRequired />
                  {" ("}
                  <Field value={extractedData?.artist_name ?? null} placeholder={p.artistName} isRequired />
                  {")"}
                </p>
                <p>
                  {t.birthDateLabel} {" "}
                  <Field value={extractedData?.birth_date ?? null} placeholder={p.birthDate} isRequired />
                </p>
                <p>
                  {t.taxNumberLabel} (
                  <Field value={extractedData?.tax_country ?? null} placeholder={p.taxCountry} isRequired />
                  ): {" "}
                  <Field value={extractedData?.tax_number ?? null} placeholder={p.taxNumber} isRequired />
                </p>
                <p>
                  {t.vatStatusLabel} {" "}
                  <Field value={extractedData?.vat_status ?? null} placeholder={p.vatStatus} isRequired />
                </p>
              </div>
            </div>
          </div>

          {/* Bank Transfer Specific */}
          {invoiceType === "bank_transfer" && (
            <div className="border-2 border-dashed border-teal-300 rounded p-2 bg-teal-50">
              <p className="font-bold text-teal-800 text-[10px] mb-1">{t.bankInfo}</p>
              <div className="bg-white rounded border border-gray-200 p-2 text-[10px] text-gray-600 space-y-0.5">
                <p>{t.bankName} <Field value={extractedData?.bank_name ?? null} placeholder={p.bankName} isRequired /></p>
                <p>{t.iban} <Field value={extractedData?.iban ?? null} placeholder={p.iban} isRequired /></p>
                <p>{t.swift} <Field value={extractedData?.swift_bic ?? null} placeholder={p.swift} isRequired /></p>
                <p>{t.accountHolder} <Field value={extractedData?.account_holder ?? null} placeholder={p.accountHolder} isRequired /></p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-[10px]">
        {hasData && (
          <>
            <div className="flex items-center gap-1">
              <span className="bg-red-100 text-red-600 border border-red-300 px-1.5 py-0.5 rounded text-[9px]">{t.missing}</span>
              <span className="text-gray-500">= {language === "da" ? "Manglende påkrævet felt" : "Missing required field"}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="bg-yellow-50 text-yellow-600 border border-yellow-200 px-1.5 py-0.5 rounded text-[9px]">{language === "da" ? "Valgfrit" : "Optional"}</span>
              <span className="text-gray-500">= {language === "da" ? "Valgfrit felt" : "Optional field"}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
