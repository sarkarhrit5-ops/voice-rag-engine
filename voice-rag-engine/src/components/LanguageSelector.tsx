import { useEffect, useRef, useState } from 'react';
import { Check, ChevronDown, Globe } from 'lucide-react';
import { LANGUAGES } from '../config/languages';
import type { LanguageOption } from '../types';

interface LanguageSelectorProps {
  value: string;
  onChange: (code: string) => void;
}

export function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const selected = LANGUAGES.find((l) => l.code === value);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={`Selected language: ${selected?.label ?? 'language'}`}
        className="focus-ring flex w-full items-center justify-between gap-3 rounded-2xl border border-cream/15 px-4 py-3 text-left transition-all hover:border-gold/40"
        style={{
          background:
            'linear-gradient(145deg, rgba(6,59,40,0.8) 0%, rgba(4,43,29,0.9) 100%)',
          boxShadow:
            '0 1px 0 0 rgba(255,210,26,0.08) inset, 0 8px 20px -10px rgba(0,0,0,0.4)',
        }}
      >
        <span className="flex items-center gap-3">
          <span
            className="flex h-7 w-7 items-center justify-center rounded-lg"
            style={{
              background: 'linear-gradient(145deg, rgba(255,210,26,0.15) 0%, rgba(255,210,26,0.05) 100%)',
              boxShadow: '0 1px 0 0 rgba(255,210,26,0.1) inset',
            }}
          >
            <Globe className="h-3.5 w-3.5 text-gold" strokeWidth={2.2} />
          </span>
          <span className="text-sm font-medium text-cream">
            {selected?.label ?? 'Select language'}
          </span>
          {selected && selected.code !== 'auto' && (
            <span className="font-display text-sm text-cream/60">
              {selected.nativeLabel}
            </span>
          )}
        </span>
        <ChevronDown
          className={`h-4 w-4 text-cream/50 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open && (
        <div
          role="listbox"
          className="animate-scale-in absolute z-50 mt-2 max-h-72 w-full overflow-y-auto rounded-2xl border border-gold/20 p-1.5 backdrop-blur-xl"
          style={{
            background: 'rgba(4, 43, 29, 0.96)',
            boxShadow:
              '0 1px 0 0 rgba(255,210,26,0.1) inset, 0 24px 60px -20px rgba(0,0,0,0.7)',
          }}
        >
          {LANGUAGES.map((lang: LanguageOption) => {
            const isActive = lang.code === value;
            return (
              <button
                key={lang.code}
                role="option"
                aria-selected={isActive}
                onClick={() => {
                  onChange(lang.code);
                  setOpen(false);
                }}
                className={`focus-ring flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left transition-colors ${
                  isActive ? 'bg-gold/15' : 'hover:bg-cream/5'
                }`}
              >
                <span className="flex items-center gap-3">
                  <span className="text-base">{lang.flag}</span>
                  <span className="text-sm font-medium text-cream">{lang.label}</span>
                  {lang.code !== 'auto' && (
                    <span className="font-display text-sm text-cream/50">
                      {lang.nativeLabel}
                    </span>
                  )}
                </span>
                {isActive && <Check className="h-4 w-4 text-gold" strokeWidth={2.5} />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
