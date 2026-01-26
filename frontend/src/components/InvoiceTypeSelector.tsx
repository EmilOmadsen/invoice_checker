import type { InvoiceType, Language } from "../types/invoice";
import { t } from "../i18n/translations";

interface InvoiceTypeSelectorProps {
  selectedType: InvoiceType;
  onTypeChange: (type: InvoiceType) => void;
  disabled?: boolean;
  language: Language;
}

export function InvoiceTypeSelector({
  selectedType,
  onTypeChange,
  disabled = false,
  language,
}: InvoiceTypeSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        {t(language, "selectPaymentType")}
      </label>
      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={() => onTypeChange("paypal")}
          disabled={disabled}
          className={`
            relative flex flex-col items-center p-4 rounded-lg border-2 transition-all
            ${
              selectedType === "paypal"
                ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
                : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
            }
            ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          `}
        >
          <div
            className={`
            w-12 h-12 rounded-full flex items-center justify-center mb-2
            ${selectedType === "paypal" ? "bg-blue-500" : "bg-gray-200"}
          `}
          >
            <svg
              className={`w-6 h-6 ${
                selectedType === "paypal" ? "text-white" : "text-gray-500"
              }`}
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797h-2.19c-.524 0-.968.382-1.05.9l-1.12 7.106zm14.146-14.42a3.35 3.35 0 0 0-.607-.541c-.013.076-.026.175-.041.254-.93 4.778-4.005 7.201-9.138 7.201h-2.19a.563.563 0 0 0-.556.479l-1.187 7.527h-.506l-.24 1.516a.56.56 0 0 0 .554.647h3.882c.46 0 .85-.334.922-.788.06-.26.76-4.852.816-5.09a.932.932 0 0 1 .923-.788h.58c3.76 0 6.705-1.528 7.565-5.946.36-1.847.174-3.388-.777-4.471z" />
            </svg>
          </div>
          <span
            className={`font-medium ${
              selectedType === "paypal" ? "text-blue-700" : "text-gray-700"
            }`}
          >
            {t(language, "paypal")}
          </span>
          <span className="text-xs text-gray-500 mt-1">
            {t(language, "paypalRequirements")}
          </span>
          {selectedType === "paypal" && (
            <div className="absolute top-2 right-2">
              <svg
                className="w-5 h-5 text-blue-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </button>

        <button
          type="button"
          onClick={() => onTypeChange("bank_transfer")}
          disabled={disabled}
          className={`
            relative flex flex-col items-center p-4 rounded-lg border-2 transition-all
            ${
              selectedType === "bank_transfer"
                ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
                : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
            }
            ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          `}
        >
          <div
            className={`
            w-12 h-12 rounded-full flex items-center justify-center mb-2
            ${selectedType === "bank_transfer" ? "bg-blue-500" : "bg-gray-200"}
          `}
          >
            <svg
              className={`w-6 h-6 ${
                selectedType === "bank_transfer" ? "text-white" : "text-gray-500"
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
              />
            </svg>
          </div>
          <span
            className={`font-medium ${
              selectedType === "bank_transfer" ? "text-blue-700" : "text-gray-700"
            }`}
          >
            {t(language, "bankTransfer")}
          </span>
          <span className="text-xs text-gray-500 mt-1">
            {t(language, "bankRequirements")}
          </span>
          {selectedType === "bank_transfer" && (
            <div className="absolute top-2 right-2">
              <svg
                className="w-5 h-5 text-blue-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </button>
      </div>
    </div>
  );
}
