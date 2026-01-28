import { useState } from "react";
import { FileUpload } from "./components/FileUpload";
import { ResultChecklist } from "./components/ResultChecklist";
import { InvoiceTypeSelector } from "./components/InvoiceTypeSelector";
import { LanguageSelector } from "./components/LanguageSelector";
import { useInvoiceAnalysis } from "./hooks/useInvoiceAnalysis";
import { t } from "./i18n/translations";
import type { InvoiceType, Language } from "./types/invoice";

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [invoiceType, setInvoiceType] = useState<InvoiceType>("paypal");
  const [language, setLanguage] = useState<Language>("da");
  const { result, isLoading, error, analyzeInvoice, reset } =
    useInvoiceAnalysis();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    reset();
  };

  const handleAnalyze = async () => {
    if (selectedFile) {
      await analyzeInvoice(selectedFile, invoiceType, language);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    reset();
  };

  const handleTypeChange = (type: InvoiceType) => {
    setInvoiceType(type);
    if (result) {
      reset();
    }
  };

  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <button
              onClick={handleReset}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            >
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="text-left">
                <h1 className="text-xl font-bold text-gray-900">
                  {t(language, "appTitle")}
                </h1>
                <p className="text-sm text-gray-500">{t(language, "appSubtitle")}</p>
              </div>
            </button>
            <LanguageSelector
              selectedLanguage={language}
              onLanguageChange={handleLanguageChange}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Invoice Type Selection */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {t(language, "paymentMethod")}
            </h2>
            <InvoiceTypeSelector
              selectedType={invoiceType}
              onTypeChange={handleTypeChange}
              disabled={isLoading}
              language={language}
            />
          </section>

          {/* Upload Section */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {t(language, "uploadInvoice")}
            </h2>
            <FileUpload onFileSelect={handleFileSelect} disabled={isLoading} />

            {/* Selected file info */}
            {selectedFile && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg flex items-center gap-3">
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <span className="text-sm text-gray-600 flex-1 truncate">
                  {selectedFile.name}
                </span>
                <span className="text-xs text-gray-400">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-6 flex gap-3">
              <button
                onClick={handleAnalyze}
                disabled={!selectedFile || isLoading}
                className={`
                  flex-1 py-3 px-6 rounded-lg font-medium text-white transition-all
                  ${
                    selectedFile && !isLoading
                      ? "bg-blue-600 hover:bg-blue-700 cursor-pointer"
                      : "bg-gray-300 cursor-not-allowed"
                  }
                `}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    {t(language, "analyzing")}
                  </span>
                ) : (
                  `${t(language, "analyzeAs")} ${invoiceType === "paypal" ? t(language, "paypal") : t(language, "bankTransfer")}`
                )}
              </button>

              {(selectedFile || result) && (
                <button
                  onClick={handleReset}
                  disabled={isLoading}
                  className="py-3 px-6 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  {t(language, "reset")}
                </button>
              )}
            </div>
          </section>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <svg
                  className="w-5 h-5 text-red-500 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div>
                  <p className="font-medium text-red-800">{t(language, "errorOccurred")}</p>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results Section */}
          {result && (
            <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <span
                  className={`
                  inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${
                    result.invoice_type === "paypal"
                      ? "bg-blue-100 text-blue-800"
                      : "bg-green-100 text-green-800"
                  }
                `}
                >
                  {result.invoice_type === "paypal"
                    ? t(language, "paypal")
                    : t(language, "bankTransfer")}
                </span>
              </div>
              <ResultChecklist result={result} language={language} />
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <p className="text-center text-sm text-gray-500">
            {t(language, "footerText")}
            <br />
            {t(language, "footerDisclaimer")}
          </p>
        </div>
      </footer>

    </div>
  );
}

export default App;
