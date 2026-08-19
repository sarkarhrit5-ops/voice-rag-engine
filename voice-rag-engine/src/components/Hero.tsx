import { ShieldCheck, Sparkles, Waves } from 'lucide-react';
import { DecorativePattern } from './DecorativePattern';

const BADGES = ['Voice', 'RAG', 'Grounded AI'];

export function Hero() {
  return (
    <div id="about" className="relative">
      {/* === 3D floating decorative elements === */}
      {/* Floating golden geometric panel */}
      <div
        className="pointer-events-none absolute -right-4 top-0 hidden lg:block animate-drift-1"
        style={{
          width: 64,
          height: 64,
          background: 'linear-gradient(145deg, rgba(255,210,26,0.12) 0%, rgba(255,210,26,0.02) 100%)',
          border: '1px solid rgba(255,210,26,0.2)',
          borderRadius: '16px',
          transform: 'perspective(600px) rotateY(15deg) rotateX(5deg)',
          boxShadow: '0 8px 32px -8px rgba(255,210,26,0.15)',
        }}
      >
        <div className="flex h-full items-center justify-center">
          <span className="font-display text-2xl text-gold/30">✦</span>
        </div>
      </div>

      {/* Floating pink diamond accent */}
      <div
        className="pointer-events-none absolute right-12 top-32 hidden lg:block animate-drift-2"
        style={{
          width: 28,
          height: 28,
          background: 'linear-gradient(145deg, rgba(245,0,122,0.2) 0%, rgba(245,0,122,0.05) 100%)',
          border: '1px solid rgba(245,0,122,0.3)',
          transform: 'rotate(45deg)',
          boxShadow: '0 4px 20px -4px rgba(245,0,122,0.2)',
        }}
      />

      {/* Floating golden dots cluster */}
      <div className="pointer-events-none absolute -left-6 top-44 hidden lg:block">
        <div className="grid animate-drift-3 grid-cols-3 gap-2">
          {Array.from({ length: 9 }).map((_, i) => (
            <span
              key={i}
              className="h-1.5 w-1.5 rounded-full bg-gold/40"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>

      {/* Small floating ring */}
      <div
        className="pointer-events-none absolute -left-10 top-24 hidden lg:block animate-float-slow"
        style={{
          width: 48,
          height: 48,
          border: '1.5px solid rgba(255,210,26,0.25)',
          borderRadius: '50%',
          transform: 'perspective(400px) rotateX(60deg)',
        }}
      />

      {/* Floating tiny sun motif */}
      <div className="pointer-events-none absolute right-20 top-64 hidden lg:block animate-bob">
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none" className="animate-ray-spin">
          {Array.from({ length: 8 }).map((_, i) => {
            const a = (i * 45 * Math.PI) / 180;
            return (
              <line
                key={i}
                x1={18 + Math.cos(a) * 10}
                y1={18 + Math.sin(a) * 10}
                x2={18 + Math.cos(a) * 16}
                y2={18 + Math.sin(a) * 16}
                stroke="#FFD21A"
                strokeWidth="1"
                strokeLinecap="round"
                opacity="0.4"
              />
            );
          })}
          <circle cx="18" cy="18" r="5" fill="none" stroke="#FFD21A" strokeWidth="1" opacity="0.3" />
        </svg>
      </div>

      {/* Floating wave curve (Goa-inspired) */}
      <div className="pointer-events-none absolute -right-8 top-72 hidden lg:block animate-drift-3">
        <svg width="48" height="20" viewBox="0 0 48 20" fill="none">
          <path
            d="M2 14 Q 12 4, 22 14 T 46 10"
            stroke="#FFD21A"
            strokeWidth="1.5"
            strokeLinecap="round"
            opacity="0.3"
            fill="none"
          />
          <path
            d="M2 18 Q 12 8, 22 18 T 46 14"
            stroke="#F5007A"
            strokeWidth="1"
            strokeLinecap="round"
            opacity="0.2"
            fill="none"
          />
        </svg>
      </div>

      {/* Floating palm-leaf shape */}
      <div className="pointer-events-none absolute left-16 top-80 hidden lg:block animate-drift-2">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <path
            d="M16 2 C 8 8, 6 18, 16 30 C 26 18, 24 8, 16 2 Z"
            fill="rgba(5,107,58,0.3)"
            stroke="#FFD21A"
            strokeWidth="1"
            opacity="0.4"
          />
        </svg>
      </div>

      {/* Eyebrow */}
      <div className="relative mb-5 inline-flex items-center gap-2 rounded-full border border-gold/20 bg-forest/30 px-3.5 py-1.5 backdrop-blur-sm">
        <span className="h-1.5 w-1.5 rounded-full bg-gold animate-pulse" />
        <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-cream/70">
          HH Goa 2026 · Voice Intelligence
        </span>
      </div>

      {/* Headline */}
      <h1 className="relative font-display text-4xl font-semibold leading-[1.1] tracking-tight text-cream sm:text-5xl lg:text-6xl">
        Speak to knowledge.
        <br />
        <span className="relative inline-block">
          Get answers you can
          <span className="relative whitespace-nowrap text-gold">
            {' '}trust.
            <svg
              className="absolute -bottom-1.5 left-0 w-full"
              viewBox="0 0 200 10"
              fill="none"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <path
                d="M2 6 Q 50 1, 100 5 T 198 4"
                stroke="#FFD21A"
                strokeWidth="2.5"
                strokeLinecap="round"
                className="animate-draw-line"
              />
              <circle cx="198" cy="4" r="3" fill="#F5007A" opacity="0.7" />
            </svg>
          </span>
        </span>
      </h1>

      {/* Supporting text */}
      <p className="relative mt-6 max-w-xl text-base leading-relaxed text-cream/65 sm:text-lg">
        A multilingual voice-enabled RAG engine that retrieves relevant knowledge,
        verifies the evidence, and answers without inventing facts.
      </p>

      {/* Badges */}
      <div className="relative mt-7 flex flex-wrap gap-2.5">
        {BADGES.map((badge, i) => (
          <span
            key={badge}
            className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-semibold uppercase tracking-wider backdrop-blur-sm ${i === 0
                ? 'border border-gold/30 bg-gold/10 text-gold'
                : i === 1
                  ? 'border border-cream/15 bg-cream/5 text-cream/70'
                  : 'border border-hh-pink/25 bg-hh-pink/10 text-hh-pink-soft'
              }`}
          >
            {i === 0 && <Waves className="h-3 w-3" strokeWidth={2.5} />}
            {i === 1 && <Sparkles className="h-3 w-3" strokeWidth={2.5} />}
            {i === 2 && <ShieldCheck className="h-3 w-3" strokeWidth={2.5} />}
            {badge}
          </span>
        ))}
      </div>

      {/* Microcopy */}
      <p className="relative mt-8 font-display text-sm italic text-cream/40">
        Ask naturally. Ground your answers.
      </p>

      {/* Decorative ornament */}
      <div className="pointer-events-none absolute -left-10 top-24 hidden lg:block">
        <DecorativePattern
          variant="ornament"
          className="animate-spin-slower h-40 w-40 opacity-50"
        />
      </div>
    </div>
  );
}
