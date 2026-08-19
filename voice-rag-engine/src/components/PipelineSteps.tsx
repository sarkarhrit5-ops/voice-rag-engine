import { Database, Mic2, ShieldCheck, Sparkles } from 'lucide-react';

const STEPS = [
  { icon: Mic2, title: 'Speak', description: 'Ask naturally in your language.' },
  { icon: Database, title: 'Retrieve', description: 'Search the relevant knowledge context.' },
  { icon: ShieldCheck, title: 'Verify', description: 'Reject unsupported answers.' },
  { icon: Sparkles, title: 'Answer', description: 'Respond using grounded evidence.' },
];

export function PipelineSteps() {
  return (
    <section id="how-it-works" className="relative">
      <div className="mb-8 flex items-center gap-3">
        <span className="text-[11px] font-semibold uppercase tracking-[0.2em] text-gold/70">
          How it works
        </span>
        <div className="h-px flex-1 bg-gradient-to-r from-gold/30 to-transparent" />
      </div>

      <div className="relative">
        {/* === Glowing flowing connector line (desktop) === */}
        <div className="absolute left-0 right-0 top-[52px] hidden lg:block">
          <svg className="w-full" height="4" preserveAspectRatio="none" viewBox="0 0 1000 4" fill="none">
            <defs>
              <linearGradient id="pipe-flow" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#FFD21A" stopOpacity="0.3" />
                <stop offset="50%" stopColor="#FFD21A" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#F5007A" stopOpacity="0.3" />
              </linearGradient>
            </defs>
            <line x1="40" y1="2" x2="960" y2="2" stroke="url(#pipe-flow)" strokeWidth="2" strokeDasharray="6 4">
              <animate attributeName="stroke-dashoffset" values="0;-20" dur="2s" repeatCount="indefinite" />
            </line>
          </svg>

          {/* Traveling data particle */}
          <div className="relative h-0">
            <div
              className="absolute h-2 w-2 rounded-full"
              style={{
                background: '#FFD21A',
                boxShadow: '0 0 8px #FFD21A, 0 0 16px rgba(255,210,26,0.4)',
                animation: 'pipeline-flow 4s linear infinite',
                offsetPath: 'path("M 40 0 L 960 0")',
                left: 0,
              }}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step, i) => (
            <div key={step.title} className="group relative">
              <div
                className="relative h-full overflow-hidden rounded-3xl border border-cream/10 p-5 transition-all duration-300 group-hover:border-gold/40 group-hover:-translate-y-1.5"
                style={{
                  background:
                    'linear-gradient(145deg, rgba(6,59,40,0.6) 0%, rgba(4,43,29,0.85) 100%)',
                  boxShadow:
                    '0 1px 0 0 rgba(255,210,26,0.08) inset, 0 -1px 0 0 rgba(0,0,0,0.2) inset, 0 16px 40px -20px rgba(0,0,0,0.6)',
                  backdropFilter: 'blur(8px)',
                }}
              >
                {/* Internal glow on hover */}
                <div
                  className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                  style={{ background: 'radial-gradient(circle at 50% 0%, rgba(255,210,26,0.08) 0%, transparent 60%)' }}
                />

                {/* Technical micro-detail: corner bracket */}
                <svg className="pointer-events-none absolute right-3 top-3 opacity-30" width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M14 0 L14 5 M14 0 L9 0" stroke="#FFD21A" strokeWidth="1" />
                </svg>

                <div className="relative mb-4 flex items-center justify-between">
                  <div
                    className="flex h-12 w-12 items-center justify-center rounded-2xl transition-all duration-300 group-hover:scale-110"
                    style={{
                      background:
                        'linear-gradient(145deg, rgba(255,210,26,0.18) 0%, rgba(255,210,26,0.06) 100%)',
                      boxShadow:
                        '0 1px 0 0 rgba(255,210,26,0.2) inset, 0 4px 16px -4px rgba(255,210,26,0.15)',
                    }}
                  >
                    <step.icon className="h-5 w-5 text-gold transition-transform duration-300 group-hover:scale-110" strokeWidth={2} />
                  </div>
                  <span
                    className="font-display text-3xl font-semibold transition-colors duration-300 group-hover:text-gold/40"
                    style={{ color: 'rgba(255,244,214,0.12)' }}
                  >
                    {String(i + 1).padStart(2, '0')}
                  </span>
                </div>
                <h3 className="relative font-display text-lg font-semibold text-cream">
                  {step.title}
                </h3>
                <p className="relative mt-1 text-sm leading-relaxed text-cream/55">
                  {step.description}
                </p>

                {/* Bottom accent line */}
                <div
                  className="absolute bottom-0 left-0 h-0.5 w-0 transition-all duration-500 group-hover:w-full"
                  style={{ background: 'linear-gradient(90deg, #FFD21A, #F5007A)' }}
                />
              </div>

              {/* Connector node dot on the line */}
              <div
                className="absolute left-1/2 top-[48px] hidden h-3 w-3 -translate-x-1/2 rounded-full lg:block"
                style={{
                  background: '#FFD21A',
                  boxShadow: '0 0 8px rgba(255,210,26,0.5)',
                  border: '2px solid #063B28',
                }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
