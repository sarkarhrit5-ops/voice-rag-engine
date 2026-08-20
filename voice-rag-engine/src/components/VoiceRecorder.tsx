import { AlertCircle, Headphones, RotateCcw, Volume2 } from 'lucide-react';
import type { VoiceState } from '../types';
import { LanguageSelector } from './LanguageSelector';
import { MicButton } from './MicButton';

interface VoiceRecorderProps {
  state: VoiceState;
  language: string;
  recorderStatus: 'idle' | 'recording' | 'denied' | 'unsupported';
  recorderError: string | null;
  audioLevel: number;
  onToggle: () => void;
  onLanguageChange: (code: string) => void;
  onRetry?: () => void;
  onPlayAnswer?: () => void;
  canPlayAnswer?: boolean;
  isPlayingAnswer?: boolean;
  pointer?: { x: number; y: number };
}

const PROCESSING_STAGES = [
  { state: 'processing', label: 'Understanding' },
  { state: 'retrieving', label: 'Searching knowledge' },
  { state: 'verifying', label: 'Checking evidence' },
] as const;

export function VoiceRecorder({
  state,
  language,
  recorderStatus,
  recorderError,
  audioLevel,
  onToggle,
  onLanguageChange,
  onRetry,
  onPlayAnswer,
  canPlayAnswer,
  isPlayingAnswer,
  pointer = { x: 0, y: 0 },
}: VoiceRecorderProps) {
  const isProcessing =
    state === 'processing' || state === 'retrieving' || state === 'verifying';

  return (
    <section
      id="voice"
      className="surface-3d relative w-full rounded-4xl border border-gold/15 p-6 transition-[transform,box-shadow,border-color] duration-500 sm:p-8 lg:w-[120%] lg:min-w-[816px]"
      aria-label="Voice interaction"
        style={{
          minWidth: '320px',
          maxWidth: 'calc(100vw - 40px)',
          transform: `perspective(1200px) rotateX(${pointer.y * -1.2}deg) rotateY(${pointer.x * 1.6}deg) translate3d(${pointer.x * 3}px, ${pointer.y * 2}px, 0)`,
          background: 'radial-gradient(circle at 72% 35%, rgba(245,0,122,0.08), transparent 24%), radial-gradient(circle at 20% 10%, rgba(255,210,26,0.1), transparent 28%), linear-gradient(145deg, rgba(6,59,40,0.62), rgba(2,31,22,0.78))',
          backdropFilter: 'blur(18px) saturate(1.1)',
          WebkitBackdropFilter: 'blur(18px) saturate(1.1)',
          boxShadow: isProcessing
            ? '0 1px 0 0 rgba(255,244,214,0.2) inset, 0 0 56px rgba(255,210,26,0.16), 0 28px 70px -28px rgba(0,0,0,0.8)'
            : '0 1px 0 0 rgba(255,244,214,0.14) inset, 0 0 38px rgba(255,180,40,0.1), 0 28px 70px -28px rgba(0,0,0,0.78)',
        }}
    >
      {/* Corner ornaments — Goa-inspired geometric motifs */}
      <div className="pointer-events-none absolute -right-3 -top-3 opacity-50">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none" aria-hidden="true">
          <path d="M56 0 L56 20 M56 0 L36 0" stroke="#FFD21A" strokeWidth="1.5" opacity="0.6" />
          <circle cx="56" cy="0" r="3.5" fill="#F5007A" opacity="0.7" />
          <path d="M44 4 Q 44 12, 52 12" stroke="#FFD21A" strokeWidth="1" fill="none" opacity="0.4" />
        </svg>
      </div>
      <div className="pointer-events-none absolute -bottom-3 -left-3 rotate-180 opacity-50">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none" aria-hidden="true">
          <path d="M56 0 L56 20 M56 0 L36 0" stroke="#FFD21A" strokeWidth="1.5" opacity="0.6" />
          <circle cx="56" cy="0" r="3.5" fill="#F5007A" opacity="0.7" />
          <path d="M44 4 Q 44 12, 52 12" stroke="#FFD21A" strokeWidth="1" fill="none" opacity="0.4" />
        </svg>
      </div>

      {/* Environmental light spill around the mic stage */}
      <div
        className="pointer-events-none absolute left-1/2 top-[48%] -translate-x-1/2 -translate-y-1/2"
        style={{
          width: 470,
          height: 470,
          transform: `translate3d(calc(-50% + ${pointer.x * 5}px), calc(-50% + ${pointer.y * 4}px), 0)`,
          background: isProcessing
            ? 'radial-gradient(circle, rgba(255,210,26,0.16) 0%, rgba(245,0,122,0.05) 34%, transparent 68%)'
            : 'radial-gradient(circle, rgba(255,210,26,0.1) 0%, rgba(245,0,122,0.035) 38%, transparent 68%)',
          filter: 'blur(4px)',
        }}
      />
      <div
        className="pointer-events-none absolute left-1/2 top-[48%] h-px w-[82%] -translate-x-1/2"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(255,210,26,0.18), rgba(245,0,122,0.14), transparent)' }}
      />

      {/* Header row — title and language selector side-by-side */}
      <div className="relative mb-8 flex flex-wrap items-center justify-between gap-4 sm:flex-nowrap">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-gold animate-pulse" />
          <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-cream/60">
            Voice Interaction
          </span>
        </div>
        {/* Language selector beside title */}
        <div className="relative">
          <LanguageSelector value={language} onChange={onLanguageChange} />
        </div>
      </div>

      {/* Mic button with rotating text orbit */}
      <div className="relative flex justify-center py-2">
        <MicButton
          state={state}
          recorderStatus={recorderStatus}
          audioLevel={audioLevel}
          onToggle={onToggle}
          disabled={false}
          languageCode={language}
        />
      </div>

      {/* Processing stage indicator */}
      {isProcessing && (
        <div className="animate-fade-in relative mt-6 flex flex-wrap items-center justify-center gap-2">
          {PROCESSING_STAGES.map((stage, idx) => {
            const active = state === stage.state;
            return (
              <div
                key={stage.state}
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium transition-all duration-300 ${
                  active
                    ? 'bg-gold/15 text-gold ring-1 ring-gold/30'
                    : 'text-cream/40'
                }`}
              >
                <span className={`h-1.5 w-1.5 rounded-full ${active ? 'bg-gold' : 'bg-cream/30'}`} />
                {stage.label}
                {idx < PROCESSING_STAGES.length - 1 && (
                  <span className="ml-1 text-cream/20">→</span>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Recorder error */}
      {recorderError && state === 'error' && (
        <div className="animate-fade-in relative mt-6 flex items-start gap-3 rounded-2xl border border-hh-pink/30 bg-hh-pink/10 p-4">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-hh-pink-soft" strokeWidth={2} />
          <div>
            <p className="text-sm font-medium text-cream">{recorderError}</p>
            <button
              onClick={onRetry}
              className="focus-ring mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-gold hover:underline"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Try again
            </button>
          </div>
        </div>
      )}

      {/* Play answer button */}
      {canPlayAnswer && (state === 'answer' || state === 'refused') && (
        <div className="animate-fade-in relative mt-6 flex justify-center">
          <button
            onClick={onPlayAnswer}
            className="focus-ring group flex items-center gap-2.5 rounded-full border border-gold/30 bg-gold/10 px-5 py-2.5 text-sm font-medium text-cream transition-all hover:bg-gold/20"
            style={{ boxShadow: '0 0 24px rgba(255, 210, 26, 0.15)' }}
          >
            {isPlayingAnswer ? (
              <>
                <Headphones className="h-4 w-4 text-gold animate-pulse" />
                Playing answer…
              </>
            ) : (
              <>
                <Volume2 className="h-4 w-4 text-gold" />
                Play answer
              </>
            )}
          </button>
        </div>
      )}
    </section>
  );
}
