import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@/contexts/ThemeContext";
import { useStore } from "@/store/useStore";
import Header from "@/components/Header";
import BackgroundEffects from "@/components/BackgroundEffects";
import PageTransition from "@/components/PageTransition";

const categoryColors: Record<string, string> = {
  work: "hsl(220, 70%, 55%)",
  personal: "hsl(36, 80%, 55%)",
  health: "hsl(150, 60%, 45%)",
  social: "hsl(340, 65%, 50%)",
  education: "hsl(45, 70%, 50%)",
};

const formatTime12 = (t: string): string => {
  const [h, m] = t.split(":").map(Number);
  const ampm = h >= 12 ? "pm" : "am";
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${h12}:${String(m).padStart(2, "0")}${ampm}`;
};

const ResultsPage = () => {
  const { mode } = useTheme();
  const isTech = mode === "tech";
  const navigate = useNavigate();
  const { resolution } = useStore();
  const [visibleLines, setVisibleLines] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  const explanations = resolution?.explanations ?? [];
  const resolvedEvents = resolution?.resolvedEvents ?? [];
  const metrics = resolution?.metrics;

  useEffect(() => {
    if (visibleLines < explanations.length) {
      const timeout = setTimeout(() => setVisibleLines((v) => v + 1), 600);
      return () => clearTimeout(timeout);
    }
  }, [visibleLines, explanations.length]);

  if (!resolution) {
    return (
      <PageTransition>
        <Header />
        <BackgroundEffects />
        <main className="relative z-10 min-h-screen pt-24 pb-16 px-6 flex items-center justify-center">
          <div className="text-center">
            <p className="text-muted-foreground text-lg mb-4">No results yet — resolve conflicts first.</p>
            <button onClick={() => navigate("/input")} className="px-8 py-3 rounded-full font-heading text-sm font-bold bg-primary text-primary-foreground shadow-glow">
              ← Add Events
            </button>
          </div>
        </main>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <Header />
      <BackgroundEffects />
      <main className="relative z-10 min-h-screen pt-24 pb-16 px-6">
        <div className="container mx-auto max-w-5xl">
          {/* Title */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
            <h1 className={`text-4xl md:text-5xl font-heading font-bold mb-3 ${isTech ? "neon-glow" : ""}`}>
              {isTech ? "📊 Mission Complete" : "🌸 Your Balanced Day"}
            </h1>
            <p className="text-muted-foreground font-body text-lg">
              {isTech ? "Optimized schedule deployed successfully." : "Every event has found its perfect place."}
            </p>
          </motion.div>

          {/* Timeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-2xl p-6 mb-8"
          >
            <h2 className={`text-lg font-heading font-bold mb-5 ${isTech ? "neon-glow" : ""}`}>
              {isTech ? "Timeline View" : "Your Day Flow"}
            </h2>

            <div ref={scrollRef} className="overflow-x-auto pb-4">
              <div className="flex gap-4 min-w-max">
                {resolvedEvents.map((event, i) => {
                  const color = categoryColors[event.category] ?? "hsl(220, 70%, 55%)";
                  return (
                    <motion.div
                      key={event.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + i * 0.08 }}
                      whileHover={{ y: -6, scale: 1.03 }}
                      className={`relative flex-shrink-0 w-44 p-4 rounded-2xl cursor-pointer transition-all duration-300 ${isTech ? "neon-border" : ""}`}
                      style={{
                        backgroundColor: `${color}15`,
                        borderLeft: `3px solid ${color}`,
                      }}
                    >
                      <div className="text-xs font-heading font-bold mb-1 uppercase tracking-wider" style={{ color }}>
                        {event.category}
                      </div>
                      <div className="font-heading text-sm font-bold text-foreground mb-1">{event.name}</div>
                      <div className="text-xs font-body text-muted-foreground">
                        {formatTime12(event.startTime)} – {formatTime12(event.endTime)}
                      </div>
                      {event.wasShifted && (
                        <div className="mt-2 text-[10px] font-heading px-2 py-0.5 rounded-full bg-primary/10 text-primary inline-block">
                          ⏱ Shifted
                        </div>
                      )}
                      {i < resolvedEvents.length - 1 && (
                        <div className="absolute top-1/2 -right-4 w-4 h-px bg-border" />
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>

          {/* Terminal Typewriter */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className={`rounded-2xl p-6 mb-8 font-mono text-sm overflow-hidden ${
              isTech
                ? "bg-[hsl(225,50%,5%)] border border-[hsl(185,100%,50%,0.2)] neon-border"
                : "bg-[hsl(25,40%,10%)] border border-[hsl(36,90%,50%,0.2)]"
            }`}
          >
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-destructive" />
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "hsl(45, 90%, 50%)" }} />
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "hsl(140, 60%, 50%)" }} />
              <span className="ml-3 text-xs text-muted-foreground font-heading">
                {isTech ? "taalmel-resolver v2.0" : "taalmel ~ harmony engine"}
              </span>
            </div>

            <div className="space-y-1.5">
              {explanations.slice(0, visibleLines).map((line, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`
                    ${line.includes("✅") ? "text-[hsl(140,70%,55%)]" : ""}
                    ${line.includes("Conflict") ? "text-[hsl(36,90%,60%)]" : ""}
                    ${line.includes("Strategy") ? "text-[hsl(185,80%,60%)]" : ""}
                    ${!line.includes("✅") && !line.includes("Conflict") && !line.includes("Strategy") ? "text-muted-foreground" : ""}
                  `}
                >
                  {line}
                </motion.div>
              ))}
              {visibleLines < explanations.length && (
                <span className="inline-block w-2 h-4 bg-primary animate-pulse-glow" />
              )}
            </div>
          </motion.div>

          {/* Metrics / Gauges */}
          {metrics && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
            >
              {[
                { label: "Events", value: String(metrics.totalEvents), icon: "📋" },
                { label: "Conflicts Fixed", value: String(metrics.conflictsResolved), icon: "✅" },
                { label: "Efficiency", value: `${metrics.efficiency}%`, icon: "⚡" },
                { label: "Free Time", value: `${metrics.freeTimeHours}h`, icon: "☀️" },
                { label: "Satisfaction", value: `${metrics.satisfactionScore}%`, icon: isTech ? "🎛️" : "🪘" },
                { label: "Fairness", value: `${metrics.fairnessScore}%`, icon: isTech ? "⚖️" : "🌿" },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 + i * 0.1 }}
                  className={`glass rounded-2xl p-5 text-center ${isTech ? "neon-border" : ""}`}
                >
                  <div className="text-2xl mb-2">{stat.icon}</div>
                  <div className="text-2xl font-heading font-bold text-primary">{stat.value}</div>
                  <div className="text-xs font-heading text-muted-foreground mt-1">{stat.label}</div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </main>
    </PageTransition>
  );
};

export default ResultsPage;
