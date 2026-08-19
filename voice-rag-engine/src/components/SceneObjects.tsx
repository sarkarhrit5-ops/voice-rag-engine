import { useMemo } from 'react';

/**
 * Mid + foreground dimensional layer of the Goa scene.
 *
 * Renders a curated set of "funky" 3D-feeling objects (gold discs, pink
 * diamonds, green spheres, rings, cubes, palm leaves, sun shapes, arches,
 * hacker-house badges, code glyphs) distributed across three depth tiers.
 * Each tier gets its own parallax strength, blur, scale and opacity so the
 * page reads as one continuous dimensional space instead of flat decoration.
 */

type Kind =
  | 'disc'
  | 'diamond'
  | 'sphere'
  | 'ring'
  | 'cube'
  | 'leaf'
  | 'sun'
  | 'wave'
  | 'arch'
  | 'badge'
  | 'code';

interface SceneItem {
  kind: Kind;
  /** percentage position */
  x: number;
  y: number;
  size: number;
  /** 0 = deep background, 1 = close foreground */
  depth: number;
  drift: 1 | 2 | 3;
  delay: number;
}

const MID_ITEMS: SceneItem[] = [
  { kind: 'disc', x: 8, y: 22, size: 52, depth: 0.35, drift: 1, delay: 0 },
  { kind: 'ring', x: 30, y: 12, size: 44, depth: 0.25, drift: 2, delay: 1.5 },
  { kind: 'badge', x: 10, y: 36, size: 46, depth: 0.45, drift: 1, delay: 1.2 },
  { kind: 'leaf', x: 4, y: 62, size: 62, depth: 0.4, drift: 3, delay: 0.8 },
  { kind: 'diamond', x: 44, y: 36, size: 26, depth: 0.5, drift: 2, delay: 2.4 },
  { kind: 'sphere', x: 63, y: 8, size: 30, depth: 0.3, drift: 1, delay: 3.1 },
  { kind: 'arch', x: 92, y: 30, size: 58, depth: 0.28, drift: 3, delay: 0.4 },
  { kind: 'code', x: 21, y: 84, size: 34, depth: 0.45, drift: 2, delay: 1.9 },
  { kind: 'disc', x: 74, y: 78, size: 42, depth: 0.22, drift: 1, delay: 2.7 },
  { kind: 'wave', x: 55, y: 92, size: 70, depth: 0.34, drift: 3, delay: 1.2 },
  { kind: 'badge', x: 88, y: 66, size: 40, depth: 0.42, drift: 2, delay: 3.6 },
];

const FRONT_ITEMS: SceneItem[] = [
  { kind: 'cube', x: 14, y: 46, size: 30, depth: 0.85, drift: 1, delay: 0.6 },
  { kind: 'disc', x: 68, y: 18, size: 22, depth: 0.95, drift: 3, delay: 2.2 },
  { kind: 'diamond', x: 82, y: 88, size: 20, depth: 0.9, drift: 2, delay: 1.1 },
];

