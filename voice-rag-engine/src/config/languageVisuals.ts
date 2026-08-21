/**
 * Maps language codes to cultural artwork assets and native names.
 * Asset files are located in /public/.
 */

export interface LanguageVisual {
  nativeName: string;
  imageAsset: string;
  textColor?: string;
}

export const LANGUAGE_VISUALS: Record<string, LanguageVisual> = {
  as: {
    nativeName: "অসমীয়া",
    imageAsset: "/assam.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  bn: {
    nativeName: "বাংলা",
    imageAsset: "/bengali.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  gu: {
    nativeName: "ગુજરાતી",
    imageAsset: "/gujrati.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  hi: {
    nativeName: "हिन्दी",
    imageAsset: "/hindi.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  kn: {
    nativeName: "ಕನ್ನಡ",
    imageAsset: "/kannad.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  ml: {
    nativeName: "മലയാളം",
    imageAsset: "/malyalam.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  mr: {
    nativeName: "मराठी",
    imageAsset: "/marathi.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  ne: {
    nativeName: "नेपाली",
    imageAsset: "/nepali.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  or: {
    nativeName: "ଓଡ଼ିଆ",
    imageAsset: "/odia.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  od: {
    nativeName: "ଓଡ଼ିଆ",
    imageAsset: "/odia.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  pa: {
    nativeName: "ਪੰਜਾਬੀ",
    imageAsset: "/punjabi.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  sa: {
    nativeName: "संस्कृतम्",
    imageAsset: "/sanskrit.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  ta: {
    nativeName: "தமிழ்",
    imageAsset: "/tamil.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  te: {
    nativeName: "తెలుగు",
    imageAsset: "/telugu.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  ur: {
    nativeName: "اردو",
    imageAsset: "/urdu.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
  en: {
    nativeName: "English",
    imageAsset: "/goa-night.png",
    textColor: "rgba(255, 210, 26, 1)",
  },
};

export function getLanguageVisual(languageCode: string): LanguageVisual | null {
  return LANGUAGE_VISUALS[languageCode] ?? null;
}
