import { useState, useCallback } from "react";
import type { ValidationResult, InvoiceType, Language } from "../types/invoice";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface UseInvoiceAnalysisReturn {
  result: ValidationResult | null;
  isLoading: boolean;
  error: string | null;
  analyzeInvoice: (file: File, invoiceType: InvoiceType, language: Language) => Promise<void>;
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
    reset,
  };
}
