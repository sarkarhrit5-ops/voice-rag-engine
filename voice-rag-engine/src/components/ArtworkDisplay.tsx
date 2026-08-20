import { useEffect, useState } from 'react';
import type { VoiceState } from '../types';
import { getLanguageVisual } from '../config/languageVisuals';

interface ArtworkDisplayProps {
  languageCode: string;
  state: VoiceState;
  size?: number; // Desktop artwork size in pixels
}

/**
 * Displays cultural artwork without circular clipping.
 * 
 * - Preserves original artwork shape (may be irregular, not perfectly circular)
 * - Renders artwork at its natural aspect ratio
 * - Handles responsive sizing
 * - Smooth fade transitions when language changes
 * - Centered behind the microphone
 */
export function ArtworkDisplay({
  languageCode,
  state,
  size = 420,
}: ArtworkDisplayProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [prevLanguageCode, setPrevLanguageCode] = useState(languageCode);
  const [fadeOut, setFadeOut] = useState(false);

  const visual = getLanguageVisual(languageCode);

  // Detect language change and trigger fade transition
  useEffect(() => {
    if (languageCode !== prevLanguageCode) {
      setFadeOut(true);
      const fadeTimer = setTimeout(() => {
        setPrevLanguageCode(languageCode);
        setFadeOut(false);
        setIsLoading(true);
      }, 150);
      return () => clearTimeout(fadeTimer);
    }
  }, [languageCode, prevLanguageCode]);

  const isListening = state === 'listening';
  const isProcessing =
    state === 'processing' || state === 'retrieving' || state === 'verifying';

  if (!visual) {
    return null;
  }

  return (
    <div
      className="pointer-events-none absolute inset-0 flex items-center justify-center"
      aria-hidden="true"
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {/* Artwork container — NO circular clipping */}
      <div
        className={`relative transition-opacity duration-200 animate-cultural-disk-slow ${fadeOut ? 'opacity-0' : 'opacity-100'}`}
        style={{
          width: size,
          height: size,
        }}
      >
        {/* Cultural artwork image — PRESERVE ORIGINAL SHAPE */}
        <img
          src={visual.imageAsset}
          alt={`${visual.nativeName} cultural artwork`}
          onLoad={() => setIsLoading(false)}
          style={{
            width: '100%',
            height: '100%',
            opacity: 0.92,
            objectFit: 'contain', // Preserve aspect ratio, no cropping
            objectPosition: 'center',
            display: 'block',
            filter: isListening
              ? 'drop-shadow(0 0 18px rgba(255, 210, 26, 0.25))'
              : isProcessing
                ? 'drop-shadow(0 0 14px rgba(255, 210, 26, 0.18))'
                : 'drop-shadow(0 0 10px rgba(255, 210, 26, 0.12))',
            // Smooth transition when artwork changes
            transition: 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
      </div>

      {/* Loading indicator (optional fallback) */}
      {isLoading && (
        <div
          className="absolute animate-pulse"
          style={{
            width: size * 0.15,
            height: size * 0.15,
            background: 'radial-gradient(circle, rgba(255, 210, 26, 0.4), transparent)',
            borderRadius: '50%',
          }}
          aria-hidden="true"
        />
      )}
    </div>
  );
}
