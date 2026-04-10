import { useTheme } from "@/contexts/ThemeContext";

const MandalaSVG = ({ className = "", neon = false }: { className?: string; neon?: boolean }) => {
  const stroke = neon ? "hsl(185 100% 50%)" : "hsl(36 90% 50%)";
  const strokeSecondary = neon ? "hsl(260 80% 60%)" : "hsl(340 65% 47%)";
  const opacity = neon ? 0.3 : 0.15;

  return (
    <svg
      viewBox="0 0 400 400"
      className={className}
      style={{ opacity }}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer ring */}
      <circle cx="200" cy="200" r="190" stroke={stroke} strokeWidth="0.5" />
      <circle cx="200" cy="200" r="170" stroke={strokeSecondary} strokeWidth="0.5" />
      <circle cx="200" cy="200" r="140" stroke={stroke} strokeWidth="0.5" />
      <circle cx="200" cy="200" r="100" stroke={strokeSecondary} strokeWidth="0.5" />
      <circle cx="200" cy="200" r="60" stroke={stroke} strokeWidth="0.5" />

      {/* Petals */}
      {Array.from({ length: 12 }).map((_, i) => {
        const angle = (i * 30 * Math.PI) / 180;
        const x1 = 200 + Math.cos(angle) * 60;
        const y1 = 200 + Math.sin(angle) * 60;
        const x2 = 200 + Math.cos(angle) * 170;
        const y2 = 200 + Math.sin(angle) * 170;
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={stroke} strokeWidth="0.3" />;
      })}

      {/* Inner petals */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i * 45 * Math.PI) / 180;
        const cx = 200 + Math.cos(angle) * 120;
        const cy = 200 + Math.sin(angle) * 120;
        return <circle key={`p${i}`} cx={cx} cy={cy} r="20" stroke={strokeSecondary} strokeWidth="0.4" />;
      })}

      {/* Decorative arcs */}
      {Array.from({ length: 6 }).map((_, i) => {
        const angle = i * 60;
        return (
          <path
            key={`arc${i}`}
            d={`M ${200 + Math.cos((angle * Math.PI) / 180) * 140} ${200 + Math.sin((angle * Math.PI) / 180) * 140} 
                Q 200 200 
                ${200 + Math.cos(((angle + 60) * Math.PI) / 180) * 140} ${200 + Math.sin(((angle + 60) * Math.PI) / 180) * 140}`}
            stroke={stroke}
            strokeWidth="0.3"
          />
        );
      })}
    </svg>
  );
};

const CulturalBackground = () => (
  <div className="fixed inset-0 overflow-hidden pointer-events-none">
    <MandalaSVG className="absolute -top-20 -right-20 w-[500px] h-[500px]" />
    <MandalaSVG className="absolute -bottom-32 -left-32 w-[600px] h-[600px]" />
    <MandalaSVG className="absolute top-1/3 left-1/2 w-[300px] h-[300px] -translate-x-1/2" />

    {/* Subtle drum silhouettes */}
    <div className="absolute bottom-10 right-10 opacity-[0.06]">
      <svg width="120" height="100" viewBox="0 0 120 100" fill="hsl(36 90% 50%)">
        <ellipse cx="60" cy="15" rx="50" ry="15" />
        <rect x="10" y="15" width="100" height="60" />
        <ellipse cx="60" cy="75" rx="50" ry="15" />
      </svg>
    </div>
  </div>
);

const TechBackground = () => (
  <div className="fixed inset-0 overflow-hidden pointer-events-none">
    {/* Grid floor */}
    <div
      className="absolute inset-0"
      style={{
        backgroundImage: `
          linear-gradient(hsla(185, 100%, 50%, 0.05) 1px, transparent 1px),
          linear-gradient(90deg, hsla(185, 100%, 50%, 0.05) 1px, transparent 1px)
        `,
        backgroundSize: "50px 50px",
        animation: "grid-scroll 4s linear infinite",
      }}
    />

    {/* Neon mandalas */}
    <MandalaSVG className="absolute -top-20 -right-20 w-[500px] h-[500px]" neon />
    <MandalaSVG className="absolute -bottom-32 -left-32 w-[600px] h-[600px]" neon />

    {/* Floating particles */}
    {Array.from({ length: 20 }).map((_, i) => (
      <div
        key={i}
        className="absolute w-1 h-1 rounded-full bg-primary"
        style={{
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
          opacity: 0.3 + Math.random() * 0.4,
          animation: `float-particle ${3 + Math.random() * 4}s ease-in-out infinite`,
          animationDelay: `${Math.random() * 3}s`,
        }}
      />
    ))}
  </div>
);

const BackgroundEffects = () => {
  const { mode } = useTheme();
  return mode === "cultural" ? <CulturalBackground /> : <TechBackground />;
};

export default BackgroundEffects;
