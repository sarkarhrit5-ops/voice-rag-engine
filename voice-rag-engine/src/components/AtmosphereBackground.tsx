import { useMemo } from 'react';

/**
 * Cinematic layered background: Goa coastal night + futuristic AI command center.
 * 12+ depth layers with parallax, volumetric light, ocean, silhouettes, neural net,
 * particles, and a giant background orbit with VOICE→RAG→VERIFY→TRUST labels.
 */
export function AtmosphereBackground({
  scrollY = 0,
  pointer = { x: 0, y: 0 },
}: {
  scrollY?: number;
  pointer?: { x: number; y: number };
}) {
  const particles = useMemo(
    () =>
      Array.from({ length: 28 }).map((_, i) => ({
        id: i,
        left: `${(i * 37) % 100}%`,
        top: `${(i * 61) % 100}%`,
        size: i % 6 === 0 ? 3 : i % 3 === 0 ? 2 : 1.5,
        delay: `${(i * 0.5) % 6}s`,
        duration: `${8 + (i % 6) * 2}s`,
        gold: i % 3 !== 0,
      })),
    []
  );

  const nodes = useMemo(
    () => [
      { x: 6, y: 18 }, { x: 12, y: 40 }, { x: 18, y: 28 },
      { x: 4, y: 58 }, { x: 15, y: 72 }, { x: 82, y: 15 },
      { x: 90, y: 38 }, { x: 94, y: 62 }, { x: 78, y: 50 },
      { x: 88, y: 78 }, { x: 50, y: 88 }, { x: 40, y: 92 },
    ],
    []
  );

  const connections = useMemo(() => {
    const pairs: [number, number][] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i]!; const b = nodes[j]!;
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        if (Math.sqrt(dx * dx + dy * dy) < 20) pairs.push([i, j]);
      }
    }
    return pairs;
  }, [nodes]);

  const orbitLabels = ['VOICE', 'RAG', 'VERIFY', 'TRUST'];

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      {/* L1: Deep emerald → black-green base */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse at 65% 15%, #0a5235 0%, transparent 45%), ' +
            'radial-gradient(ellipse at 15% 75%, #0d3a25 0%, transparent 50%), ' +
            'linear-gradient(180deg, #053524 0%, #031f15 55%, #021510 100%)',
        }}
      />

      {/* L2: Supplied Goa artwork, treated as a distant cinematic plane */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: "url('/goa-night.png')",
          backgroundPosition: `calc(50% + ${pointer.x * 12}px) calc(48% + ${pointer.y * 8}px)`,
          transform: `scale(1.08) translate3d(${pointer.x * -5}px, ${pointer.y * -3}px, 0)`,
          opacity: 0.88,
          filter: 'saturate(0.95) contrast(1.06) brightness(0.86)',
          mixBlendMode: 'screen',
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(180deg, rgba(5,5,25,0.48) 0%, rgba(3,31,21,0.42) 42%, rgba(2,21,16,0.9) 100%)',
        }}
      />

      {/* L3: Warm Goa sunset glow at horizon */}
      <div
        className="absolute"
        style={{
          left: '10%', bottom: '8%', width: '70%', height: '35%',
          background:
            'radial-gradient(ellipse, rgba(255,160,50,0.09) 0%, rgba(255,100,40,0.04) 35%, transparent 70%)',
          filter: 'blur(50px)',
        }}
      />

      {/* L4: Horizon light source and atmospheric depth */}
      <div
        className="absolute animate-sun-breathe"
        style={{
          right: '27%',
          bottom: '27%',
          width: 150,
          height: 150,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255,244,214,0.62) 0%, rgba(255,210,26,0.22) 24%, rgba(245,0,122,0.08) 52%, transparent 72%)',
          filter: 'blur(2px)',
          transform: `translate3d(${pointer.x * -6}px, ${pointer.y * -4}px, 0)`,
        }}
      />
      <div
        className="absolute"
        style={{
          left: '8%',
          right: '8%',
          bottom: '17%',
          height: '18%',
          background: 'linear-gradient(180deg, transparent, rgba(255,142,85,0.08) 42%, rgba(2,21,16,0.18))',
          filter: 'blur(18px)',
          transform: `translate3d(${pointer.x * -3}px, ${pointer.y * -2}px, 0)`,
        }}
      />
      <div
        className="absolute inset-x-0 bottom-[17%] h-px"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(255,210,26,0.2), rgba(245,0,122,0.16), transparent)' }}
      />

      {/* L4b: Dimensional 3D sun sitting on the horizon + its ocean reflection */}
      <div
        className="absolute animate-sun-breathe"
        style={{
          right: '28%',
          bottom: '28%',
          width: 92,
          height: 92,
          borderRadius: '50%',
          background:
            'radial-gradient(circle at 38% 32%, #fffaf0 0%, #FFD21A 34%, #ff9d3c 62%, rgba(245,0,122,0.35) 88%)',
          boxShadow:
            '0 0 60px rgba(255,210,26,0.45), 0 0 140px rgba(255,157,60,0.28), inset -6px -8px 22px rgba(245,0,122,0.25)',
          filter: 'blur(0.6px)',
          opacity: 0.75,
          transform: `translate3d(${pointer.x * -6}px, ${pointer.y * -4}px, 0)`,
        }}
      />
      <div
        className="absolute animate-ray-spin"
        style={{
          right: 'calc(28% - 54px)',
          bottom: 'calc(28% - 54px)',
          width: 200,
          height: 200,
          background:
            'conic-gradient(from 0deg, rgba(255,210,26,0.14), transparent 12%, rgba(255,210,26,0.1) 26%, transparent 38%, rgba(255,157,60,0.12) 54%, transparent 68%, rgba(255,210,26,0.1) 84%, transparent 96%)',
          borderRadius: '50%',
          filter: 'blur(14px)',
          opacity: 0.55,
          maskImage: 'radial-gradient(circle, transparent 22%, black 40%, transparent 76%)',
          WebkitMaskImage: 'radial-gradient(circle, transparent 22%, black 40%, transparent 76%)',
        }}
      />
      <div
        className="absolute animate-ocean-shimmer"
        style={{
          right: '30%',
          bottom: '6%',
          width: 90,
          height: '22%',
          background:
            'linear-gradient(180deg, rgba(255,210,26,0.22) 0%, rgba(255,157,60,0.1) 40%, transparent 92%)',
          filter: 'blur(11px)',
          opacity: 0.6,
          transform: `translate3d(${pointer.x * -4}px, 0, 0)`,
        }}
      />

      {/* L5: Volumetric light rays from upper-right */}
      <div
        className="absolute animate-light-ray"
        style={{
          right: '15%', top: '-5%', width: 120, height: '80%',
          background: 'linear-gradient(180deg, rgba(255,210,26,0.06) 0%, transparent 70%)',
          filter: 'blur(20px)',
          transform: 'skewX(-8deg)',
        }}
      />
      <div
        className="absolute animate-light-ray"
        style={{
          right: '30%', top: '-5%', width: 80, height: '70%',
          background: 'linear-gradient(180deg, rgba(255,210,26,0.04) 0%, transparent 70%)',
          filter: 'blur(15px)',
          transform: 'skewX(-12deg)',
          animationDelay: '3s',
        }}
      />

      {/* L5: Technical grid with radial mask */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,210,26,0.035) 1px, transparent 1px), ' +
            'linear-gradient(90deg, rgba(255,210,26,0.035) 1px, transparent 1px)',
          backgroundSize: '56px 56px',
          maskImage: 'radial-gradient(ellipse at 50% 35%, black 25%, transparent 75%)',
          WebkitMaskImage: 'radial-gradient(ellipse at 50% 35%, black 25%, transparent 75%)',
        }}
      />

      {/* L6: Giant background orbit with VOICE→RAG→VERIFY→TRUST */}
      <div
        className="absolute left-1/2 top-[35%] -translate-x-1/2 -translate-y-1/2"
        style={{ width: 900, height: 900, transform: `translate(-50%, -50%) translateY(${scrollY * 0.05}px)` }}
      >
        <div className="relative h-full w-full">
          {/* Outer ring */}
          <div className="absolute inset-0 rounded-full" style={{ border: '1px solid rgba(255,210,26,0.05)' }} />
          {/* Middle ring */}
          <div className="absolute inset-[12%] rounded-full" style={{ border: '1px dashed rgba(255,210,26,0.04)' }} />
          {/* Inner ring */}
          <div className="absolute inset-[28%] rounded-full" style={{ border: '1px solid rgba(45,212,191,0.04)' }} />

          {/* Rotating labels */}
          <div className="absolute inset-0 orbit-label-drift">
            {orbitLabels.map((label, i) => {
              const angle = (i * 90 - 90) * (Math.PI / 180);
              const r = 42;
              const x = 50 + Math.cos(angle) * r;
              const y = 50 + Math.sin(angle) * r;
              return (
                <span
                  key={label}
                  className="absolute font-display text-[10px] font-semibold uppercase tracking-[0.3em]"
                  style={{
                    left: `${x}%`,
                    top: `${y}%`,
                    transform: 'translate(-50%, -50%)',
                    color: i === 0 ? '#FFD21A' : i === 3 ? '#F5007A' : 'rgba(255,244,214,0.3)',
                    textShadow: i === 0 || i === 3 ? '0 0 8px currentColor' : 'none',
                    opacity: 0.5,
                  }}
                >
                  {label}
                </span>
              );
            })}
          </div>

          {/* Tiny data markers on orbit */}
          <div className="absolute inset-0 orbit-label-drift" style={{ animationDuration: '90s' }}>
            {Array.from({ length: 12 }).map((_, i) => {
              const angle = (i * 30) * (Math.PI / 180);
              const r = 49;
              const x = 50 + Math.cos(angle) * r;
              const y = 50 + Math.sin(angle) * r;
              return (
                <span
                  key={i}
                  className="absolute h-1 w-1 rounded-full"
                  style={{
                    left: `${x}%`,
                    top: `${y}%`,
                    background: i % 4 === 0 ? '#F5007A' : '#FFD21A',
                    boxShadow: '0 0 4px currentColor',
                    opacity: 0.4,
                  }}
                />
              );
            })}
          </div>
        </div>
      </div>

      {/* L7: Foreground dimensional accents */}
      <div
        className="absolute hidden sm:block"
        style={{ left: '38%', top: '24%', width: 34, height: 34, transform: `translate3d(${pointer.x * 10}px, ${pointer.y * 7}px, 0) rotate(18deg)`, border: '1px solid rgba(255,210,26,0.42)', boxShadow: '0 0 24px rgba(255,210,26,0.16)', opacity: 0.5 }}
      />
      <div
        className="absolute hidden sm:block rounded-full"
        style={{ right: '35%', top: '18%', width: 18, height: 18, transform: `translate3d(${pointer.x * 12}px, ${pointer.y * 8}px, 0)`, background: 'radial-gradient(circle at 35% 30%, rgba(255,244,214,0.8), rgba(255,210,26,0.38) 38%, rgba(5,107,58,0.18) 72%)', boxShadow: '0 0 20px rgba(255,210,26,0.28)', opacity: 0.65 }}
      />
      <div
        className="absolute hidden sm:block"
        style={{ right: '17%', top: '40%', width: 22, height: 22, transform: `translate3d(${pointer.x * 14}px, ${pointer.y * 9}px, 0) rotate(45deg)`, border: '1px solid rgba(245,0,122,0.62)', background: 'rgba(245,0,122,0.08)', boxShadow: '0 0 20px rgba(245,0,122,0.18)', opacity: 0.6 }}
      />
      <div
        className="absolute hidden sm:block rounded-full"
        style={{ left: '27%', top: '55%', width: 7, height: 7, transform: `translate3d(${pointer.x * 16}px, ${pointer.y * 10}px, 0)`, background: '#FFD21A', boxShadow: '0 0 12px #FFD21A', opacity: 0.6 }}
      />

      {/* L8: Goa silhouettes — palms left (parallax) */}
      <svg
        className="absolute left-0"
        style={{ bottom: 0, width: '32%', height: '50%', transform: `translateY(${scrollY * 0.12}px)` }}
        viewBox="0 0 300 400" fill="none" preserveAspectRatio="xMinYMax meet"
      >
        <path d="M80 400 Q78 300 85 220 Q88 200 82 180" stroke="#021510" strokeWidth="4" fill="none" opacity="0.8" />
        <g opacity="0.6">
          <path d="M82 180 Q50 165 18 175 Q40 178 82 185" fill="#021510" />
          <path d="M82 180 Q112 152 148 158 Q115 175 82 185" fill="#021510" />
          <path d="M82 180 Q55 195 22 212 Q55 195 82 190" fill="#021510" />
          <path d="M82 180 Q115 195 152 208 Q115 190 82 190" fill="#021510" />
          <path d="M82 180 Q82 152 74 125 Q86 155 88 180" fill="#021510" />
        </g>
        <path d="M185 400 Q188 320 183 248 Q181 233 185 218" stroke="#021510" strokeWidth="3" fill="none" opacity="0.55" />
        <g opacity="0.4">
          <path d="M185 218 Q158 206 132 212 Q158 216 185 222" fill="#021510" />
          <path d="M185 218 Q212 202 240 208 Q212 220 185 222" fill="#021510" />
          <path d="M185 218 Q162 230 136 240 Q165 228 185 224" fill="#021510" />
          <path d="M185 218 Q208 230 236 238 Q208 224 185 224" fill="#021510" />
        </g>
      </svg>

      {/* Palms right */}
      <svg
        className="absolute right-0"
        style={{ bottom: 0, width: '28%', height: '45%', transform: `translateY(${scrollY * 0.08}px)` }}
        viewBox="0 0 300 400" fill="none" preserveAspectRatio="xMaxYMax meet"
      >
        <path d="M225 400 Q228 308 222 238 Q220 222 225 206" stroke="#021510" strokeWidth="3.5" fill="none" opacity="0.65" />
        <g opacity="0.5">
          <path d="M225 206 Q192 190 158 196 Q192 202 225 212" fill="#021510" />
          <path d="M225 206 Q258 186 290 192 Q258 208 225 212" fill="#021510" />
          <path d="M225 206 Q198 220 168 230 Q198 218 225 214" fill="#021510" />
          <path d="M225 206 Q252 220 282 228 Q252 216 225 214" fill="#021510" />
          <path d="M225 206 Q225 178 218 152 Q230 180 230 206" fill="#021510" />
        </g>
      </svg>

      {/* Lighthouse */}
      <svg
        className="absolute right-[6%]"
        style={{ bottom: 0, width: '4.5%', height: '24%', transform: `translateY(${scrollY * 0.05}px)` }}
        viewBox="0 0 60 200" fill="none" preserveAspectRatio="xMidYMax meet"
      >
        <g opacity="0.35">
          <rect x="23" y="55" width="14" height="145" fill="#021510" />
          <path d="M19 55 L41 55 L37 40 L23 40 Z" fill="#021510" />
          <rect x="25" y="25" width="10" height="16" fill="#021510" />
          <circle cx="30" cy="20" r="6" fill="#021510" />
          <circle cx="30" cy="20" r="4" fill="#FFD21A" opacity="0.4" className="animate-pulse" />
          <path d="M30 20 L8 8 M30 20 L52 8" stroke="#FFD21A" strokeWidth="0.8" opacity="0.2" />
        </g>
      </svg>

      {/* Goan church */}
      <svg
        className="absolute left-[4%]"
        style={{ bottom: 0, width: '7%', height: '18%', transform: `translateY(${scrollY * 0.04}px)` }}
        viewBox="0 0 80 120" fill="none" preserveAspectRatio="xMidYMax meet"
      >
        <g opacity="0.3">
          <rect x="18" y="48" width="44" height="72" fill="#021510" />
          <path d="M18 48 L62 48 L40 16 Z" fill="#021510" />
          <rect x="35" y="6" width="10" height="14" fill="#021510" />
          <circle cx="40" cy="4" r="5" fill="#021510" />
          <rect x="33" y="62" width="14" height="28" fill="#021510" opacity="0.5" />
          <rect x="24" y="58" width="6" height="10" fill="#021510" opacity="0.4" />
          <rect x="50" y="58" width="6" height="10" fill="#021510" opacity="0.4" />
        </g>
      </svg>

      {/* L8: Ocean with reflective shimmer */}
      <svg
        className="absolute bottom-0 left-0 w-full animate-ocean-shimmer"
        style={{ height: '22%', transform: `translateY(${scrollY * -0.03}px)` }}
        viewBox="0 0 1200 200" fill="none" preserveAspectRatio="xMidYMax slice"
      >
        <path d="M0 200 L0 135 Q 150 115 300 135 T 600 125 T 900 135 T 1200 130 L1200 200 Z" fill="#021510" opacity="0.6" />
        <path d="M0 200 L0 162 Q 200 148 400 162 T 800 152 T 1200 158 L1200 200 Z" fill="#031f15" opacity="0.5" />
        {/* Reflective highlights */}
        <path d="M0 137 Q 150 117 300 137 T 600 127 T 900 137 T 1200 132" stroke="rgba(255,210,26,0.08)" strokeWidth="1" fill="none" />
        <path d="M0 164 Q 200 150 400 164 T 800 154 T 1200 160" stroke="rgba(255,210,26,0.05)" strokeWidth="1" fill="none" />
        <path d="M0 180 Q 250 172 500 180 T 1000 176 T 1200 178" stroke="rgba(45,212,191,0.04)" strokeWidth="0.8" fill="none" />
      </svg>

      {/* Sailboat */}
      <svg
        className="absolute left-[33%]"
        style={{ bottom: '17%', width: '3.5%', height: '5%', transform: `translateY(${scrollY * -0.02}px)` }}
        viewBox="0 0 60 40" fill="none" preserveAspectRatio="xMidYMax meet"
      >
        <g opacity="0.25">
          <path d="M8 30 L52 30 L46 37 L14 37 Z" fill="#021510" />
          <line x1="30" y1="30" x2="30" y2="4" stroke="#021510" strokeWidth="1.5" />
          <path d="M30 7 L30 28 L50 28 Z" fill="#021510" opacity="0.5" />
        </g>
      </svg>

      {/* L9: Radar / orbital circles */}
      <div className="absolute rounded-full" style={{ right: '-6%', top: '12%', width: 550, height: 550, border: '1px solid rgba(255,210,26,0.07)', transform: `translateY(${scrollY * 0.1}px)` }} />
      <div className="absolute rounded-full" style={{ right: '2%', top: '20%', width: 380, height: 380, border: '1px dashed rgba(255,210,26,0.05)', transform: `translateY(${scrollY * 0.1}px)` }} />
      <div className="absolute rounded-full" style={{ right: '6%', top: '26%', width: 220, height: 220, border: '1px solid rgba(45,212,191,0.05)', transform: `translateY(${scrollY * 0.1}px)` }} />
      <div className="absolute rounded-full" style={{ left: '-8%', top: '32%', width: 480, height: 480, border: '1px solid rgba(245,0,122,0.05)', transform: `translateY(${scrollY * -0.08}px)` }} />
      <div className="absolute rounded-full" style={{ left: '-3%', top: '40%', width: 300, height: 300, border: '1px dashed rgba(245,0,122,0.04)', transform: `translateY(${scrollY * -0.08}px)` }} />

      {/* L10: Neural network */}
      <svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
        {connections.map(([a, b], i) => (
          <line key={`c-${i}`} x1={`${nodes[a]!.x}%`} y1={`${nodes[a]!.y}%`} x2={`${nodes[b]!.x}%`} y2={`${nodes[b]!.y}%`} stroke="rgba(255,210,26,0.07)" strokeWidth="0.5" />
        ))}
        {nodes.map((n, i) => (
          <circle key={`n-${i}`} cx={`${n.x}%`} cy={`${n.y}%`} r="2.5" fill={i % 5 === 0 ? '#F5007A' : '#FFD21A'} opacity="0.3">
            <animate attributeName="opacity" values="0.15;0.45;0.15" dur={`${4 + (i % 3)}s`} repeatCount="indefinite" begin={`${i * 0.4}s`} />
          </circle>
        ))}
      </svg>

      {/* L11: Sound waves from mic area */}
      <svg className="absolute" style={{ right: '12%', top: '22%', width: 340, height: 220, opacity: 0.18 }} viewBox="0 0 340 220" fill="none">
        {[0, 1, 2, 3, 4].map((i) => (
          <path key={i} d={`M ${280 + i * 12} 110 Q ${220 - i * 18} ${55 + i * 12}, ${90 - i * 12} ${110 + i * 6} T ${-30} ${95 + i * 8}`} stroke="#FFD21A" strokeWidth="1" opacity={0.45 - i * 0.07}>
            <animate attributeName="stroke-dashoffset" values="0;-25" dur={`${3 + i}s`} repeatCount="indefinite" />
          </path>
        ))}
      </svg>

      {/* L12: Expanding ripples around voice panel */}
      <div className="absolute rounded-full" style={{ right: '8%', top: '18%', width: 440, height: 440, border: '1px solid rgba(255,210,26,0.05)', animation: 'pulse-ring 5s ease-out infinite' }} />
      <div className="absolute rounded-full" style={{ right: '8%', top: '18%', width: 440, height: 440, border: '1px solid rgba(255,210,26,0.04)', animation: 'pulse-ring 5s ease-out infinite 2.5s' }} />

      {/* L13: Glowing particles */}
      {particles.map((p) => (
        <span key={p.id} className="absolute rounded-full" style={{ left: p.left, top: p.top, width: p.size, height: p.size, background: p.gold ? '#FFD21A' : '#F5007A', boxShadow: p.gold ? '0 0 6px rgba(255,210,26,0.4)' : '0 0 6px rgba(245,0,122,0.3)', opacity: 0.35, animation: `float-slow ${p.duration} ease-in-out ${p.delay} infinite` }} />
      ))}

      {/* L14: Atmospheric glows */}
      <div className="absolute rounded-full blur-3xl animate-float-slow" style={{ right: '3%', top: '8%', width: 340, height: 340, background: 'rgba(255,210,26,0.05)' }} />
      <div className="absolute rounded-full blur-3xl animate-float-slower" style={{ left: '-2%', top: '48%', width: 400, height: 400, background: 'rgba(245,0,122,0.04)' }} />
      <div className="absolute rounded-full blur-3xl" style={{ left: '40%', bottom: '5%', width: 300, height: 300, background: 'rgba(255,160,50,0.04)' }} />

      {/* L15: Radial mic glow */}
      <div className="absolute hidden lg:block" style={{ right: '3%', top: '12%', width: 560, height: 560, background: 'radial-gradient(circle, rgba(255,210,26,0.06) 0%, transparent 58%)' }} />

      {/* L16: Teal accent dots */}
      <div className="absolute left-[28%] top-[12%] h-1 w-1 rounded-full" style={{ background: 'rgba(45,212,191,0.35)', boxShadow: '0 0 4px rgba(45,212,191,0.2)' }} />
      <div className="absolute left-[62%] top-[68%] h-1 w-1 rounded-full" style={{ background: 'rgba(45,212,191,0.3)', boxShadow: '0 0 4px rgba(45,212,191,0.15)' }} />
      <div className="absolute left-[48%] top-[82%] h-1 w-1 rounded-full" style={{ background: 'rgba(45,212,191,0.25)' }} />
      <div className="absolute left-[15%] top-[85%] h-1 w-1 rounded-full" style={{ background: 'rgba(45,212,191,0.2)' }} />
    </div>
  );
}
