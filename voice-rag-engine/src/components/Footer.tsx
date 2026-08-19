import { Mic } from 'lucide-react';

export function Footer() {
  return (
    <footer
      className="relative mt-16 border-t border-gold/10"
      style={{
        background:
          'linear-gradient(180deg, rgba(4,43,29,0.6) 0%, rgba(4,43,29,0.9) 100%)',
      }}
    >
      <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          <a
            href="https://hhgoa.com/"
            target="_blank"
            rel="noopener noreferrer"
            title="HH GOA | Hacker House Goa 2026"
            className="group flex items-center gap-3 transition-opacity hover:opacity-90"
          >
            <img
              src="/hh-logo.png"
              alt="HH GOA | Hacker House Goa 2026"
              className="h-9 w-9 rounded-xl object-contain shadow-md transition-all group-hover:scale-105 border border-gold/30 p-0.5"
              style={{
                background: 'rgba(6, 59, 40, 0.9)',
                boxShadow: '0 0 10px rgba(255, 210, 26, 0.15)',
              }}
            />
            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cream/40 transition-colors group-hover:text-gold">
                HH Goa 2026
              </div>
              <div className="font-display text-base font-semibold text-cream">
                Voice RAG
              </div>
            </div>
          </a>

          <p className="text-center text-xs text-cream/40">
            Built for Hacker House Goa ·{' '}
            <span className="text-cream/60">Voice · Retrieval · Grounded Generation</span>
          </p>

          <div className="flex flex-col items-center gap-3 sm:items-end">
            <div className="flex items-center gap-4 text-[10px] font-semibold uppercase tracking-wider text-cream/30">
              <span>Ground your answers</span>
              <span className="h-1 w-1 rounded-full bg-gold/40" />
              <span>Knowledge, with evidence</span>
            </div>
            <div className="flex items-center gap-2">
              <span
                className="inline-flex items-center gap-1.5 rounded-full border border-gold/25 px-2.5 py-1 text-[9px] font-semibold uppercase tracking-wider text-gold"
                style={{ background: 'rgba(255,210,26,0.06)' }}
              >
                HH Goa 2026 · Voice Intelligence
              </span>
              <span
                className="inline-flex items-center gap-1.5 rounded-full border border-hh-pink/25 px-2.5 py-1 text-[9px] font-semibold uppercase tracking-wider text-hh-pink-soft"
                style={{ background: 'rgba(245,0,122,0.06)' }}
              >
                Built for HH Goa Hackathon
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
