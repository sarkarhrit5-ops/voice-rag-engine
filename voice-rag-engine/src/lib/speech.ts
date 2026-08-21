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

// Language-specific phonetic adjustments for smooth TTS pronunciation
const PHONETIC_REPLACEMENTS: Record<string, [RegExp, string][]> = {
  hi: [[/\bRAG\b/g, "आर.ए.जी."], [/\bAI\b/g, "ए.आई."]],
  bn: [[/\bRAG\b/g, "র‌্যাগ"], [/\bAI\b/g, "এ.আই."]],
  mr: [[/\bRAG\b/g, "आर.ए.जी."], [/\bAI\b/g, "ए.आई."]],
  gu: [[/\bRAG\b/g, "આર.એ.જી."], [/\bAI\b/g, "એ.આઈ."]],
  ta: [[/\bRAG\b/g, "ராக்"], [/\bAI\b/g, "ஏ.ஐ."]],
  te: [[/\bRAG\b/g, "రాగ్"], [/\bAI\b/g, "ఏ.ఐ."]],
  kn: [[/\bRAG\b/g, "ರಾಗ್"], [/\bAI\b/g, "ಎ.ಐ."]],
  ml: [[/\bRAG\b/g, "റാഗ്"], [/\bAI\b/g, "എ.ഐ."]],
  pa: [[/\bRAG\b/g, "ਰੈਗ"], [/\bAI\b/g, "ਏ.ਆਈ."]],
  ur: [[/\bRAG\b/g, "ریگ"], [/\bAI\b/g, "اے.آئی."]],
  or: [[/\bRAG\b/g, "ରାଗ୍"], [/\bAI\b/g, "ଏ.ଆଇ."]],
  as: [[/\bRAG\b/g, "ৰেগ"], [/\bAI\b/g, "এ.আই."]],
  ne: [[/\bRAG\b/g, "आर.ए.जी."], [/\bAI\b/g, "ए.आई."]],
  sa: [[/\bRAG\b/g, "आर.ए.जी."], [/\bAI\b/g, "ए.आई."]],
  en: [[/\bRAG\b/g, "R-A-G"]],
};

function prepareSpeechText(text: string, langCode: string): string {
  let cleaned = text.trim();
  const replacements = PHONETIC_REPLACEMENTS[langCode.toLowerCase()] || [];
  for (const [pattern, replacement] of replacements) {
    cleaned = cleaned.replace(pattern, replacement);
  }
  return cleaned;
}

let activeUtterance: SpeechSynthesisUtterance | null = null;
let keepAliveTimer: ReturnType<typeof setInterval> | null = null;

export function speakText(
  text: string,
  langCode: string,
  onStart?: () => void,
  onEnd?: () => void
): () => void {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) {
    return () => {};
  }

  stopSpeaking();

  const cleanLang = (langCode || "hi").toLowerCase().split("-")[0];
  const processedText = prepareSpeechText(text, cleanLang);
  const targetLocale = LANGUAGE_VOICE_MAP[cleanLang] || "en-US";

  const utterance = new SpeechSynthesisUtterance(processedText);
  utterance.lang = targetLocale;
  utterance.rate = 0.92;
  utterance.pitch = 1.0;

  activeUtterance = utterance;

  const setVoiceAndSpeak = () => {
    const voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
      const exactVoice = voices.find(
        (v) => v.lang.toLowerCase() === targetLocale.toLowerCase()
      );
      const prefixVoice = voices.find(
        (v) => v.lang.toLowerCase().startsWith(cleanLang) || v.lang.toLowerCase().includes(cleanLang)
      );
      const fallbackVoice = voices.find(
        (v) => v.lang.toLowerCase().includes("in") || v.lang.toLowerCase().startsWith("en")
      );
      utterance.voice = exactVoice || prefixVoice || fallbackVoice || null;
    }

    utterance.onstart = () => {
      // Chrome speech synthesis keep-alive for long sentences
      if (keepAliveTimer) clearInterval(keepAliveTimer);
      keepAliveTimer = setInterval(() => {
        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        } else {
          if (keepAliveTimer) clearInterval(keepAliveTimer);
        }
      }, 8000);

      onStart?.();
    };

    const cleanup = () => {
      if (keepAliveTimer) {
        clearInterval(keepAliveTimer);
        keepAliveTimer = null;
      }
      activeUtterance = null;
      onEnd?.();
    };

    utterance.onend = cleanup;
    utterance.onerror = cleanup;

    window.speechSynthesis.speak(utterance);
  };

  const voices = window.speechSynthesis.getVoices();
  if (voices.length === 0) {
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.onvoiceschanged = null;
      setVoiceAndSpeak();
    };
  } else {
    setVoiceAndSpeak();
  }

  return () => {
    stopSpeaking();
  };
}

export function stopSpeaking() {
  if (typeof window !== "undefined" && "speechSynthesis" in window) {
    if (keepAliveTimer) {
      clearInterval(keepAliveTimer);
      keepAliveTimer = null;
    }
    activeUtterance = null;
    window.speechSynthesis.cancel();
  }
}
