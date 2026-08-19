interface DecorativePatternProps {
  variant?: 'dots' | 'grid' | 'ornament' | 'corner';
  className?: string;
}

export function DecorativePattern({ variant = 'dots', className = '' }: DecorativePatternProps) {
  if (variant === 'dots') {
    return <div className={`pattern-dots ${className}`} aria-hidden="true" />;
  }
  if (variant === 'grid') {
    return <div className={`pattern-grid-gold ${className}`} aria-hidden="true" />;
  }
  if (variant === 'corner') {
    return (
      <svg
        className={className}
        width="64"
        height="64"
        viewBox="0 0 64 64"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M2 2 L2 24 M2 2 L24 2"
          stroke="#FFD21A"
          strokeWidth="1.5"
          strokeLinecap="round"
          opacity="0.5"
        />
        <circle cx="2" cy="2" r="2.5" fill="#FFD21A" opacity="0.7" />
        <path
          d="M10 2 Q 10 10, 18 10"
          stroke="#F5007A"
          strokeWidth="1"
          fill="none"
          opacity="0.4"
        />
      </svg>
    );
  }
  // ornament — a subtle Indian-inspired geometric motif
  return (
    <svg
      className={className}
      viewBox="0 0 200 200"
      fill="none"
      aria-hidden="true"
    >
      <g opacity="0.15">
        <circle cx="100" cy="100" r="80" stroke="#FFD21A" strokeWidth="1" />
        <circle cx="100" cy="100" r="60" stroke="#FFD21A" strokeWidth="0.8" />
        <circle cx="100" cy="100" r="40" stroke="#FFD21A" strokeWidth="0.6" />
        {Array.from({ length: 12 }).map((_, i) => {
          const angle = (i * 30 * Math.PI) / 180;
          const x1 = 100 + Math.cos(angle) * 40;
          const y1 = 100 + Math.sin(angle) * 40;
          const x2 = 100 + Math.cos(angle) * 80;
          const y2 = 100 + Math.sin(angle) * 80;
          return (
            <line
              key={i}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="#FFD21A"
              strokeWidth="0.5"
            />
          );
        })}
        <circle cx="100" cy="100" r="6" fill="#F5007A" opacity="0.5" />
      </g>
    </svg>
  );
}
