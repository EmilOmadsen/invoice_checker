import type { Language } from "../types/invoice";

interface IdealLayoutPreviewProps {
  language: Language;
  isOpen: boolean;
  onClose: () => void;
}

export function IdealLayoutPreview({ language, isOpen, onClose }: IdealLayoutPreviewProps) {
  if (!isOpen) return null;

  const texts = {
    da: {
      title: "Ideelt PayPal Faktura Layout",
      close: "Luk",
      header: "HEADER",
      headerDesc: "Øverst til højre",
      invoiceTitle: "FAKTURERING",
      senderName: "Afsenders fulde navn",
      address: "Komplet adresse med land",
      phone: "Telefonnummer",
      email: "Email-adresse",
      invoiceDetails: "FAKTURAOPLYSNINGER",
      invoiceDetailsDesc: "Venstre side",
      invoiceNo: "Faktura-nr.:",
      invoiceDate: "Fakturadato:",
      dueDate: "Forfaldsdato:",
      qrCode: "QR-kode (valgfrit)",
      recipient: "MODTAGER",
      sendTo: "SEND FAKTURA TIL",
      lineItems: "LINJEPOSTER",
      columnHeaders: "Nr. | VARER OG BESKRIVELSE | ANTAL/TIMER | PRIS | BELØB",
      serviceDesc: "Beskrivelse af ydelsen",
      subtotal: "Subtotal",
      total: "SAMLET PRIS",
      notes: "BEMÆRKNINGER TIL KUNDEN",
      notesDesc: "Vigtig sektion!",
      companyInfo: "Modtagers firmaoplysninger",
      creatorInfo: "Creator: Navn (kunstnernavn)",
      birthDate: "Date of birth: YYYY-MM-DD",
      taxNumber: "Personal tax number (XX): XXXXXX-XXXX",
      vatStatus: "Not VAT registered.",
      required: "Påkrævet",
      recommended: "Anbefalet",
    },
    en: {
      title: "Ideal PayPal Invoice Layout",
      close: "Close",
      header: "HEADER",
      headerDesc: "Top right",
      invoiceTitle: "INVOICE",
      senderName: "Sender's full name",
      address: "Complete address with country",
      phone: "Phone number",
      email: "Email address",
      invoiceDetails: "INVOICE DETAILS",
      invoiceDetailsDesc: "Left side",
      invoiceNo: "Invoice no.:",
      invoiceDate: "Invoice date:",
      dueDate: "Due date:",
      qrCode: "QR code (optional)",
      recipient: "RECIPIENT",
      sendTo: "SEND INVOICE TO",
      lineItems: "LINE ITEMS",
      columnHeaders: "No. | ITEMS AND DESCRIPTION | QTY/HOURS | PRICE | AMOUNT",
      serviceDesc: "Description of service",
      subtotal: "Subtotal",
      total: "TOTAL",
      notes: "NOTES TO CUSTOMER",
      notesDesc: "Important section!",
      companyInfo: "Recipient company information",
      creatorInfo: "Creator: Name (artist name)",
      birthDate: "Date of birth: YYYY-MM-DD",
      taxNumber: "Personal tax number (XX): XXXXXX-XXXX",
      vatStatus: "Not VAT registered.",
      required: "Required",
      recommended: "Recommended",
    },
  };

  const t = texts[language];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">{t.title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Invoice Preview */}
        <div className="p-6">
          <div className="border-2 border-gray-300 rounded-lg p-6 bg-gray-50">
            {/* Invoice Layout Preview */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">

              {/* Top Section - Header and Invoice Details */}
              <div className="flex justify-between">
                {/* Left - Invoice Details */}
                <div className="space-y-2">
                  <div className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {t.invoiceDetailsDesc}
                  </div>
                  <div className="border-2 border-dashed border-blue-300 rounded-lg p-4 bg-blue-50">
                    <p className="font-semibold text-gray-700 mb-2">{t.invoiceDetails}</p>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>{t.invoiceNo} <span className="text-gray-400">001</span></p>
                      <p>{t.invoiceDate} <span className="text-gray-400">2024-01-15</span></p>
                      <p>{t.dueDate} <span className="text-gray-400">2024-01-30</span></p>
                    </div>
                    <div className="mt-3 border-2 border-dashed border-gray-300 rounded p-3 text-center">
                      <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                      </svg>
                      <p className="text-xs text-gray-500 mt-1">{t.qrCode}</p>
                      <span className="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded mt-1">
                        {t.recommended}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right - Header */}
                <div className="text-right space-y-2">
                  <div className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                    {t.headerDesc}
                  </div>
                  <div className="border-2 border-dashed border-green-300 rounded-lg p-4 bg-green-50">
                    <p className="text-2xl font-bold text-gray-800 mb-3">{t.invoiceTitle}</p>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p className="font-semibold">{t.senderName}</p>
                      <p>{t.address}</p>
                      <p>{t.phone}</p>
                      <p>{t.email}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recipient Section */}
              <div className="border-2 border-dashed border-purple-300 rounded-lg p-4 bg-purple-50">
                <p className="font-semibold text-gray-700 mb-2">{t.sendTo}</p>
                <p className="text-sm text-gray-600">info@thelabelsunday.com</p>
              </div>

              {/* Line Items Table */}
              <div className="border-2 border-dashed border-orange-300 rounded-lg p-4 bg-orange-50">
                <p className="font-semibold text-gray-700 mb-3">{t.lineItems}</p>
                <div className="bg-white rounded border border-gray-200 overflow-hidden">
                  <div className="bg-gray-100 px-3 py-2 text-xs font-medium text-gray-600">
                    {t.columnHeaders}
                  </div>
                  <div className="px-3 py-2 text-sm text-gray-600 border-t border-gray-200">
                    <p>1 | {t.serviceDesc} | 1 | €500.00 | €500.00</p>
                  </div>
                  <div className="px-3 py-2 text-sm border-t border-gray-200 flex justify-between">
                    <span>{t.subtotal}</span>
                    <span>€500.00</span>
                  </div>
                  <div className="px-3 py-2 text-sm font-bold border-t-2 border-gray-300 flex justify-between bg-gray-50">
                    <span>{t.total}</span>
                    <span>€500.00 EUR</span>
                  </div>
                </div>
              </div>

              {/* Notes to Customer - Most Important! */}
              <div className="border-2 border-dashed border-red-300 rounded-lg p-4 bg-red-50">
                <div className="flex items-center gap-2 mb-3">
                  <p className="font-semibold text-gray-700">{t.notes}</p>
                  <span className="inline-block bg-red-100 text-red-800 text-xs px-2 py-0.5 rounded font-medium">
                    {t.notesDesc}
                  </span>
                </div>
                <div className="bg-white rounded border border-gray-200 p-3 text-sm text-gray-600 space-y-2">
                  <p className="font-medium">{t.companyInfo}</p>
                  <p className="text-gray-500">The Label Sunday, Vognmagergade 7, 6., 1120 Copenhagen K</p>
                  <p className="text-gray-500">info@thelabelsunday.com</p>
                  <div className="border-t border-gray-200 pt-2 mt-2 space-y-1">
                    <p>{t.creatorInfo} <span className="bg-green-100 text-green-800 text-xs px-1.5 py-0.5 rounded ml-1">{t.required}</span></p>
                    <p>{t.birthDate} <span className="bg-green-100 text-green-800 text-xs px-1.5 py-0.5 rounded ml-1">{t.required}</span></p>
                    <p>{t.taxNumber} <span className="bg-green-100 text-green-800 text-xs px-1.5 py-0.5 rounded ml-1">{t.required}</span></p>
                    <p>{t.vatStatus} <span className="bg-green-100 text-green-800 text-xs px-1.5 py-0.5 rounded ml-1">{t.required}</span></p>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-dashed border-green-300 bg-green-50 rounded"></div>
              <span className="text-gray-600">{t.header}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-dashed border-blue-300 bg-blue-50 rounded"></div>
              <span className="text-gray-600">{t.invoiceDetails}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-dashed border-purple-300 bg-purple-50 rounded"></div>
              <span className="text-gray-600">{t.recipient}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-dashed border-orange-300 bg-orange-50 rounded"></div>
              <span className="text-gray-600">{t.lineItems}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-dashed border-red-300 bg-red-50 rounded"></div>
              <span className="text-gray-600">{t.notes}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
