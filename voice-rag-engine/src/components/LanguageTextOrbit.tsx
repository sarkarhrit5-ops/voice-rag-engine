import type { VoiceState } from '../types';

interface LanguageTextOrbitProps {
  languageText: string;
  textColor?: string;
  repeatCount?: number;
  orbitRadius: number;
  rotationSpeed?: number; // in seconds
  state?: VoiceState;
}

/**
 * Reusable rotating text orbit component
 * Displays language text repeated around a circular path
 * Can be customized for different languages and styles
 */
export function LanguageTextOrbit({
  languageText,
  textColor = 'rgba(255, 210, 26, 1)', // Default: bright pinkish-gold
  repeatCount = 3,
  orbitRadius,
  rotationSpeed = 25,
  state = 'idle',
}: LanguageTextOrbitProps) {
  const isListening = state === 'listening';

  // Keep only a small text-safe margin around the mathematical orbit.
  const svgSize = orbitRadius * 2 + 40;
  const center = svgSize / 2;
  const textRadius = orbitRadius;

  return (
    <div
      className="pointer-events-none absolute inset-0 flex items-center justify-center"
      aria-hidden="true"
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {/* Rotating text orbit container */}
      <div
        style={{
          width: svgSize,
          height: svgSize,
          animation: `rotate-text-orbit ${rotationSpeed}s linear infinite`,
          transformOrigin: 'center center',
        }}
      >
        <svg
          width={svgSize}
          height={svgSize}
          viewBox={`0 0 ${svgSize} ${svgSize}`}
          style={{ overflow: 'visible' }}
          aria-hidden="true"
        >
          <defs>
            {/* Circular path for text */}
            <path
              id={`orbit-text-path-${orbitRadius}`}
              d={`M ${center},${center - textRadius} a ${textRadius},${textRadius} 0 1,1 -0.01,0`}
              fill="none"
            />
          </defs>

          {/* Text repeated around the orbit */}
          <text
            style={{
              fontSize: '13px',
              fontWeight: '700',
              letterSpacing: '2px',
              fill: textColor,
              filter: `drop-shadow(0 2px 6px rgba(0, 0, 0, 0.6))`,
              paintOrder: 'stroke fill',
              stroke: 'rgba(0, 0, 0, 0.3)',
              strokeWidth: '0.4px',
            }}
          >
            {Array.from({ length: repeatCount }).map((_, i) => {
              const segmentLength = 100 / repeatCount;
              const startOffset = (i * segmentLength) % 100;

              return (
                <textPath
                  key={i}
                  href={`#orbit-text-path-${orbitRadius}`}
                  startOffset={`${startOffset}%`}
                  textAnchor={i === 0 ? 'start' : i === repeatCount - 1 ? 'end' : 'middle'}
                >
                  {languageText}
                  {i < repeatCount - 1 && ' · '}
                </textPath>
              );
            })}
          </text>
        </svg>
      </div>

      {/* Glow effect when listening */}
      {isListening && (
        <div
          className="absolute pointer-events-none"
          style={{
            width: svgSize + 20,
            height: svgSize + 20,
            background:
              'radial-gradient(circle, rgba(255,210,26,0.15) 0%, transparent 70%)',
            borderRadius: '50%',
          }}
        />
      )}
    </div>
  );
}
