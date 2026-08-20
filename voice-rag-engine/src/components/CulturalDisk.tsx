import type { VoiceState } from '../types';

interface CulturalDiskProps {
  state: VoiceState;
  size?: number;
}

/**
 * Large rotating cultural disk with Assam artwork
 * Features high-opacity image without text (text moved to external orbit)
 * Size: 540px desktop, 380px mobile (110-120% larger)
 */
export function CulturalDisk({ state, size = 540 }: CulturalDiskProps) {
  const isListening = state === 'listening';
  const isProcessing =
    state === 'processing' || state === 'retrieving' || state === 'verifying';
  return (
    <div
      className="pointer-events-none absolute inset-0 flex items-center justify-center"
      aria-hidden="true"
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {/* Outer rotating container — provides the rotation animation */}
      <div
        className="relative animate-cultural-disk-slow"
        style={{
          width: size,
          height: size,
          transformOrigin: 'center center',
        }}
      >
        {/* Circular image container with high opacity */}
        <div
          className="absolute rounded-full overflow-hidden"
          style={{
            inset: 0,
            width: '100%',
            height: '100%',
            // Subtle but visible glow/shadow
            boxShadow: isListening
              ? 'inset 0 0 40px rgba(0, 0, 0, 0.3), 0 0 50px rgba(255, 210, 26, 0.25)'
              : isProcessing
                ? 'inset 0 0 30px rgba(0, 0, 0, 0.25), 0 0 35px rgba(255, 210, 26, 0.15)'
                : 'inset 0 0 25px rgba(0, 0, 0, 0.2), 0 0 25px rgba(255, 210, 26, 0.1)',
          }}
        >
          {/* Assam cultural artwork — HIGH OPACITY: 92% */}
          <img
            src="/assam.png"
            alt="Assam cultural artwork"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center',
              opacity: 0.92,
              display: 'block',
            }}
            loading="eager"
            decoding="sync"
          />
        </div>
      </div>

      {/* Glow effect when listening */}
      {isListening && (
        <div
          className="absolute pointer-events-none"
          style={{
            width: size + 30,
            height: size + 30,
            background:
              'radial-gradient(circle, rgba(255,210,26,0.2) 0%, transparent 70%)',
            borderRadius: '50%',
          }}
        />
      )}
    </div>
  );
}
