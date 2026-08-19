import { Mic, ShieldCheck } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'About', href: '#about' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Performance', href: '#performance' },
];

export function Header() {
  return (
    <header
      className="sticky top-0 z-40 border-b border-gold/10 backdrop-blur-md"
      style={{ background: 'rgba(6, 59, 40, 0.85)' }}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
        <a href="#top" className="group flex items-center gap-3">
          <div
            className="relative flex h-10 w-10 items-center justify-center rounded-xl transition-all group-hover:scale-105"
            style={{
              background:
                'linear-gradient(145deg, rgba(255,210,26,0.15) 0%, rgba(255,210,26,0.05) 100%)',
              boxShadow:
                '0 1px 0 0 rgba(255,210,26,0.15) inset, 0 4px 12px -4px rgba(255,210,26,0.1)',
            }}
          >
            <Mic className="h-5 w-5 text-gold" strokeWidth={2.2} />
          </div>
          <div className="leading-tight">
            <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cream/50">
              HH Goa 2026
            </div>
            <div className="font-display text-lg font-semibold text-cream">
              Voice RAG
            </div>
          </div>
        </a>

        <nav className="hidden items-center gap-8 md:flex">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="focus-ring relative text-sm font-medium text-cream/70 transition-colors hover:text-cream"
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div
          className="flex items-center gap-2 rounded-full border border-gold/20 px-3 py-1.5"
          style={{
            background:
              'linear-gradient(145deg, rgba(5,107,58,0.4) 0%, rgba(5,107,58,0.2) 100%)',
            boxShadow: '0 1px 0 0 rgba(255,210,26,0.08) inset',
          }}
        >
          <ShieldCheck className="h-3.5 w-3.5 text-gold" strokeWidth={2.5} />
          <span className="hidden text-[11px] font-semibold uppercase tracking-wider text-cream/80 sm:inline">
            Grounded AI
          </span>
        </div>
      </div>
    </header>
  );
}
