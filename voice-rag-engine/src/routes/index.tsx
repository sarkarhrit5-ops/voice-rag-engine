import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "Voice RAG — HH Goa 2026 | Speak to knowledge" },
      {
        name: "description",
        content:
          "A multilingual voice-enabled RAG engine that retrieves relevant knowledge, verifies the evidence, and answers without inventing facts.",
      },
      { property: "og:title", content: "Voice RAG — HH Goa 2026" },
      {
        property: "og:description",
        content: "Speak to knowledge. Get grounded, verified answers in your language.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
});

import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { WelcomeScreen } from "../components/WelcomeScreen";
import { Header } from "../components/Header";
import { Hero } from "../components/Hero";
import { VoiceRecorder } from "../components/VoiceRecorder";
import { TranscriptCard } from "../components/TranscriptCard";
import { AnswerCard } from "../components/AnswerCard";
import { PipelineSteps } from "../components/PipelineSteps";
import { Footer } from "../components/Footer";
import { AtmosphereBackground } from "../components/AtmosphereBackground";
import { SceneObjects } from "../components/SceneObjects";
import { speakText, stopSpeaking } from "../lib/speech";
import { findPredefinedResponse } from "../config/predefinedQueries";
import { useAudioRecorder } from "../hooks/useAudioRecorder";
import { isBackendConfigured, sendVoiceQuery, decodeAudioBase64 } from "../lib/api";
import { getLanguageByCode } from "../config/languages";
import { DEFAULT_LANGUAGE } from "../config/languages";
import type { VoiceState, VoiceQueryResponse } from "../types";
import type { LanguageCode } from "../lib/languages";

