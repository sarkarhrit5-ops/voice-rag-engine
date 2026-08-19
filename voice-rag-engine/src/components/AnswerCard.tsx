import { useState } from 'react';
import { ChevronDown, FileText, ShieldCheck, ShieldX, Sparkles, Volume2 } from 'lucide-react';
import type { SourceItem } from '../types';
import { GroundingBadge } from './GroundingBadge';

interface AnswerCardProps {
  answer: string;
  grounded: boolean;
  confidence?: number;
  sources?: SourceItem[];
  reason?: string;
  isDemo?: boolean;
  canPlayAnswer?: boolean;
  isPlayingAnswer?: boolean;
  onPlayAnswer?: () => void;
}

export function AnswerCard({
  answer,
  grounded,
  confidence,
  sources = [],
  reason,
  isDemo,
  canPlayAnswer,
  isPlayingAnswer,
  onPlayAnswer,
}: AnswerCardProps) {
  const [showSources, setShowSources] = useState(false);
  const hasSources = sources.length > 0;

  return (
    <div
      className="surface-cream-3d animate-fade-up rounded-3xl border border-gold/30 p-6 sm:p-7"
      style={{ animationDelay: '0.1s' }}
    >
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-forest" strokeWidth={2.5} />
          <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-forest/60">
            Answer
          </span>
        </div>
        <div className="flex items-center gap-2">
          {canPlayAnswer && onPlayAnswer && (
            <button
              onClick={onPlayAnswer}
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition-all ${
                isPlayingAnswer
                  ? 'border-forest bg-forest text-cream animate-pulse'
                  : 'border-forest/20 bg-forest/5 text-forest hover:border-forest/40 hover:bg-forest/10'
              }`}
              title={isPlayingAnswer ? 'Stop audio' : 'Listen to audio response'}
            >
              <Volume2 className="h-3.5 w-3.5" />
              <span>{isPlayingAnswer ? 'Playing...' : 'Listen'}</span>
            </button>
          )}
          {isDemo && (
            <span className="rounded-full border border-hh-pink/30 bg-hh-pink/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-hh-pink">
              Demo
            </span>
          )}
        </div>
      </div>

      <p className="font-display text-xl leading-relaxed text-forest-dark sm:text-2xl">
        {answer}
      </p>

      {/* Grounding status */}
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <GroundingBadge grounded={grounded} />
        {typeof confidence === 'number' && (
          <span className="rounded-full bg-forest/5 px-3 py-1 text-xs font-medium text-forest/70">
            Confidence {Math.round(confidence * 100)}%
          </span>
        )}
      </div>

      {!grounded && reason && (
        <p className="mt-3 text-sm text-forest/60">{reason}</p>
      )}

      {/* Sources — evidence cards */}
      {hasSources && (
        <div className="mt-5 border-t border-forest/10 pt-4">
          <button
            onClick={() => setShowSources((v) => !v)}
            className="focus-ring flex w-full items-center justify-between text-left"
            aria-expanded={showSources}
          >
            <span className="flex items-center gap-2 text-sm font-semibold text-forest">
              <FileText className="h-4 w-4" strokeWidth={2.2} />
              View sources
              <span className="text-forest/50">({sources.length})</span>
            </span>
            <ChevronDown
              className={`h-4 w-4 text-forest/50 transition-transform duration-200 ${showSources ? 'rotate-180' : ''}`}
            />
          </button>

          {showSources && (
            <div className="animate-fade-in mt-3 space-y-2.5">
              {sources.map((src, i) => (
                <div
                  key={src.id ?? i}
                  className="rounded-2xl border border-forest/10 bg-white/40 p-3.5 transition-all hover:border-gold/40 hover:shadow-sm"
                  style={{
                    background:
                      'linear-gradient(145deg, rgba(255,255,255,0.5) 0%, rgba(255,244,214,0.3) 100%)',
                  }}
                >
                  <div className="flex items-start gap-2.5">
                    <span
                      className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-forest"
                      style={{
                        background: 'linear-gradient(145deg, #FFD21A 0%, #e8b800 100%)',
                        boxShadow: '0 2px 6px rgba(255,210,26,0.3)',
                      }}
                    >
                      {i + 1}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-forest-dark">{src.title}</p>
                      {src.reference && (
                        <p className="mt-0.5 text-xs font-medium text-forest/50">{src.reference}</p>
                      )}
                      {src.snippet && (
                        <p className="mt-1.5 text-sm leading-relaxed text-forest/70 line-clamp-2">
                          {src.snippet}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Grounding explanation */}
      <div
        className="mt-5 flex items-start gap-2.5 rounded-2xl p-3.5"
        style={{
          background: grounded
            ? 'linear-gradient(145deg, rgba(5,107,58,0.06) 0%, rgba(5,107,58,0.02) 100%)'
            : 'linear-gradient(145deg, rgba(245,0,122,0.06) 0%, rgba(245,0,122,0.02) 100%)',
        }}
      >
        {grounded ? (
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-forest" strokeWidth={2.5} />
        ) : (
          <ShieldX className="mt-0.5 h-4 w-4 shrink-0 text-hh-pink" strokeWidth={2.5} />
        )}
        <p className="text-xs leading-relaxed text-forest/70">
          {grounded
            ? 'Grounded in retrieved context. The answer is supported by the sources shown above.'
            : 'Not enough evidence. The system only answers when the retrieved context provides sufficient support.'}
        </p>
      </div>
    </div>
  );
}
