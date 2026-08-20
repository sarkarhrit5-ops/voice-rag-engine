import { Loader2, Mic, MicOff, Square } from 'lucide-react';
import type { VoiceState } from '../types';
import { LanguageTextOrbit } from './LanguageTextOrbit';
import { ArtworkDisplay } from './ArtworkDisplay';
import { getLanguageVisual } from '../config/languageVisuals';

interface MicButtonProps {
  state: VoiceState;
  recorderStatus: 'idle' | 'recording' | 'denied' | 'unsupported';
  audioLevel: number;
  onToggle: () => void;
  disabled?: boolean;
  languageCode?: string;
}

const STATE_LABELS: Record<VoiceState, string> = {
  idle: 'Tap to speak',
  listening: 'Listening…',
  processing: 'Understanding your question…',
  retrieving: 'Searching relevant knowledge…',
  verifying: 'Checking evidence…',
  answer: 'Tap to speak again',
  refused: 'Tap to speak again',
  error: 'Try again',
};

export function MicButton({
  state,
  recorderStatus,
  audioLevel,
  onToggle,
  disabled,
  languageCode = 'hi',
}: MicButtonProps) {
  const isListening = state === 'listening';
  const isProcessing =
    state === 'processing' || state === 'retrieving' || state === 'verifying';
  const isError = state === 'error' || recorderStatus === 'denied' || recorderStatus === 'unsupported';

  // Responsive sizing for artwork and orbit
  // Scale the complete composition so its orbit fits the available panel width.
  const viewportWidth = typeof window !== 'undefined' ? window.innerWidth : 1280;
  const artworkSize = viewportWidth < 640 ? 190 : viewportWidth < 1024 ? 250 : 494;
  const orbitRadius = artworkSize / 2 + 35; // Text orbit ~35px outside artwork edge
  
  const visual = getLanguageVisual(languageCode);
  const languageText = visual?.nativeName ?? '';
  const textColor = visual?.textColor ?? 'rgba(255, 210, 26, 1)';

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Voice interaction composition — artwork with rotating text orbit */}
      <div
        className="relative flex items-center justify-center preserve-3d"
        style={{
          width: orbitRadius * 2 + 40,
          height: orbitRadius * 2 + 40,
        }}
      >
        {/* Cultural artwork — no circular clipping, preserves original shape */}
        <ArtworkDisplay
          languageCode={languageCode}
          state={state}
          size={artworkSize}
        />

        {/* Language text rotating around the artwork */}
        <LanguageTextOrbit
          languageText={languageText}
          textColor={textColor}
          repeatCount={3}
          orbitRadius={orbitRadius}
          rotationSpeed={25}
          state={state}
        />

        {/* Waveform bars while listening — organic, responsive */}
        {isListening && (
          <div className="absolute flex items-center justify-center gap-[3px]" style={{ width: 120, height: 80 }}>
            {Array.from({ length: 11 }).map((_, i) => {
              const center = 5;
              const dist = Math.abs(i - center);
              const base = Math.max(0.12, 1 - dist * 0.15);
              const height = base * (0.3 + audioLevel * 0.7);
              return (
                <span
                  key={i}
                  className="w-[3px] rounded-full bg-gradient-to-t from-gold/30 to-gold"
                  style={{
                    height: `${height * 100}%`,
                    animation: `wave ${0.5 + (i % 4) * 0.12}s ease-in-out ${i * 0.04}s infinite`,
                    boxShadow: '0 0 6px rgba(255, 210, 26, 0.3)',
                  }}
                />
              );
            })}
          </div>
        )}

        {/* Knowledge retrieval particles — travel inward toward the mic */}
        {isProcessing && (
          <div className="pointer-events-none absolute inset-0" aria-hidden="true">
            {Array.from({ length: 10 }).map((_, i) => {
              const angle = (i * 36 * Math.PI) / 180;
              const r = orbitRadius - 10;
              return (
                <span
                  key={i}
                  className="absolute left-1/2 top-1/2 h-1.5 w-1.5 rounded-full"
                  style={{
                    background: i % 3 === 0 ? '#F5007A' : '#FFD21A',
                    boxShadow: '0 0 8px currentColor',
                    ['--kx' as string]: `${Math.cos(angle) * r}px`,
                    ['--ky' as string]: `${Math.sin(angle) * r}px`,
                    animation: `knowledge-inflow 2.4s cubic-bezier(0.4, 0, 0.2, 1) ${i * 0.18}s infinite`,
                  }}
                />
              );
            })}
          </div>
        )}

        {/* === The microphone button — SMALLER (60px), centered in front === */}
        <button
          type="button"
          onClick={onToggle}
          disabled={disabled || isProcessing}
          aria-label={
            isListening
              ? 'Stop recording'
              : isProcessing
                ? 'Processing your question'
                : 'Start recording'
          }
          aria-pressed={isListening}
          className={`focus-ring group relative z-10 flex items-center justify-center rounded-full transition-all duration-300 ${
            isListening ? 'scale-110' : isError ? '' : 'hover:scale-105'
          }`}
          style={{
            width: 60,
            height: 60,
            background: isError
              ? 'radial-gradient(circle at 30% 24%, rgba(255,210,26,0.18), transparent 46%), linear-gradient(145deg, #0a5a3a 0%, #063b28 58%, #042b1d 100%)'
              : isListening
                ? 'radial-gradient(circle at 30% 24%, #fff6cf 0%, transparent 52%), radial-gradient(circle at 76% 82%, rgba(245,0,122,0.32), transparent 46%), linear-gradient(145deg, #ffe566 0%, #FFD21A 55%, #d69f00 100%)'
                : 'radial-gradient(circle at 28% 22%, rgba(255,210,26,0.45) 0%, rgba(255,210,26,0.08) 34%, transparent 58%), radial-gradient(circle at 78% 84%, rgba(245,0,122,0.28) 0%, transparent 48%), linear-gradient(150deg, #0d6844 0%, #056B3A 48%, #042b1d 100%)',
            boxShadow: isListening
              ? '0 0 50px rgba(255, 210, 26, 0.5), 0 0 100px rgba(255, 210, 26, 0.15), inset 0 3px 6px rgba(255,255,255,0.45), inset 0 -3px 6px rgba(0,0,0,0.18)'
              : isProcessing
                ? '0 0 30px rgba(255, 210, 26, 0.2), inset 0 3px 6px rgba(255,255,255,0.35), inset 0 -3px 6px rgba(0,0,0,0.18)'
                : isError
                  ? '0 8px 24px rgba(245, 0, 122, 0.3), inset 0 2px 4px rgba(255,255,255,0.2), inset 0 -2px 4px rgba(0,0,0,0.2)'
                  : '0 14px 34px rgba(0, 0, 0, 0.45), 0 0 30px rgba(255, 180, 40, 0.24), 0 6px 26px rgba(245, 0, 122, 0.14), inset 0 3px 8px rgba(255,229,102,0.34), inset -3px -5px 12px rgba(245,0,122,0.14), inset 0 -5px 10px rgba(0,0,0,0.34)',
          }}
        >
          {/* Inner glass highlight */}
          <span
            className="absolute rounded-full"
            style={{
              inset: 5,
              background: 'linear-gradient(145deg, rgba(255,255,255,0.3) 0%, transparent 55%)',
              borderRadius: '50%',
            }}
          />
          {/* Outer rim ring for metallic edge */}
          <span
            className="absolute rounded-full"
            style={{
              inset: 0,
              border: '1.5px solid rgba(255,255,255,0.2)',
              borderRadius: '50%',
            }}
          />

          {isProcessing ? (
            <Loader2 className="relative h-6 w-6 animate-spin text-forest-dark" strokeWidth={2.2} />
          ) : isListening ? (
            <Square className="relative h-5 w-5 fill-forest-dark text-forest-dark" strokeWidth={2.5} />
          ) : isError ? (
            <MicOff className="relative h-6 w-6 text-cream" strokeWidth={2} />
          ) : (
            <Mic className="relative h-7 w-7 text-gold transition-transform group-hover:scale-110" strokeWidth={2} />
          )}
        </button>
      </div>

      {/* State label */}
      <div className="text-center">
        <p
          className={`font-display text-lg font-medium transition-colors duration-300 ${
            isError ? 'text-hh-pink-soft' : isListening ? 'text-gold' : 'text-cream/80'
          }`}
        >
          {STATE_LABELS[state]}
        </p>
        {isProcessing && (
          <div className="mt-2 flex items-center justify-center gap-1.5">
            <span className="dot-bounce h-1.5 w-1.5 rounded-full bg-gold/70" style={{ animationDelay: '0s' }} />
            <span className="dot-bounce h-1.5 w-1.5 rounded-full bg-gold/70" style={{ animationDelay: '0.15s' }} />
            <span className="dot-bounce h-1.5 w-1.5 rounded-full bg-gold/70" style={{ animationDelay: '0.3s' }} />
          </div>
        )}
      </div>
    </div>
  );
}
