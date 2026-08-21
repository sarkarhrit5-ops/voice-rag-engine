export const LANGUAGES = [
  { code: "as", label: "অসমীয়া", english: "Assamese" },
  { code: "bn", label: "বাংলা", english: "Bengali" },
  { code: "gu", label: "ગુજરાતી", english: "Gujarati" },
  { code: "hi", label: "हिन्दी", english: "Hindi" },
  { code: "kn", label: "ಕನ್ನಡ", english: "Kannada" },
  { code: "ml", label: "മലയാളം", english: "Malayalam" },
  { code: "mr", label: "मराठी", english: "Marathi" },
  { code: "ne", label: "नेपाली", english: "Nepali" },
  { code: "or", label: "ଓଡ଼ିଆ", english: "Odia" },
  { code: "pa", label: "ਪੰਜਾਬੀ", english: "Punjabi" },
  { code: "sa", label: "संस्कृतम्", english: "Sanskrit" },
  { code: "ta", label: "தமிழ்", english: "Tamil" },
  { code: "te", label: "తెలుగు", english: "Telugu" },
  { code: "ur", label: "اردو", english: "Urdu" },
  { code: "en", label: "English", english: "English" },
] as const;

export type LanguageCode = (typeof LANGUAGES)[number]["code"];

export type VoicePhase =
  "idle" | "listening" | "understanding" | "searching" | "checking" | "answered" | "refused";

export interface SourceRef {
  id: number;
  title: string;
  snippet: string;
  url: string;
}

export interface VoiceResult {
  transcript: string;
  answer: string;
  grounded: boolean;
  sources: SourceRef[];
  refused: boolean;
}

export const PIPELINE_STAGES: { key: VoicePhase; label: string }[] = [
  { key: "understanding", label: "Understanding" },
  { key: "searching", label: "Searching knowledge" },
  { key: "checking", label: "Checking evidence" },
];