function Index() {
  const [appState, setAppState] = useState<"welcome" | "main">("welcome");
  const [selectedLanguage, setSelectedLanguage] = useState<string>(DEFAULT_LANGUAGE);

  const enterApp = useCallback((languageCode: LanguageCode) => {
    setSelectedLanguage(languageCode);
    setAppState("main");
  }, []);

  const backToWelcome = useCallback(() => {
    setAppState("welcome");
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (appState === "main" && event.key === "Escape") {
        backToWelcome();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [appState, backToWelcome]);

  if (appState === "welcome") {
    return (
      <div className="relative h-screen w-screen overflow-hidden bg-forest-950">
        <WelcomeScreen onEnter={enterApp} />
      </div>
    );
  }

  return <MainScreen initialLanguage={selectedLanguage} onBack={backToWelcome} />;
}

interface MainScreenProps {
  initialLanguage: string;
  onBack: () => void;
}

function MainScreen({ initialLanguage, onBack }: MainScreenProps) {
  const [language, setLanguage] = useState(initialLanguage);
  const [voiceState, setVoiceState] = useState<VoiceState>("idle");
  const [response, setResponse] = useState<VoiceQueryResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isPlayingAnswer, setIsPlayingAnswer] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const [pointer, setPointer] = useState({ x: 0, y: 0 });

  const {
    status: recorderStatus,
    audioBlob,
    audioLevel,
    start,
    stop,
    reset,
    error: recorderError,
  } = useAudioRecorder();

  const answerAudioRef = useRef<HTMLAudioElement | null>(null);
  const answerAudioUrlRef = useRef<string | null>(null);

  const backendReady = isBackendConfigured();

  useEffect(() => {
    setLanguage(initialLanguage);
  }, [initialLanguage]);

  // Parallax scroll tracking (throttled via rAF)
  useEffect(() => {
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          setScrollY(window.scrollY);
          ticking = false;
        });
        ticking = true;
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    let frame = 0;
    const handlePointerMove = (event: PointerEvent) => {
      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        setPointer({
          x: (event.clientX / window.innerWidth - 0.5) * 2,
          y: (event.clientY / window.innerHeight - 0.5) * 2,
        });
        frame = 0;
      });
    };
    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, []);

  useEffect(() => {
    return () => {
      if (answerAudioRef.current) {
        answerAudioRef.current.pause();
      }
      if (answerAudioUrlRef.current) {
        URL.revokeObjectURL(answerAudioUrlRef.current);
      }
    };
  }, []);

  const handleToggle = useCallback(async () => {
    if (voiceState === "listening") {
      stop();
      setVoiceState("idle");
      return;
    }
    if (voiceState === "answer" || voiceState === "refused" || voiceState === "error") {
      setResponse(null);
      setErrorMsg(null);
      setVoiceState("idle");
      reset();
    }
    await start();
  }, [voiceState, start, stop, reset]);

  useEffect(() => {
    if (recorderStatus === "recording") {
      setVoiceState("listening");
    } else if (recorderStatus === "denied" || recorderStatus === "unsupported") {
      setVoiceState("error");
    }
  }, [recorderStatus]);

  // When recording stops and we have a blob, run the query
  useEffect(() => {
    if (audioBlob && voiceState === "idle" && recorderStatus === "idle") {
      processQuery(audioBlob);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioBlob, recorderStatus]);

  const processQuery = useCallback(
    async (blob: Blob) => {
      stopSpeaking();
      setResponse(null);
      setErrorMsg(null);

      setVoiceState("processing");

      try {
        if (!backendReady) {
          setErrorMsg("The voice API is not configured. Set VITE_API_BASE_URL to your FastAPI backend.");
          setVoiceState("error");
          return;
        }

        const res = await sendVoiceQuery(blob, language);
        const predefined = findPredefinedResponse(res.transcription, res.normalized_language || res.language || language);
        const responseToShow = predefined
          ? {
              ...predefined,
              transcription: res.transcription,
              language: res.language || predefined.language || language,
              normalized_language:
                res.normalized_language || predefined.normalized_language || predefined.language || language,
              latency: res.latency ?? predefined.latency,
              request_id: res.request_id,
            }
          : res;
        setResponse(responseToShow);
        setVoiceState(responseToShow.refusal || !responseToShow.grounded ? "refused" : "answer");

        if (answerAudioRef.current) {
          answerAudioRef.current.pause();
          answerAudioRef.current = null;
        }
        if (answerAudioUrlRef.current) {
          URL.revokeObjectURL(answerAudioUrlRef.current);
          answerAudioUrlRef.current = null;
        }

        const playNativeSpeech = () => {
          if (responseToShow.answer) {
            speakText(
              responseToShow.answer,
              responseToShow.language || language,
              () => setIsPlayingAnswer(true),
              () => setIsPlayingAnswer(false)
            );
          }
        };

        if (!predefined && res.audio_base64 && !res.audio_base64.startsWith("mock-audio") && res.audio_base64.length > 100) {
          try {
            const url = decodeAudioBase64(res.audio_base64);
            answerAudioUrlRef.current = url;
            const audio = new Audio(url);
            answerAudioRef.current = audio;
            setIsPlayingAnswer(true);
            audio.onended = () => setIsPlayingAnswer(false);
            audio.onerror = () => playNativeSpeech();
            audio.play().catch(() => playNativeSpeech());
          } catch {
            playNativeSpeech();
          }
        } else if (!predefined && res.audio_url) {
          const audio = new Audio(res.audio_url);
          answerAudioRef.current = audio;
          setIsPlayingAnswer(true);
          audio.onended = () => setIsPlayingAnswer(false);
          audio.onerror = () => playNativeSpeech();
          audio.play().catch(() => playNativeSpeech());
        } else {
          playNativeSpeech();
        }
      } catch (err) {
        const msg = (err as Error).message;
        if (msg === "TIMEOUT") {
          setErrorMsg("The request took longer than expected. Please try again.");
        } else if (msg === "BACKEND_NOT_CONFIGURED" || msg.startsWith("FastAPI is unavailable")) {
          setErrorMsg("The voice API is not configured. Set VITE_API_BASE_URL to your FastAPI backend.");
        } else {
          setErrorMsg("Something went wrong while reaching the voice engine. Please try again.");
        }
        setVoiceState("error");
      }
    },
    [backendReady, language],
  );

  const handlePlayAnswer = useCallback(() => {
    if (isPlayingAnswer) {
      stopSpeaking();
      if (answerAudioRef.current) {
        answerAudioRef.current.pause();
      }
      setIsPlayingAnswer(false);
      return;
    }

    const playSpeech = () => {
      if (response?.answer) {
        speakText(
          response.answer,
          response.language || language,
          () => setIsPlayingAnswer(true),
          () => setIsPlayingAnswer(false)
        );
      }
    };

    if (answerAudioRef.current && answerAudioUrlRef.current) {
      answerAudioRef.current.currentTime = 0;
      setIsPlayingAnswer(true);
      answerAudioRef.current.onended = () => setIsPlayingAnswer(false);
      answerAudioRef.current.onerror = () => playSpeech();
      answerAudioRef.current.play().catch(() => playSpeech());
    } else {
      playSpeech();
    }
  }, [isPlayingAnswer, response, language]);

  const handleRetry = useCallback(() => {
    stopSpeaking();
    if (answerAudioRef.current) {
      answerAudioRef.current.pause();
      answerAudioRef.current = null;
    }
    if (answerAudioUrlRef.current) {
      URL.revokeObjectURL(answerAudioUrlRef.current);
      answerAudioUrlRef.current = null;
    }
    setResponse(null);
    setErrorMsg(null);
    setVoiceState("idle");
    reset();
  }, [reset]);

  const responseLanguage = response?.normalized_language ?? response?.language ?? language;
  const selectedLang = getLanguageByCode(responseLanguage);
  const showTranscript = response && (voiceState === "answer" || voiceState === "refused");
  const canPlayAnswer = Boolean(
    response && (response.audio_base64 || response.audio_url || response.answer)
  );

  return (
    <div id="top" className="relative min-h-screen overflow-x-hidden bg-forest-dark">
      {/* === Immersive layered atmosphere background === */}
      <AtmosphereBackground scrollY={scrollY} pointer={pointer} />

      {/* Midground dimensional objects — behind the UI, in front of the landscape */}
      <div className="pointer-events-none fixed inset-0 z-[5]">
        <SceneObjects scrollY={scrollY} pointer={pointer} variant="mid" />
      </div>

      <div className="relative z-10">
        <Header />
        <div className="mx-auto mt-4 flex max-w-7xl px-5 sm:px-8">
          <button
            type="button"
            onClick={onBack}
            className="focus-ring inline-flex items-center gap-2 rounded-full border border-cream/15 bg-forest/30 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-cream/70 transition-all hover:border-gold/30 hover:text-cream"
            aria-label="Return to language selection"
          >
            <ArrowLeft className="h-3.5 w-3.5" strokeWidth={2.2} />
            Languages
          </button>
        </div>

        {/* Hero + Voice card + Predefined queries */}
        <main className="mx-auto max-w-7xl px-5 pt-6 sm:px-8 sm:pt-10">
          <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-2 lg:gap-16">
            {/* Left column — parallax shift */}
            <div
              className="animate-fade-up"
              style={{ transform: `translateY(${scrollY * -0.02}px)` }}
            >
              <Hero language={language} />
            </div>

            {/* Right column — voice card */}
            <div className="animate-fade-up [animation-delay:0.1s]">
              <VoiceRecorder
                state={voiceState}
                language={language}
                recorderStatus={recorderStatus}
                recorderError={recorderError ?? errorMsg}
                audioLevel={audioLevel}
                onToggle={handleToggle}
                onLanguageChange={setLanguage}
                onRetry={handleRetry}
                onPlayAnswer={handlePlayAnswer}
                pointer={pointer}
                canPlayAnswer={canPlayAnswer}
                isPlayingAnswer={isPlayingAnswer}
              />

              {/* Transcript + Answer below the card */}
              {showTranscript && response && (
                <div className="mt-5 space-y-4">
                  <TranscriptCard
                    text={response.transcription}
                    languageLabel={selectedLang?.label ?? ""}
                  />

                  {voiceState === "refused" ? (
                    <RefusalCard
                      text={response.answer}
                      reason={response.reason ?? response.tts_error ?? ""}
                    />
                  ) : (
                    <AnswerCard
                      answer={response.answer}
                      grounded={response.grounded}
                      confidence={response.confidence ?? 0}
                      sources={response.sources ?? []}
                      reason={response.reason ?? ""}
                      canPlayAnswer={canPlayAnswer}
                      isPlayingAnswer={isPlayingAnswer}
                      onPlayAnswer={handlePlayAnswer}
                    />
                  )}

                  {/* Ask another */}
                  <div className="flex justify-center pt-2">
                    <button
                      onClick={handleRetry}
                      className="focus-ring flex items-center gap-2 rounded-full border border-cream/15 bg-forest/30 px-5 py-2.5 text-sm font-medium text-cream/80 transition-all hover:border-gold/30 hover:text-cream"
                      style={{ boxShadow: "0 1px 0 0 rgba(255,210,26,0.06) inset" }}
                    >
                      Ask another question
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Pipeline section */}
          <div className="mt-20 sm:mt-28">
            <PipelineSteps />
          </div>
        </main>

        <Footer />
      </div>

      {/* Foreground accents — a few objects float slightly in front of the UI */}
      <div className="pointer-events-none fixed inset-0 z-20">
        <SceneObjects scrollY={scrollY} pointer={pointer} variant="front" />
      </div>
    </div>
  );
}

function RefusalCard({ text, reason }: { text?: string; reason?: string }) {
  return (
    <div
      className="animate-fade-up rounded-3xl border border-hh-pink/20 p-6"
      style={{
        background: "linear-gradient(145deg, rgba(4,43,29,0.7) 0%, rgba(4,43,29,0.9) 100%)",
        boxShadow: "0 1px 0 0 rgba(255,210,26,0.06) inset, 0 24px 60px -24px rgba(0,0,0,0.6)",
      }}
    >
      <div className="mb-3 flex items-center gap-2">
        <span
          className="flex h-7 w-7 items-center justify-center rounded-full"
          style={{
            background:
              "linear-gradient(145deg, rgba(245,0,122,0.2) 0%, rgba(245,0,122,0.05) 100%)",
          }}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
            <path
              d="M7 1 L13 12 L1 12 Z"
              stroke="#F5007A"
              strokeWidth="1.5"
              strokeLinejoin="round"
            />
            <path d="M7 5 L7 8" stroke="#F5007A" strokeWidth="1.5" strokeLinecap="round" />
            <circle cx="7" cy="10" r="0.8" fill="#F5007A" />
          </svg>
        </span>
        <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-hh-pink-soft">
          Not enough evidence
        </span>
      </div>
      <p className="font-display text-lg leading-relaxed text-cream">
        {text || "I couldn't find enough reliable information to answer that."}
      </p>
      {reason && <p className="mt-3 text-sm leading-relaxed text-cream/55">{reason}</p>}
    </div>
  );
}
