// Decorative space scene for the app shell (Member 3). Everything here is aria-hidden and
// pointer-events: none, so it never gets in the way of reading or operating the dashboard.
// All motion is CSS and stops under prefers-reduced-motion (see global.css).
// Original team artwork: not an agency logo, spacecraft or mission patch.

/** Small deterministic PRNG so the starfield looks the same on every load (and in screenshots). */
function seeded(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

interface Star { x: number; y: number; r: number; delay: number; dur: number; tier: 0 | 1 | 2 }

const STARS: Star[] = (() => {
  const rand = seeded(20261114);
  return Array.from({ length: 90 }, () => {
    const roll = rand();
    const tier: Star["tier"] = roll > 0.93 ? 2 : roll > 0.6 ? 1 : 0;
    return {
      x: Math.round(rand() * 1200),
      y: Math.round(rand() * 190),
      r: tier === 2 ? 1.8 : tier === 1 ? 1.15 : 0.7,
      delay: Math.round(rand() * 6000) / 1000,
      dur: 2.4 + Math.round(rand() * 3000) / 1000,
      tier,
    };
  });
})();

function sparkle(x: number, y: number, s: number) {
  return `M${x} ${y - s * 2.4}L${x + s * 0.45} ${y - s * 0.45}L${x + s * 2.4} ${y}L${x + s * 0.45} ${y + s * 0.45}L${x} ${y + s * 2.4}L${x - s * 0.45} ${y + s * 0.45}L${x - s * 2.4} ${y}L${x - s * 0.45} ${y - s * 0.45}Z`;
}

/** Starfield, sized to cover the header. */
function Stars() {
  return (
    <svg className="scene__sky" viewBox="0 0 1200 190" preserveAspectRatio="xMaxYMax slice" aria-hidden="true">
      {STARS.map((s, i) =>
        s.tier === 2 ? (
          <path key={i} className="star star--spark" d={sparkle(s.x, s.y, s.r)} style={{ animationDelay: `${s.delay}s`, animationDuration: `${s.dur + 1.5}s` }} />
        ) : (
          <circle key={i} className={`star star--${s.tier}`} cx={s.x} cy={s.y} r={s.r} style={{ animationDelay: `${s.delay}s`, animationDuration: `${s.dur}s` }} />
        ),
      )}
    </svg>
  );
}

/** Earth's limb as a thin horizon pinned to the bottom-right, same proportions on every screen. */
function Earth() {
  return (
    <svg className="scene__earth" viewBox="0 0 1000 120" preserveAspectRatio="xMaxYMax meet" aria-hidden="true">
      <defs>
        <radialGradient id="scene-earth" cx="0.5" cy="0.06" r="0.5">
          <stop offset="0" stopColor="#3f97de" />
          <stop offset="0.5" stopColor="#1f63b1" />
          <stop offset="1" stopColor="#0d2f66" />
        </radialGradient>
        <linearGradient id="scene-glow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#8fe8ff" stopOpacity="0.9" />
          <stop offset="1" stopColor="#5ec8e5" stopOpacity="0" />
        </linearGradient>
        <filter id="scene-blur" x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur stdDeviation="5" />
        </filter>
        <clipPath id="scene-earth-clip"><circle cx="820" cy="1100" r="1070" /></clipPath>
      </defs>
      {/* atmosphere glow, ocean, slowly drifting cloud bands */}
      <circle cx="820" cy="1100" r="1084" fill="none" stroke="url(#scene-glow)" strokeWidth="18" filter="url(#scene-blur)" />
      <circle cx="820" cy="1100" r="1070" fill="url(#scene-earth)" />
      <g clipPath="url(#scene-earth-clip)">
        <g className="scene__clouds">
          <path d="M520 104 q60 -12 120 -4 t130 -6 t110 6" fill="none" stroke="#ffffff" strokeOpacity="0.35" strokeWidth="5" strokeLinecap="round" />
          <path d="M700 84 q50 -9 100 -2 t90 -4" fill="none" stroke="#ffffff" strokeOpacity="0.28" strokeWidth="4" strokeLinecap="round" />
          <path d="M880 72 q40 -7 90 0 t120 -5" fill="none" stroke="#ffffff" strokeOpacity="0.3" strokeWidth="6" strokeLinecap="round" />
          <path d="M640 112 q50 -10 110 -2" fill="none" stroke="#ffffff" strokeOpacity="0.22" strokeWidth="4" strokeLinecap="round" />
        </g>
      </g>
      <circle cx="820" cy="1100" r="1070" fill="none" stroke="#bff3ff" strokeOpacity="0.75" strokeWidth="1.5" />
    </svg>
  );
}

/** Crew capsule with a service module, solar wings and an engine glow. Points right. */
function Spacecraft() {
  return (
    <svg className="scene__ship" viewBox="0 0 150 60" aria-hidden="true">
      <g className="ship__flame">
        <path d="M30 30 L4 24 Q-2 30 4 36 Z" fill="#ff9a3c" />
        <path d="M30 30 L14 27 Q11 30 14 33 Z" fill="#ffe2a8" />
      </g>
      {/* solar wings */}
      <g>
        <rect x="40" y="2" width="34" height="16" rx="1.5" fill="#2d5fa8" stroke="#a9c8ef" strokeWidth="1" />
        <path d="M51 2v16M62 2v16M40 10h34" stroke="#a9c8ef" strokeWidth="0.8" />
        <rect x="40" y="42" width="34" height="16" rx="1.5" fill="#2d5fa8" stroke="#a9c8ef" strokeWidth="1" />
        <path d="M51 42v16M62 42v16M40 50h34" stroke="#a9c8ef" strokeWidth="0.8" />
        <path d="M57 18v6M57 36v6" stroke="#cfd8e6" strokeWidth="2" />
      </g>
      {/* service module */}
      <rect x="30" y="22" width="56" height="16" rx="3" fill="#e9eef5" stroke="#8e9bad" strokeWidth="1" />
      <path d="M44 22v16M72 22v16" stroke="#b5c2d1" strokeWidth="1" />
      {/* crew capsule */}
      <path d="M86 20 L118 26 Q130 30 118 34 L86 40 Z" fill="#ffffff" stroke="#8e9bad" strokeWidth="1" />
      <path d="M100 26 l8 1.5 v5 l-8 1.5 z" fill="#0e1a2b" />
      <circle cx="112" cy="30" r="1.6" fill="#e8601c" />
    </svg>
  );
}

/** Tethered astronaut on a spacewalk, drawn for this project. */
function Astronaut() {
  return (
    <svg className="scene__astro" viewBox="0 0 170 110" aria-hidden="true">
      {/* tether runs off to the right, towards the (unseen) vehicle */}
      <path className="astro__tether" d="M70 62 C 100 92, 130 30, 172 52" fill="none" stroke="#e6edf8" strokeWidth="1.6" strokeDasharray="1 3.2" strokeLinecap="round" />
      <g className="astro__body">
        {/* backpack */}
        <rect x="18" y="34" width="20" height="30" rx="4" fill="#cfd8e6" stroke="#8e9bad" strokeWidth="1" />
        {/* legs */}
        <path d="M44 66 q-6 14 -2 26" stroke="#f5f8fc" strokeWidth="10" strokeLinecap="round" fill="none" />
        <path d="M54 66 q8 10 18 14" stroke="#f5f8fc" strokeWidth="10" strokeLinecap="round" fill="none" />
        <path d="M44 66 q-6 14 -2 26M54 66 q8 10 18 14" stroke="#8e9bad" strokeWidth="11.5" strokeLinecap="round" fill="none" opacity="0.35" />
        {/* torso */}
        <rect x="34" y="36" width="28" height="34" rx="9" fill="#f5f8fc" stroke="#8e9bad" strokeWidth="1" />
        <rect x="41" y="46" width="14" height="9" rx="2" fill="#dbe3ee" stroke="#8e9bad" strokeWidth="0.8" />
        <circle cx="44.5" cy="50.5" r="1.6" fill="#e8601c" />
        {/* arms: one waving */}
        <path className="astro__wave" d="M60 42 q14 -6 20 -18" stroke="#f5f8fc" strokeWidth="9" strokeLinecap="round" fill="none" />
        <path d="M36 44 q-10 8 -8 20" stroke="#f5f8fc" strokeWidth="9" strokeLinecap="round" fill="none" />
        {/* helmet */}
        <circle cx="48" cy="24" r="15" fill="#f5f8fc" stroke="#8e9bad" strokeWidth="1" />
        <path d="M37 22 q11 -10 23 0 q1 10 -11.5 12 q-12.5 -2 -11.5 -12 Z" fill="#f6c879" stroke="#b07d2a" strokeWidth="0.8" />
        <path d="M41 20 q5 -4 11 -3.5" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" fill="none" opacity="0.9" />
      </g>
    </svg>
  );
}

/** Everything that moves behind the header content. */
export function HeaderScene() {
  return (
    <div className="scene" aria-hidden="true">
      <Stars />
      <Earth />
      <span className="scene__meteor" />
      <span className="scene__meteor scene__meteor--late" />
      <div className="scene__ship-lane"><Spacecraft /></div>
      <div className="scene__astro-wrap"><Astronaut /></div>
    </div>
  );
}

/** Faint, slowly drifting star dust and an orbiting satellite behind the light page body. */
export function Cosmos() {
  return (
    <div className="cosmos" aria-hidden="true">
      <svg className="cosmos__orbit" viewBox="0 0 600 600">
        <g transform="translate(300 300) rotate(-18) scale(1 0.34)">
          <circle r="260" fill="none" stroke="currentColor" strokeWidth="2.4" strokeDasharray="4 10" />
          <g className="cosmos__sat">
            <g transform="translate(260 0) scale(1 2.9)">
              <rect x="-9" y="-2.5" width="7" height="5" fill="#2d5fa8" />
              <rect x="2" y="-2.5" width="7" height="5" fill="#2d5fa8" />
              <rect x="-2.5" y="-3" width="5" height="6" rx="1" fill="#e8601c" />
            </g>
          </g>
        </g>
        <circle cx="120" cy="470" r="34" fill="currentColor" opacity="0.35" />
        <circle cx="108" cy="460" r="7" fill="#ffffff" opacity="0.5" />
      </svg>
    </div>
  );
}
