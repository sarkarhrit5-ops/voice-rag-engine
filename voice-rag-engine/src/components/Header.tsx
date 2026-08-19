import { useState, useEffect } from 'react';
import { Info, X, Sparkles, Cpu, Mic, Volume2, ShieldCheck, ExternalLink, ArrowRight } from 'lucide-react';

export function Header() {
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'about' | 'how-it-works'>('about');

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setShowModal(false);
    }
    if (showModal) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [showModal]);

  const scrollToSection = (id: string) => {
    setShowModal(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header
      className="sticky top-0 z-40 border-b border-gold/10 backdrop-blur-md"
      style={{ background: 'rgba(6, 59, 40, 0.85)' }}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
        <a href="#top" className="group flex items-center gap-3 transition-opacity hover:opacity-90">
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
          <div className="font-display text-xl font-semibold text-cream tracking-tight">
            Voice RAG
          </div>
        </a>

        {/* Middle Brand Banner */}
        <a
          href="https://hhgoa.com/"
          target="_blank"
          rel="noopener noreferrer"
          title="HH GOA | Hacker House Goa 2026"
          className="flex items-center justify-center transition-all hover:scale-105 hover:opacity-95"
        >
          <img
            src="/hacker-house-banner.png"
            alt="Hacker House Goa"
            className="h-8 sm:h-10 w-auto max-w-[180px] sm:max-w-[280px] md:max-w-[360px] object-contain rounded-md shadow-md border border-gold/20"
            style={{
              boxShadow: '0 0 16px rgba(255, 210, 26, 0.15)',
            }}
          />
        </a>

        {/* Right Action: About & How it works popup button */}
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="focus-ring flex items-center gap-2 rounded-full border border-gold/30 px-3.5 py-1.5 transition-all hover:border-gold/60 hover:scale-105 active:scale-95 cursor-pointer"
          style={{
            background: 'linear-gradient(145deg, rgba(5,107,58,0.5) 0%, rgba(4,43,29,0.7) 100%)',
            boxShadow: '0 1px 0 0 rgba(255,210,26,0.12) inset, 0 4px 12px -2px rgba(0,0,0,0.3)',
          }}
          aria-label="Open About and How It Works info"
        >
          <Info className="h-3.5 w-3.5 text-gold" strokeWidth={2.4} />
          <span className="hidden text-[11px] font-semibold uppercase tracking-wider text-cream/90 sm:inline">
            About & How it works
          </span>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-cream/90 sm:hidden">
            Info
          </span>
        </button>
      </div>

      {/* Modal Popup */}
      {showModal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
        >
          {/* Backdrop */}
          <div
            onClick={() => setShowModal(false)}
            className="fixed inset-0 bg-black/75 backdrop-blur-sm transition-opacity"
          />

          {/* Modal Content Card */}
          <div
            className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-3xl border border-gold/30 p-6 sm:p-8 shadow-2xl backdrop-blur-2xl"
            style={{
              background: 'linear-gradient(145deg, rgba(6, 59, 40, 0.98) 0%, rgba(4, 43, 29, 0.98) 100%)',
              boxShadow: '0 0 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(255, 210, 26, 0.15)',
            }}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-gold/15 pb-4 mb-6">
              <div className="flex items-center gap-3">
                <img
                  src="/hh-logo.png"
                  alt="HH Goa"
                  className="h-8 w-8 rounded-lg object-contain border border-gold/30"
                />
                <div>
                  <h3 className="font-display text-lg font-semibold text-cream">
                    Voice RAG Intelligence
                  </h3>
                  <p className="text-xs text-cream/50">
                    Hacker House Goa 2026 · Multilingual Voice Engine
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="p-1.5 rounded-full text-cream/60 hover:text-cream hover:bg-cream/10 transition-colors"
                aria-label="Close modal"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Tab Navigation */}
            <div className="flex rounded-xl bg-forest-dark/70 p-1 mb-6 border border-gold/15">
              <button
                type="button"
                onClick={() => setActiveTab('about')}
                className={`flex-1 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${activeTab === 'about'
                    ? 'bg-gold text-forest-dark shadow-md font-bold'
                    : 'text-cream/70 hover:text-cream'
                  }`}
              >
                About Voice RAG
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('how-it-works')}
                className={`flex-1 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${activeTab === 'how-it-works'
                    ? 'bg-gold text-forest-dark shadow-md font-bold'
                    : 'text-cream/70 hover:text-cream'
                  }`}
              >
                How It Works (Architecture)
              </button>
            </div>

            {/* Tab 1: About */}
            {activeTab === 'about' && (
              <div className="space-y-4 text-cream/80 text-sm leading-relaxed">
                <p>
                  <strong className="text-gold font-semibold">Voice RAG</strong> is an ultra-low latency,
                  multilingual voice retrieval engine built for the <strong className="text-cream">Hacker House Goa 2026 Hackathon</strong>.
                </p>
                <p>
                  It enables seamless bidirectional speech interaction across <strong>15 Indian languages</strong> (Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Assamese, Nepali, Odia, Sanskrit, and English).
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                  <div className="p-3.5 rounded-2xl bg-forest/40 border border-gold/20">
                    <div className="flex items-center gap-2 text-gold font-semibold text-xs uppercase mb-1">
                      <ShieldCheck className="h-4 w-4" /> 100% Grounded AI
                    </div>
                    <p className="text-xs text-cream/70">
                      Eliminates hallucination by enforcing strict confidence score thresholds and refusal logic.
                    </p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-forest/40 border border-gold/20">
                    <div className="flex items-center gap-2 text-gold font-semibold text-xs uppercase mb-1">
                      <Sparkles className="h-4 w-4" /> 15 Regional Languages
                    </div>
                    <p className="text-xs text-cream/70">
                      Full speech-to-text, native generation, and text-to-speech voice playback in all 15 languages.
                    </p>
                  </div>
                </div>
                <div className="pt-4 flex items-center justify-between border-t border-gold/15">
                  <a
                    href="https://hhgoa.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-gold hover:underline"
                  >
                    Visit HH Goa Official Website <ExternalLink className="h-3 w-3" />
                  </a>
                  <button
                    type="button"
                    onClick={() => scrollToSection('about')}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-cream bg-gold/20 hover:bg-gold/30 px-3 py-1.5 rounded-full border border-gold/30 transition-all"
                  >
                    Go to Overview <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            )}

            {/* Tab 2: How It Works */}
            {activeTab === 'how-it-works' && (
              <div className="space-y-4 text-cream/80 text-sm leading-relaxed">
                <p className="text-xs text-cream/60">
                  The system executes an optimized 4-stage pipeline designed for sub-second performance:
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 rounded-2xl bg-forest/40 border border-gold/20">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gold/20 text-gold font-bold text-xs">
                      1
                    </span>
                    <div>
                      <h4 className="text-xs font-bold text-cream uppercase tracking-wide">
                        Speech-to-Text (STT)
                      </h4>
                      <p className="text-xs text-cream/70">
                        Captures live audio directly from the browser and transcribes it with Sarvam AI's low-latency speech models.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 rounded-2xl bg-forest/40 border border-gold/20">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gold/20 text-gold font-bold text-xs">
                      2
                    </span>
                    <div>
                      <h4 className="text-xs font-bold text-cream uppercase tracking-wide">
                        Dense Vector Retrieval (FAISS + E5)
                      </h4>
                      <p className="text-xs text-cream/70">
                        Embeds the query using multilingual E5 and searches across dual Hindi & English FAISS knowledge indexes.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 rounded-2xl bg-forest/40 border border-gold/20">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gold/20 text-gold font-bold text-xs">
                      3
                    </span>
                    <div>
                      <h4 className="text-xs font-bold text-cream uppercase tracking-wide">
                        Grounded Generation & Validation
                      </h4>
                      <p className="text-xs text-cream/70">
                        Generates a concise answer strictly bounded by retrieved evidence. Short-circuits with clear refusal if context is missing.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 rounded-2xl bg-forest/40 border border-gold/20">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gold/20 text-gold font-bold text-xs">
                      4
                    </span>
                    <div>
                      <h4 className="text-xs font-bold text-cream uppercase tracking-wide">
                        Voice Synthesis (TTS) & Auto-Playback
                      </h4>
                      <p className="text-xs text-cream/70">
                        Synthesizes spoken audio in the selected regional language with native accent models.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-4 flex items-center justify-end border-t border-gold/15">
                  <button
                    type="button"
                    onClick={() => scrollToSection('how-it-works')}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-cream bg-gold/20 hover:bg-gold/30 px-3 py-1.5 rounded-full border border-gold/30 transition-all"
                  >
                    View Interactive Pipeline <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