function Shape({ kind, size }: { kind: Kind; size: number }) {
  const s = size;
  switch (kind) {
    case 'disc':
      return (
        <div
          className="rounded-full"
          style={{
            width: s,
            height: s * 0.34,
            background:
              'linear-gradient(160deg, var(--env-sun) 0%, #e8b800 42%, rgba(5,107,58,0.65) 100%)',
            boxShadow:
              '0 0 22px rgba(255,210,26,0.28), inset 0 1px 2px rgba(255,244,214,0.7), inset 0 -2px 4px rgba(0,0,0,0.35)',
            transform: 'rotateX(62deg)',
            opacity: 0.85,
          }}
        />
      );
    case 'sphere':
      return (
        <div
          className="rounded-full"
          style={{
            width: s,
            height: s,
            background:
              'radial-gradient(circle at 32% 26%, rgba(255,244,214,0.85), rgba(255,210,26,0.4) 26%, #0a7a45 58%, #042b1d 100%)',
            boxShadow:
              '0 0 20px rgba(5,107,58,0.5), inset -3px -4px 10px rgba(0,0,0,0.45), inset 2px 2px 6px rgba(245,0,122,0.18)',
          }}
        />
      );
    case 'diamond':
      return (
        <div
          style={{
            width: s,
            height: s,
            transform: 'rotate(45deg)',
            background:
              'linear-gradient(145deg, rgba(245,0,122,0.42) 0%, rgba(245,0,122,0.08) 60%, rgba(255,210,26,0.14) 100%)',
            border: '1px solid rgba(245,0,122,0.6)',
            boxShadow: '0 0 18px rgba(245,0,122,0.3), inset 0 0 12px rgba(255,244,214,0.12)',
          }}
        />
      );
    case 'ring':
      return (
        <div
          className="rounded-full"
          style={{
            width: s,
            height: s * 0.42,
            border: '2px solid rgba(255,210,26,0.55)',
            borderTopColor: 'rgba(255,244,214,0.85)',
            borderBottomColor: 'rgba(5,107,58,0.7)',
            transform: 'rotateX(58deg) rotateZ(-12deg)',
            boxShadow: '0 0 18px rgba(255,210,26,0.22)',
          }}
        />
      );
    case 'cube':
      return (
        <div
          style={{
            width: s,
            height: s,
            transform: 'rotateX(20deg) rotateY(-24deg)',
            background:
              'linear-gradient(135deg, rgba(255,210,26,0.22) 0%, rgba(5,107,58,0.55) 55%, rgba(4,43,29,0.85) 100%)',
            border: '1px solid rgba(255,210,26,0.4)',
            boxShadow:
              '6px 6px 0 -1px rgba(245,0,122,0.18), 0 0 20px rgba(255,210,26,0.16)',
          }}
        />
      );
    case 'leaf':
      return (
        <svg width={s} height={s} viewBox="0 0 32 32" fill="none">
          <path
            d="M16 2 C 7 9, 6 20, 16 30 C 26 20, 25 9, 16 2 Z"
            fill="rgba(5,107,58,0.35)"
            stroke="rgba(255,210,26,0.55)"
            strokeWidth="1"
          />
          <path d="M16 4 L16 28" stroke="rgba(255,210,26,0.4)" strokeWidth="0.7" />
          <path d="M16 12 L9 9 M16 12 L23 9 M16 19 L10 16 M16 19 L22 16" stroke="rgba(255,244,214,0.22)" strokeWidth="0.6" />
        </svg>
      );
    case 'sun':
      return (
        <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="8" fill="url(#sun-core)" />
          <defs>
            <radialGradient id="sun-core">
              <stop offset="0%" stopColor="#FFF4D6" />
              <stop offset="60%" stopColor="#FFD21A" />
              <stop offset="100%" stopColor="#e8b800" />
            </radialGradient>
          </defs>
          {Array.from({ length: 12 }).map((_, i) => {
            const a = (i * 30 * Math.PI) / 180;
            return (
              <line
                key={i}
                x1={20 + Math.cos(a) * 11}
                y1={20 + Math.sin(a) * 11}
                x2={20 + Math.cos(a) * 17}
                y2={20 + Math.sin(a) * 17}
                stroke="rgba(255,210,26,0.55)"
                strokeWidth="1"
                strokeLinecap="round"
              />
            );
          })}
        </svg>
      );
    case 'wave':
      return (
        <svg width={s} height={s * 0.4} viewBox="0 0 70 28" fill="none">
          <path d="M1 20 Q 12 6, 23 20 T 45 20 T 68 18" stroke="rgba(255,210,26,0.45)" strokeWidth="1.2" fill="none" />
          <path d="M1 26 Q 14 14, 27 26 T 50 25 T 68 24" stroke="rgba(245,0,122,0.3)" strokeWidth="1" fill="none" />
        </svg>
      );
    case 'arch':
      return (
        <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
          <path d="M6 38 L6 18 A 14 14 0 0 1 34 18 L34 38" stroke="rgba(255,210,26,0.4)" strokeWidth="1.2" fill="rgba(5,107,58,0.14)" />
          <path d="M12 38 L12 20 A 8 8 0 0 1 28 20 L28 38" stroke="rgba(245,0,122,0.28)" strokeWidth="0.9" fill="none" />
        </svg>
      );
    case 'badge':
      return (
        <div
          className="flex items-center justify-center rounded-full overflow-hidden"
          style={{
            width: s,
            height: s,
            background: 'linear-gradient(145deg, rgba(6,59,40,0.8), rgba(4,43,29,0.55))',
            border: '1px solid rgba(255,210,26,0.35)',
            boxShadow: '0 0 18px rgba(255,210,26,0.18), inset 0 1px 0 rgba(255,244,214,0.18)',
          }}
        >
          <img src="/hh-logo.png" alt="HH Goa" className="w-full h-full object-cover opacity-85" />
        </div>
      );
    case 'code':
      return (
        <span
          className="font-mono font-semibold"
          style={{
            fontSize: s * 0.5,
            color: 'rgba(255,210,26,0.4)',
            textShadow: '0 0 12px rgba(255,210,26,0.35)',
          }}
        >
          {'{ }'}
        </span>
      );
  }
}

