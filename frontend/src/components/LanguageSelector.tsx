import type { Language } from "../types/invoice";

interface LanguageSelectorProps {
  selectedLanguage: Language;
  onLanguageChange: (language: Language) => void;
}

export function LanguageSelector({
  selectedLanguage,
  onLanguageChange,
}: LanguageSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => onLanguageChange("da")}
        className={`
          px-3 py-1.5 text-sm font-medium rounded-md transition-all
          ${
            selectedLanguage === "da"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }
        `}
      >
        🇩🇰 Dansk
      </button>
      <button
        onClick={() => onLanguageChange("en")}
        className={`
          px-3 py-1.5 text-sm font-medium rounded-md transition-all
          ${
            selectedLanguage === "en"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }
        `}
      >
        🇬🇧 English
      </button>
    </div>
  );
}
