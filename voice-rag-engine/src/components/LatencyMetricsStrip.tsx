import { Activity, Clock, Database, Mic2, Sparkles, Zap } from 'lucide-react';
import type { LatencyMetrics } from '../types';

interface LatencyMetricsStripProps {
  metrics: LatencyMetrics;
  grounded: boolean;
}

export function LatencyMetricsStrip({ metrics, grounded }: LatencyMetricsStripProps) {
  const items = [
    { label: 'Speech', value: metrics.stt_ms, icon: Mic2, unit: 'ms' },
    { label: 'Retrieval', value: metrics.retrieval_ms, icon: Database, unit: 'ms' },
    { label: 'Generation', value: metrics.generation_ms, icon: Sparkles, unit: 'ms' },
    { label: 'Total', value: metrics.total_ms, icon: Zap, unit: 'ms' },
  ].filter((i) => i.value !== undefined);

  return (
    <div
      id="performance"
      className="animate-fade-up flex flex-wrap items-center gap-2.5 rounded-2xl border border-cream/10 p-3"
      style={{
        background:
          'linear-gradient(145deg, rgba(6,59,40,0.6) 0%, rgba(4,43,29,0.8) 100%)',
        boxShadow:
          '0 1px 0 0 rgba(255,210,26,0.06) inset, 0 12px 32px -16px rgba(0,0,0,0.5)',
      }}
      aria-label="Performance telemetry"
    >
      <div className="flex items-center gap-1.5 px-1.5">
        <Activity className="h-3.5 w-3.5 text-gold" strokeWidth={2.5} />
        <span className="text-[10px] font-semibold uppercase tracking-wider text-cream/50">
          Telemetry
        </span>
      </div>
      <div className="h-4 w-px bg-cream/10" />
      {items.map((item) => (
        <div
          key={item.label}
          className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5"
          style={{
            background: 'linear-gradient(145deg, rgba(255,210,26,0.04) 0%, rgba(255,244,214,0.02) 100%)',
            boxShadow: '0 1px 0 0 rgba(255,210,26,0.05) inset',
          }}
        >
          <item.icon className="h-3 w-3 text-gold/70" strokeWidth={2.5} />
          <span className="text-[11px] font-medium text-cream/60">{item.label}</span>
          <span className="font-display text-sm font-semibold text-cream">
            {item.value}
            <span className="ml-0.5 text-[10px] font-normal text-cream/40">{item.unit}</span>
          </span>
        </div>
      ))}
      <div className="h-4 w-px bg-cream/10" />
      <div
        className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5"
        style={{
          background: grounded
            ? 'linear-gradient(145deg, rgba(255,210,26,0.08) 0%, rgba(255,210,26,0.02) 100%)'
            : 'linear-gradient(145deg, rgba(245,0,122,0.06) 0%, rgba(245,0,122,0.02) 100%)',
          boxShadow: '0 1px 0 0 rgba(255,210,26,0.08) inset',
        }}
      >
        <Clock className="h-3 w-3 text-gold/70" strokeWidth={2.5} />
        <span className="text-[11px] font-medium text-cream/60">Grounded</span>
        <span className="font-display text-sm font-semibold text-gold">
          {grounded ? 'YES' : 'NO'}
        </span>
      </div>
    </div>
  );
}
