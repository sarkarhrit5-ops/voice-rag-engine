import { useMemo } from 'react';
import type { VoiceState } from '../types';

interface OrbitalRingProps {
  state: VoiceState;
  size?: number;
}

/**
 * The signature 3D revolving "HH GOA 2026" text ring.
 * Rotates around the vertical Y axis — like a coin or wheel standing upright
 * and spinning, creating a true 3D orbital feel.
 */
export function OrbitalRing({ state, size = 320 }: OrbitalRingProps) {
  const isListening = state === 'listening';
  const isProcessing =
    state === 'processing' || state === 'retrieving' || state === 'verifying';
  const isError = state === 'error';

  const ringClass = isListening
    ? 'orbit-spin-fast'
    : isProcessing
      ? 'orbit-spin'
      : 'orbit-spin-rev';

  const ringText = useMemo(() => {
    const phrase = 'HH GOA 2026 · ';
    return phrase.repeat(4);
  }, []);

  const markers = useMemo(
    () => Array.from({ length: 8 }, (_, i) => (i / 8) * 360),
    []
  );

  const radius = size / 2 - 14;
  const center = size / 2;

  // Orbit radius for floating objects (slightly outside the ring)
  const orbitRadius = size / 2 + 18;

  return (
    <div
      className="pointer-events-none absolute inset-0 flex items-center justify-center"
      aria-hidden="true"
    >
      <div
        className="perspective-1200 relative preserve-3d"
        style={{ width: size, height: size }}
      >
        {/* === Outer 3D text ring (vertical rotation) === */}
        <div
          className={`preserve-3d absolute inset-0 ${ringClass}`}
          style={{ transformOrigin: 'center center' }}
        >
          <svg
            width={size}
            height={size}
            viewBox={`0 0 ${size} ${size}`}
            className="absolute inset-0"
          >
            <defs>
              <linearGradient id="ring-edge" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#FFF4D6" stopOpacity="0.8" />
                <stop offset="35%" stopColor="#FFD21A" stopOpacity="0.95" />
                <stop offset="72%" stopColor="#F5007A" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#056B3A" stopOpacity="0.85" />
              </linearGradient>
              <filter id="ring-shadow">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0.98 0 1 0 0 0.7 0 0 1 0 0.1 0 0 0 0.55 0" />
              </filter>
              <path
                id="orbit-text-path"
                d={`M ${center},${center - radius} a ${radius},${radius} 0 1,1 -0.01,0`}
                fill="none"
              />
              <linearGradient id="ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#FFD21A" />
                <stop offset="50%" stopColor="#ffe566" />
                <stop offset="100%" stopColor="#FFD21A" />
              </linearGradient>
              <filter id="ring-glow">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Ring track */}
            <circle
              cx={center}
              cy={center}
              r={radius}
              fill="none"
              stroke="#FFD21A"
              strokeWidth={isListening ? 11 : isProcessing ? 8 : 6}
              opacity={isError ? 0.12 : isListening ? 0.16 : 0.1}
              filter="url(#ring-shadow)"
            />
            <circle
              cx={center}
              cy={center}
              r={radius}
              fill="none"
              stroke="url(#ring-edge)"
              strokeWidth={isListening ? 3.5 : 2.5}
              opacity={isError ? 0.35 : isListening ? 0.95 : isProcessing ? 0.85 : 0.72}
              filter="url(#ring-glow)"
            />
            {/* Bevel: inner + outer edges */}
            <circle cx={center} cy={center} r={radius - 8} fill="none" stroke="#FFF4D6" strokeWidth="0.65" opacity={isListening ? 0.35 : 0.18} />
            <circle cx={center} cy={center} r={radius + 8} fill="none" stroke="#056B3A" strokeWidth="1.5" opacity={isError ? 0.2 : 0.65} />
            <circle cx={center} cy={center} r={radius + 11} fill="none" stroke="#F5007A" strokeWidth="0.75" strokeDasharray="1 22" opacity={isError ? 0.12 : 0.45} />

            {/* Text following the circular path */}
            <text
              fill={isError ? '#FFF4D6' : '#FFD21A'}
              fontSize="14"
              fontWeight="700"
              letterSpacing="3.5"
              filter="url(#ring-glow)"
              opacity={isError ? 0.5 : 0.92}
            >
              <textPath href="#orbit-text-path" startOffset="0">
                {ringText}
              </textPath>
            </text>

            {/* Decorative markers */}
            {markers.map((angle, i) => {
              const rad = (angle * Math.PI) / 180;
              const mx = center + Math.cos(rad) * radius;
              const my = center + Math.sin(rad) * radius;
              const isPink = i % 4 === 0 && i !== 0;
              return (
                <circle
                  key={i}
                  cx={mx}
                  cy={my}
                  r={isPink ? 3.5 : 2.5}
                  fill={isPink ? '#F5007A' : '#FFD21A'}
                  opacity={isPink ? 0.75 : 0.55}
                />
              );
            })}
          </svg>
        </div>

        {/* === Environmental contact shadow + gold light spill onto the card === */}
        <div
          className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full"
          style={{
            width: size * 1.05,
            height: size * 1.05,
            background:
              'radial-gradient(circle, rgba(255,210,26,0.09) 0%, rgba(245,0,122,0.04) 42%, transparent 66%)',
            filter: 'blur(18px)',
            opacity: isError ? 0.4 : isListening ? 1 : 0.7,
            transition: 'opacity 500ms ease',
          }}
        />
        <div
          className="pointer-events-none absolute left-1/2 rounded-[50%]"
          style={{
            width: size * 0.62,
            height: 22,
            bottom: -6,
            transform: 'translateX(-50%)',
            background: 'radial-gradient(ellipse, rgba(0,0,0,0.45) 0%, transparent 72%)',
            filter: 'blur(8px)',
          }}
        />

        {/* === Light trail sweeping behind the ring === */}
        <div
          className={`pointer-events-none absolute inset-0 ${isListening ? 'ring-trail-fast' : 'ring-trail'}`}
          style={{ transformOrigin: 'center center' }}
        >
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="absolute inset-0">
            <defs>
              <linearGradient id="trail-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#FFD21A" stopOpacity="0" />
                <stop offset="70%" stopColor="#FFD21A" stopOpacity="0.28" />
                <stop offset="100%" stopColor="#FFF4D6" stopOpacity="0.6" />
              </linearGradient>
            </defs>
            <path
              d={`M ${center + radius},${center} A ${radius},${radius} 0 0,0 ${center - radius},${center}`}
              fill="none"
              stroke="url(#trail-grad)"
              strokeWidth={isListening ? 6 : 4}
              strokeLinecap="round"
              opacity={isError ? 0.25 : 0.8}
              style={{ filter: 'blur(2px)' }}
            />
          </svg>
        </div>

        {/* === Secondary thin green/pink orbital layer (different tilt + speed) === */}
        <div
          className="preserve-3d absolute inset-0 orbit-spin-inner"
          style={{ transformOrigin: 'center center', animationDuration: '52s' }}
        >
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="absolute inset-0">
            <circle cx={center} cy={center} r={radius - 18} fill="none" stroke="#056B3A" strokeWidth="2.5" opacity="0.55" />
            <circle cx={center} cy={center} r={radius - 18} fill="none" stroke="#F5007A" strokeWidth="0.9" strokeDasharray="2 14" opacity="0.5" />
          </svg>
        </div>

        {/* === Inner counter-rotating ring for depth === */}
        <div
          className="preserve-3d absolute inset-0 orbit-spin-inner"
          style={{ transformOrigin: 'center center' }}
        >
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="absolute inset-0">
            <circle cx={center} cy={center} r={radius - 30} fill="none" stroke="#FFD21A" strokeWidth="1" opacity="0.22" strokeDasharray="4 8" />
          </svg>
        </div>

        {/* === Processing scan beam === */}
        {isProcessing && (
          <div className="preserve-3d absolute inset-0 orbit-scan" style={{ transformOrigin: 'center center' }}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="absolute inset-0">
              <defs>
                <linearGradient id="scan-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#FFD21A" stopOpacity="0" />
                  <stop offset="50%" stopColor="#FFD21A" stopOpacity="0.7" />
                  <stop offset="100%" stopColor="#FFD21A" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path
                d={`M ${center - radius},${center} A ${radius},${radius} 0 0,1 ${center + radius},${center}`}
                fill="none"
                stroke="url(#scan-grad)"
                strokeWidth="5"
              />
            </svg>
          </div>
        )}

        {/* === Listening pulse glow === */}
        {isListening && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="animate-pulse rounded-full"
              style={{
                width: size * 0.7,
                height: size * 0.7,
                background: 'radial-gradient(circle, rgba(255,210,26,0.15) 0%, transparent 70%)',
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
