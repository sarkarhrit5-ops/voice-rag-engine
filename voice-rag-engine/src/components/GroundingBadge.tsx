import { ShieldCheck, ShieldX } from 'lucide-react';

interface GroundingBadgeProps {
  grounded: boolean;
}

export function GroundingBadge({ grounded }: GroundingBadgeProps) {
  if (grounded) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-forest/10 px-3 py-1 text-xs font-semibold text-forest">
        <ShieldCheck className="h-3.5 w-3.5" strokeWidth={2.5} />
        Grounded
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-hh-pink/10 px-3 py-1 text-xs font-semibold text-hh-pink">
      <ShieldX className="h-3.5 w-3.5" strokeWidth={2.5} />
      Not grounded
    </span>
  );
}
