import { useTheme } from "@/contexts/ThemeContext";

const TaalMelLogo = ({ size = "lg" }: { size?: "sm" | "lg" }) => {
  const { mode } = useTheme();
  const isTech = mode === "tech";
  const dim = size === "lg" ? 48 : 32;

  return (
    <div className="flex items-center gap-3">
      {/* Logo icon: Tabla + Circuit */}
      <svg
        width={dim}
        height={dim}
        viewBox="0 0 48 48"
        fill="none"
        className="transition-all duration-500"
      >
        {/* Tabla body */}
        <ellipse cx="24" cy="12" rx="16" ry="6" stroke="hsl(var(--primary))" strokeWidth="1.5" fill="none" />
        <path d="M8 12 L8 34 Q8 42 24 42 Q40 42 40 34 L40 12" stroke="hsl(var(--primary))" strokeWidth="1.5" fill="none" />
        <ellipse cx="24" cy="34" rx="16" ry="8" stroke="hsl(var(--primary))" strokeWidth="1" fill="none" opacity="0.5" />

        {/* Circuit pulse line */}
        <path
          d="M6 24 L14 24 L18 18 L22 30 L26 18 L30 30 L34 24 L42 24"
          stroke="hsl(var(--accent))"
          strokeWidth="1.5"
          strokeLinecap="round"
          className={isTech ? "neon-glow" : ""}
        />

        {/* Circuit dots */}
        <circle cx="6" cy="24" r="2" fill="hsl(var(--accent))" />
        <circle cx="42" cy="24" r="2" fill="hsl(var(--accent))" />
      </svg>

      {/* Brand name */}
      <div className="flex items-baseline">
        <span
          className="font-heading font-bold tracking-wide transition-all duration-500"
          style={{ fontSize: size === "lg" ? "1.5rem" : "1.1rem" }}
        >
          Taal
        </span>
        <span
          className="font-hindi font-bold text-primary transition-all duration-500"
          style={{ fontSize: size === "lg" ? "1.6rem" : "1.2rem" }}
        >
          मेल
        </span>
      </div>
    </div>
  );
};

export default TaalMelLogo;
