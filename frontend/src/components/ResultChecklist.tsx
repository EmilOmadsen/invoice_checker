import type { ValidationResult, CheckStatus, OverallStatus, Language } from "../types/invoice";
import { t } from "../i18n/translations";

interface ResultChecklistProps {
  result: ValidationResult;
  language: Language;
}

function StatusIcon({ status }: { status: CheckStatus }) {
  switch (status) {
    case "present":
      return (
        <span className="flex-shrink-0 w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </span>
      );
    case "missing":
      return (
        <span className="flex-shrink-0 w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </span>
      );
    case "unclear":
      return (
        <span className="flex-shrink-0 w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </span>
      );
  }
}

function OverallStatusBadge({ status, language }: { status: OverallStatus; language: Language }) {
  const config = {
    approved: {
      bg: "bg-green-100",
      text: "text-green-800",
      border: "border-green-200",
      labelKey: "approved" as const,
    },
    missing_information: {
      bg: "bg-yellow-100",
      text: "text-yellow-800",
      border: "border-yellow-200",
      labelKey: "missingInformation" as const,
    },
    invalid: {
      bg: "bg-red-100",
      text: "text-red-800",
      border: "border-red-200",
      labelKey: "invalid" as const,
    },
  };

  const { bg, text, border, labelKey } = config[status];

  return (
    <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${bg} ${text} border ${border}`}>
      {t(language, labelKey)}
    </span>
  );
}

export function ResultChecklist({ result, language }: ResultChecklistProps) {
  const presentCount = result.checks.filter((c) => c.status === "present").length;
  const missingCount = result.checks.filter((c) => c.status === "missing").length;
  const unclearCount = result.checks.filter((c) => c.status === "unclear").length;

  const foundLabel = language === "da" ? "Fundet" : "Found";
  const okLabel = "OK";
  const missingLabel = t(language, "missing");
  const unclearLabel = t(language, "unclear");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">{t(language, "results")}</h2>
        <OverallStatusBadge status={result.overall_status} language={language} />
      </div>

      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-500 mb-2">{t(language, "summary")}</h3>
        <p className="text-gray-700">{result.summary}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-600">{presentCount}</p>
          <p className="text-sm text-green-700">{okLabel}</p>
        </div>
        <div className="bg-red-50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-red-600">{missingCount}</p>
          <p className="text-sm text-red-700">{missingLabel}</p>
        </div>
        <div className="bg-yellow-50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-600">{unclearCount}</p>
          <p className="text-sm text-yellow-700">{unclearLabel}</p>
        </div>
      </div>

      {/* Checklist */}
      <div className="space-y-3">
        <h3 className="text-lg font-medium text-gray-900">{t(language, "validationChecks")}</h3>
        <div className="divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
          {result.checks.map((check, index) => (
            <div key={index} className="p-4 bg-white hover:bg-gray-50 transition-colors">
              <div className="flex items-start gap-3">
                <StatusIcon status={check.status} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900">{check.requirement}</p>
                  {check.found_value && (
                    <p className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">{foundLabel}:</span> {check.found_value}
                    </p>
                  )}
                  <p className="text-sm text-gray-500 mt-1">{check.comment}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Issues (Combined Missing Items and Warnings) */}
      {(result.missing_items.length > 0 || result.warnings.length > 0) && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-red-900">{t(language, "issues")}</h3>
          <ul className="bg-red-50 rounded-lg p-4 space-y-2">
            {result.missing_items.map((item, index) => (
              <li key={`missing-${index}`} className="flex items-center gap-2 text-red-700">
                <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                {item}
              </li>
            ))}
            {result.warnings.map((warning, index) => (
              <li key={`warning-${index}`} className="flex items-center gap-2 text-red-700">
                <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                {warning}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Layout Suggestions */}
      {result.layout_suggestions && result.layout_suggestions.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-blue-900">{t(language, "layoutSuggestions")}</h3>
          <div className="bg-blue-50 rounded-lg p-4 space-y-4">
            {result.layout_suggestions.map((suggestion, index) => (
              <div key={index} className="border-l-4 border-blue-400 pl-4">
                <p className="font-medium text-blue-800">{suggestion.section}</p>
                <p className="text-sm text-blue-700 mt-1">
                  <span className="font-medium">{t(language, "issue")}:</span> {suggestion.issue}
                </p>
                <p className="text-sm text-blue-600 mt-1">
                  <span className="font-medium">{t(language, "suggestion")}:</span> {suggestion.suggestion}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
