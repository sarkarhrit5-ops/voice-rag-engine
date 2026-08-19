import { Quote } from 'lucide-react';

interface TranscriptCardProps {
  text: string;
  languageLabel?: string;
}

export function TranscriptCard({ text, languageLabel }: TranscriptCardProps) {
  return (
    <div className="animate-fade-up rounded-3xl border border-cream/10 bg-forest-darker/50 p-5">
      <div className="mb-3 flex items-center gap-2">
        <Quote className="h-3.5 w-3.5 text-gold" strokeWidth={2.5} />
        <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-cream/50">
          You asked
        </span>
        {languageLabel && (
          <span className="ml-auto rounded-full bg-cream/5 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-cream/40">
            {languageLabel}
          </span>
        )}
      </div>
      <p className="font-display text-lg leading-relaxed text-cream sm:text-xl">
        “{text}”
      </p>
    </div>
  );
}
