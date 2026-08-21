import { LANGUAGES as WELCOME_LANGUAGES } from "../lib/languages";
import type { LanguageOption } from "../types";

const INDIA_FLAG = "🇮🇳";

export const LANGUAGES: LanguageOption[] = WELCOME_LANGUAGES.map((language) => ({
  code: language.code,
  label: language.english,
  nativeLabel: language.label,
  flag: language.code === "ne" ? "🇳🇵" : language.code === "en" ? "🇬🇧" : INDIA_FLAG,
}));

export const DEFAULT_LANGUAGE = "hi";

export function getLanguageByCode(code: string): LanguageOption | undefined {
  return LANGUAGES.find((language) => language.code === code);
}
