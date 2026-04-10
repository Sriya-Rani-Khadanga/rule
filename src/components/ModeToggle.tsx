import { useTheme } from "@/contexts/ThemeContext";
import { motion } from "framer-motion";

const ModeToggle = () => {
  const { mode, toggle, isTransitioning } = useTheme();
  const isTech = mode === "tech";

  return (
    <button
      onClick={toggle}
      disabled={isTransitioning}
      className="relative flex items-center gap-3 px-4 py-2 rounded-full glass neon-border transition-all duration-500 hover:shadow-glow group"
      aria-label="Toggle theme mode"
    >
      <span className="text-sm font-heading text-muted-foreground">
        {isTech ? "🎪" : "🎪"} Cultural
      </span>

      <div className="relative w-14 h-7 rounded-full bg-muted overflow-hidden">
        <motion.div
          className="absolute top-0.5 w-6 h-6 rounded-full"
          animate={{
            left: isTech ? "calc(100% - 26px)" : "2px",
            backgroundColor: isTech ? "hsl(185 100% 50%)" : "hsl(36 90% 50%)",
          }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
        {isTech && (
          <motion.div
            className="absolute inset-0 rounded-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
              background: "linear-gradient(90deg, transparent, hsla(185, 100%, 50%, 0.15))",
            }}
          />
        )}
      </div>

      <span className="text-sm font-heading text-muted-foreground">
        Tech {isTech ? "🚀" : "🚀"}
      </span>
    </button>
  );
};

export default ModeToggle;
