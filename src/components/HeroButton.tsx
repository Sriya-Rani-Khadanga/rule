import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "@/contexts/ThemeContext";

const HeroButton = () => {
  const { mode } = useTheme();
  const isTech = mode === "tech";
  const [particles, setParticles] = useState<{ id: number; x: number; y: number }[]>([]);

  const handleHover = () => {
    const newParticles = Array.from({ length: 8 }).map((_, i) => ({
      id: Date.now() + i,
      x: (Math.random() - 0.5) * 200,
      y: (Math.random() - 0.5) * 200,
    }));
    setParticles(newParticles);
    setTimeout(() => setParticles([]), 800);
  };

  return (
    <div className="relative inline-block">
      {/* Particle burst */}
      <AnimatePresence>
        {particles.map((p) => (
          <motion.div
            key={p.id}
            className="absolute top-1/2 left-1/2 pointer-events-none"
            initial={{ x: 0, y: 0, scale: 1, opacity: 1 }}
            animate={{ x: p.x, y: p.y, scale: 0, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            {isTech ? (
              <div className="w-2 h-2 rounded-full bg-primary shadow-glow" />
            ) : (
              <div
                className="w-3 h-3 rounded-full"
                style={{
                  background: `hsl(${Math.random() * 60 + 330} 70% 60%)`,
                }}
              />
            )}
          </motion.div>
        ))}
      </AnimatePresence>

      <motion.button
        onHoverStart={handleHover}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.97 }}
        className={`
          relative px-10 py-4 rounded-full font-heading font-bold text-lg tracking-wider
          transition-all duration-500 overflow-hidden
          ${isTech
            ? "bg-primary text-primary-foreground neon-border shadow-glow"
            : "bg-primary text-primary-foreground shadow-glow"
          }
        `}
      >
        {/* Glow halo */}
        <motion.div
          className="absolute inset-0 rounded-full opacity-0"
          whileHover={{ opacity: 0.3 }}
          style={{
            background: isTech
              ? "radial-gradient(circle, hsl(185 100% 50% / 0.4), transparent 70%)"
              : "radial-gradient(circle, hsl(36 90% 50% / 0.4), transparent 70%)",
          }}
        />
        <span className="relative z-10">Start Scheduling</span>
      </motion.button>
    </div>
  );
};

export default HeroButton;
