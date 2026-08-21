import { useState } from "react";
import { Sparkles, MessageSquare, Hand } from "lucide-react";
import {
  getPredefinedQueriesForLanguage,
  type PredefinedQueryItem,
} from "../config/predefinedQueries";
import type { VoiceQueryResponse } from "../types";

interface PredefinedQueriesProps {
  language: string;
  onSelectQuery: (item: PredefinedQueryItem) => void;
  disabled?: boolean;
}

export function PredefinedQueries({
  language,
  onSelectQuery,
  disabled = false,
}: PredefinedQueriesProps) {
  const queries = getPredefinedQueriesForLanguage(language);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const categories = ["All", ...Array.from(new Set(queries.map((q) => q.category)))];

  const filteredQueries =
    selectedCategory === "All"
      ? queries
      : queries.filter((q) => q.category === selectedCategory);

  const greetingQuery = queries.find((q) => q.category === "Greeting");

  return (
    <div className="mt-8 rounded-3xl border border-cream/10 bg-forest-900/40 p-5 backdrop-blur-md">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gold/15 text-gold">
            <Sparkles className="h-3.5 w-3.5" />
          </div>
          <div>
            <h3 className="font-display text-sm font-semibold text-cream">
              Predefined & Sample Questions
            </h3>
            <p className="text-xs text-cream/50">
              Click any question or say Hello to test verified answers in this language
            </p>
          </div>
        </div>

        {greetingQuery && (
          <button
            type="button"
            disabled={disabled}
            onClick={() => onSelectQuery(greetingQuery)}
            className="group flex items-center gap-1.5 rounded-full border border-gold/40 bg-gold/10 px-3.5 py-1.5 text-xs font-semibold text-gold shadow-sm transition-all hover:bg-gold/20 hover:scale-105 active:scale-95 disabled:opacity-50"
          >
            <Hand className="h-3.5 w-3.5 animate-wave" />
            <span>👋 Say Hello ({language.toUpperCase()})</span>
          </button>
        )}
      </div>

      {/* Category filters */}
      {categories.length > 2 && (
        <div className="mb-3.5 flex flex-wrap gap-1.5">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat)}
              className={`rounded-full px-3 py-1 text-[11px] font-medium transition-all ${
                selectedCategory === cat
                  ? "border border-gold/40 bg-gold/20 text-gold"
                  : "border border-cream/10 bg-forest/20 text-cream/60 hover:text-cream"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Query cards/chips grid */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {filteredQueries.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelectQuery(item)}
            className="group flex items-start gap-2.5 rounded-2xl border border-cream/10 bg-forest/30 p-3 text-left transition-all hover:border-gold/30 hover:bg-forest/50 hover:shadow-md active:scale-[0.99] disabled:opacity-50"
          >
            <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-cream/5 text-cream/50 group-hover:bg-gold/20 group-hover:text-gold transition-colors">
              <MessageSquare className="h-3 w-3" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="rounded bg-cream/5 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-cream/40 group-hover:text-gold/70">
                  {item.category}
                </span>
              </div>
              <p className="mt-1 text-xs font-medium leading-relaxed text-cream/80 group-hover:text-cream line-clamp-2">
                {item.question}
              </p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