function Layer({
  items,
  scrollY,
  pointer,
}: {
  items: SceneItem[];
  scrollY: number;
  pointer: { x: number; y: number };
}) {
  return (
    <>
      {items.map((item, i) => {
        // Depth drives parallax strength, blur, opacity and scale
        const px = pointer.x * (2 + item.depth * 13);
        const py = pointer.y * (2 + item.depth * 11);
        const sy = scrollY * (0.02 + item.depth * 0.12);
        return (
          <div
            key={`${item.kind}-${i}`}
            className="absolute"
            style={{
              left: `${item.x}%`,
              top: `${item.y}%`,
              transform: `translate3d(${px}px, ${py - sy}px, 0)`,
              filter: `blur(${Math.max(0, (0.55 - item.depth) * 4)}px)`,
              opacity: 0.5 + item.depth * 0.45,
              willChange: 'transform',
            }}
          >
            <div
              className={`animate-drift-${item.drift} preserve-3d`}
              style={{ animationDelay: `${item.delay}s`, transformStyle: 'preserve-3d' }}
            >
              <Shape kind={item.kind} size={item.size} />
            </div>
          </div>
        );
      })}
    </>
  );
}

export function SceneObjects({
  scrollY = 0,
  pointer = { x: 0, y: 0 },
  variant = 'mid',
}: {
  scrollY?: number;
  pointer?: { x: number; y: number };
  variant?: 'mid' | 'front';
}) {
  const items = useMemo(() => (variant === 'mid' ? MID_ITEMS : FRONT_ITEMS), [variant]);

  return (
    <div
      className="pointer-events-none absolute inset-0 hidden overflow-hidden sm:block"
      aria-hidden="true"
      style={{ perspective: 1200 }}
    >
      {/* Atmospheric translucent depth forms — sit between background and UI */}
      {variant === 'mid' && (
        <>
          <div
            className="absolute rounded-full"
            style={{
              left: '52%',
              top: '6%',
              width: 620,
              height: 620,
              transform: `translate3d(${pointer.x * 6}px, ${pointer.y * 5 - scrollY * 0.05}px, 0)`,
              background:
                'radial-gradient(circle, rgba(255,210,26,0.05) 0%, rgba(245,0,122,0.02) 38%, transparent 68%)',
              filter: 'blur(30px)',
            }}
          />
          <div
            className="absolute rounded-full"
            style={{
              left: '2%',
              top: '34%',
              width: 380,
              height: 380,
              transform: `translate3d(${pointer.x * 4}px, ${pointer.y * 3 - scrollY * 0.03}px, 0)`,
              border: '1px solid rgba(255,244,214,0.05)',
              background: 'radial-gradient(circle, rgba(5,107,58,0.12) 0%, transparent 70%)',
              filter: 'blur(6px)',
            }}
          />
        </>
      )}
      <Layer items={items} scrollY={scrollY} pointer={pointer} />
    </div>
  );
}
