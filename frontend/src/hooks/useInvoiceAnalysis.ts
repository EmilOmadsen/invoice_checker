import { useState, useCallback } from "react";
import type { ValidationResult, InvoiceType, Language } from "../types/invoice";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface UseInvoiceAnalysisReturn {
  result: ValidationResult | null;
  isLoading: boolean;
  error: string | null;
  analyzeInvoice: (file: File, invoiceType: InvoiceType, language: Language) => Promise<void>;
  analyzeInvoiceUrl: (url: string, invoiceType: InvoiceType, language: Language) => Promise<void>;
  reset: () => void;
}

export function useInvoiceAnalysis(): UseInvoiceAnalysisReturn {
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeInvoice = useCallback(
    async (file: File, invoiceType: InvoiceType, language: Language) => {
      setIsLoading(true);
      setError(null);
      setResult(null);

      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("invoice_type", invoiceType);
        formData.append("language", language);

        const response = await fetch(`${API_URL}/api/analyze`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Server error: ${response.status}`
          );
        }

        const data: ValidationResult = await response.json();
        setResult(data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : language === "da" ? "Der opstod en uventet fejl" : "An unexpected error occurred";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const analyzeInvoiceUrl = useCallback(
    async (url: string, invoiceType: InvoiceType, language: Language) => {
      setIsLoading(true);
      setError(null);
      setResult(null);

      try {
        const response = await fetch(`${API_URL}/api/analyze-invoice`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            invoiceUrl: url,
            invoice_type: invoiceType,
            language: language,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Server error: ${response.status}`
          );
        }

        const data = await response.json();

        // The /api/analyze-invoice endpoint returns {status, logs, summary}
        // Convert to ValidationResult format for the UI
        if (data.status !== undefined && data.logs !== undefined) {
          // Parse the Copilot-format response back into ValidationResult
          const checks: ValidationResult["checks"] = [];
          const missingItems: string[] = [];
          const warnings: string[] = [];

          // Parse logs text to extract check info
          const lines = (data.logs as string).split("\n");
          let currentSection = "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("Errors (")) {
              currentSection = "errors";
            } else if (trimmed.startsWith("Approved (")) {
              currentSection = "approved";
            } else if (trimmed.startsWith("- MISSING:")) {
              const requirement = trimmed.replace("- MISSING:", "").trim();
              checks.push({ requirement, status: "missing", found_value: null, comment: "" });
              missingItems.push(requirement);
            } else if (trimmed.startsWith("- ERROR:")) {
              const requirement = trimmed.replace("- ERROR:", "").trim().split(" (found:")[0];
              checks.push({ requirement, status: "unclear", found_value: null, comment: "" });
            } else if (trimmed.startsWith("- WARNING:")) {
              warnings.push(trimmed.replace("- WARNING:", "").trim());
            } else if (currentSection === "approved" && trimmed.startsWith("- ")) {
              const parts = trimmed.substring(2).split(": ");
              const requirement = parts[0];
              const foundValue = parts.length > 1 ? parts.slice(1).join(": ") : null;
              checks.push({ requirement, status: "present", found_value: foundValue, comment: "" });
            }
          }

          setResult({
            overall_status: data.status === "pass" ? "approved" : "missing_information",
            invoice_type: invoiceType,
            checks,
            missing_items: missingItems,
            warnings,
            layout_suggestions: [],
            summary: data.summary || "",
            extracted_data: null,
          });
        } else {
          // Already in ValidationResult format
          setResult(data as ValidationResult);
        }
      } catch (err) {
        const message =
          err instanceof Error ? err.message : language === "da" ? "Der opstod en uventet fejl" : "An unexpected error occurred";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    result,
    isLoading,
    error,
    analyzeInvoice,
    analyzeInvoiceUrl,
    reset,
  };
}
