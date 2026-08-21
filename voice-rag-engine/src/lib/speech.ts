const LANGUAGE_VOICE_MAP: Record<string, string> = {
  hi: "hi-IN",
  bn: "bn-IN",
  mr: "mr-IN",
  gu: "gu-IN",
  ta: "ta-IN",
  te: "te-IN",
  kn: "kn-IN",
  ml: "ml-IN",
  pa: "pa-IN",
  ur: "ur-IN",
  or: "or-IN",
  as: "as-IN",
  ne: "ne-NP",
  sa: "sa-IN",
  en: "en-IN",
};

export function speakText(
  text: string,
  langCode: string,
  onStart?: () => void,
  onEnd?: () => void
): () => void {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) {
    return () => {};
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  const targetLocale = LANGUAGE_VOICE_MAP[langCode.toLowerCase()] || "en-US";
  utterance.lang = targetLocale;
  utterance.rate = 0.95;

  const voices = window.speechSynthesis.getVoices();
  const matchedVoice = voices.find((v) => v.lang.startsWith(targetLocale) || v.lang.includes(langCode));
  if (matchedVoice) {
    utterance.voice = matchedVoice;
  }

  if (onStart) utterance.onstart = onStart;
  if (onEnd) {
    utterance.onend = onEnd;
    utterance.onerror = onEnd;
  }

  window.speechSynthesis.speak(utterance);

  return () => {
    window.speechSynthesis.cancel();
  };
}

export function stopSpeaking() {
  if (typeof window !== "undefined" && "speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
}
