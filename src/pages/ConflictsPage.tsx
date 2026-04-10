import { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@/contexts/ThemeContext";
import { useStore } from "@/store/useStore";
import { resolveSchedule } from "@/lib/resolver";
import Header from "@/components/Header";
import BackgroundEffects from "@/components/BackgroundEffects";
import PageTransition from "@/components/PageTransition";

const getHeatColor = (intensity: number, isTech: boolean) => {
  if (intensity < 0.3) return isTech ? "hsla(185, 100%, 50%, 0.1)" : "hsla(120, 60%, 50%, 0.15)";
  if (intensity < 0.5) return isTech ? "hsla(185, 100%, 50%, 0.25)" : "hsla(60, 70%, 50%, 0.25)";
  if (intensity < 0.7) return isTech ? "hsla(220, 80%, 60%, 0.4)" : "hsla(36, 90%, 50%, 0.35)";
  if (intensity < 0.85) return isTech ? "hsla(260, 80%, 60%, 0.6)" : "hsla(20, 80%, 50%, 0.5)";
  return isTech ? "hsla(300, 80%, 50%, 0.8)" : "hsla(0, 70%, 50%, 0.65)";
};

const timeToMin = (t: string) => {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + (m || 0);
};

const ConflictsPage = () => {
  const { mode } = useTheme();
  const isTech = mode === "tech";
  const navigate = useNavigate();
  const { events, setResolution, setIsResolving } = useStore();
  const [radarAngle, setRadarAngle] = useState(0);
  const [selectedCell, setSelectedCell] = useState<{ day: string; hour: number } | null>(null);

  // Build heatmap from real events
  const hours = Array.from({ length: 12 }, (_, i) => i + 7);
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  const heatmapData = useMemo(() => {
    const data: { day: string; hour: number; intensity: number; events: string[] }[] = [];
    const dayMap: Record<string, number> = { 0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5 }; // JS day → Mon=0

    days.forEach((day, dayIdx) => {
      hours.forEach((hour) => {
        // Find events in this slot
        const slotEvents = events.filter((e) => {
          const d = new Date(e.date);
          const mappedDay = dayMap[d.getDay()];
          if (mappedDay !== dayIdx) return false;
          const start = timeToMin(e.startTime);
          const end = timeToMin(e.endTime);
          const slotStart = hour * 60;
          const slotEnd = (hour + 1) * 60;
          return start < slotEnd && end > slotStart;
        });

        const intensity = slotEvents.length === 0 ? Math.random() * 0.15 :
          slotEvents.length === 1 ? 0.4 + (slotEvents[0].priority / 100) * 0.2 :
            0.7 + Math.min(0.3, (slotEvents.length - 1) * 0.15);

        data.push({
          day,
          hour,
          intensity: Math.min(1, intensity),
          events: slotEvents.map((e) => e.name),
        });
      });
    });
    return data;
  }, [events]);

  const conflicts = heatmapData.filter((d) => d.intensity > 0.7);

  useEffect(() => {
    if (!isTech) return;
    const interval = setInterval(() => setRadarAngle((prev) => (prev + 2) % 360), 50);
    return () => clearInterval(interval);
  }, [isTech]);

  const handleResolve = () => {
    setIsResolving(true);
    // Simulate processing delay for the rocket animation feel
    setTimeout(() => {
      const result = resolveSchedule(events);
      setResolution(result);
      setIsResolving(false);
      navigate("/results");
    }, 1500);
  };

  return (
    <PageTransition>
      <Header />
      <BackgroundEffects />
      <main className="relative z-10 min-h-screen pt-24 pb-16 px-6">
        <div className="container mx-auto max-w-5xl">
          {/* Title */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
            <h1 className={`text-4xl md:text-5xl font-heading font-bold mb-3 ${isTech ? "neon-glow" : ""}`}>
              {isTech ? "📡 Conflict Radar" : "🎨 Event Tapestry"}
            </h1>
            <p className="text-muted-foreground font-body text-lg">
              {isTech
                ? `Scanning ${events.length} events for scheduling collisions...`
                : `Weaving your ${events.length} events into a harmonious pattern.`}
            </p>
          </motion.div>

          {/* No events fallback */}
          {events.length === 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-20">
              <p className="text-muted-foreground text-lg mb-4">No events loaded yet.</p>
              <button
                onClick={() => navigate("/input")}
                className="px-8 py-3 rounded-full font-heading text-sm font-bold bg-primary text-primary-foreground shadow-glow"
              >
                ← Add Events
              </button>
            </motion.div>
          )}

          {events.length > 0 && (
            <>
              {/* Heatmap */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="glass rounded-2xl p-6 mb-8 relative overflow-hidden"
              >
                {isTech && (
                  <div
                    className="absolute inset-0 pointer-events-none z-10"
                    style={{
                      background: `conic-gradient(from ${radarAngle}deg at 50% 50%, hsla(185, 100%, 50%, 0.08) 0deg, transparent 60deg, transparent 360deg)`,
                    }}
                  />
                )}

                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr>
                        <th className="p-2 text-xs font-heading text-muted-foreground" />
                        {hours.map((h) => (
                          <th key={h} className="p-2 text-xs font-heading text-muted-foreground">
                            {h > 12 ? `${h - 12}pm` : h === 12 ? "12pm" : `${h}am`}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {days.map((day) => (
                        <tr key={day}>
                          <td className="p-2 text-xs font-heading text-muted-foreground font-bold">{day}</td>
                          {hours.map((hour) => {
                            const cell = heatmapData.find((d) => d.day === day && d.hour === hour);
                            const isSelected = selectedCell?.day === day && selectedCell?.hour === hour;
                            return (
                              <td key={hour} className="p-1">
                                <motion.div
                                  whileHover={{ scale: 1.2 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => setSelectedCell(isSelected ? null : { day, hour })}
                                  className={`w-full aspect-square rounded-lg cursor-pointer transition-all duration-300 min-w-[32px]
                                    ${isSelected ? "ring-2 ring-primary" : ""}
                                    ${isTech ? "rounded-sm" : "rounded-xl"}`}
                                  style={{
                                    backgroundColor: getHeatColor(cell?.intensity ?? 0, isTech),
                                    boxShadow: (cell?.intensity ?? 0) > 0.7 && isTech
                                      ? `0 0 8px ${getHeatColor(cell?.intensity ?? 0, isTech)}` : "none",
                                  }}
                                />
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Selected cell info */}
                {selectedCell && (() => {
                  const cell = heatmapData.find((d) => d.day === selectedCell.day && d.hour === selectedCell.hour);
                  return cell && cell.events.length > 0 ? (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 p-3 rounded-xl bg-background/50 border border-border">
                      <span className="text-xs font-heading text-primary">{selectedCell.day} {selectedCell.hour > 12 ? selectedCell.hour - 12 : selectedCell.hour}:00{selectedCell.hour >= 12 ? "pm" : "am"}</span>
                      <div className="text-sm font-body text-foreground mt-1">{cell.events.join(", ")}</div>
                    </motion.div>
                  ) : null;
                })()}

                {/* Legend */}
                <div className="flex items-center justify-center gap-2 mt-4 text-xs font-heading text-muted-foreground">
                  <span>Free</span>
                  <div className="flex gap-0.5">
                    {[0.1, 0.3, 0.5, 0.7, 0.9].map((v) => (
                      <div key={v} className="w-5 h-3 rounded-sm" style={{ backgroundColor: getHeatColor(v, isTech) }} />
                    ))}
                  </div>
                  <span>Conflict</span>
                </div>
              </motion.div>

              {/* Conflict List */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="glass rounded-2xl p-6 mb-8"
              >
                <h2 className={`text-xl font-heading font-bold mb-4 ${isTech ? "neon-glow" : ""}`}>
                  {isTech ? "⚠️ Detected Collisions" : "🔴 Overlapping Events"} ({conflicts.length})
                </h2>
                <div className="space-y-3">
                  {conflicts.slice(0, 5).map((c, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + i * 0.1 }}
                      className="flex items-center gap-4 p-3 rounded-xl bg-background/30 border border-border"
                    >
                      <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: getHeatColor(c.intensity, isTech) }} />
                      <div className="flex-1">
                        <span className="font-heading text-sm font-bold">
                          {c.day} at {c.hour > 12 ? c.hour - 12 : c.hour}:00{c.hour >= 12 ? "pm" : "am"}
                        </span>
                        <span className="text-muted-foreground text-xs ml-2 font-body">
                          {c.events.join(" × ") || "Multiple events"}
                        </span>
                      </div>
                      <span className="text-xs font-heading px-2 py-1 rounded-full bg-destructive/10 text-destructive">
                        {Math.round(c.intensity * 100)}% clash
                      </span>
                    </motion.div>
                  ))}
                  {conflicts.length === 0 && (
                    <p className="text-muted-foreground text-sm text-center py-4">
                      {isTech ? "No collisions detected." : "No overlapping events found!"}
                    </p>
                  )}
                </div>
              </motion.div>

              {/* Action */}
              <div className="flex justify-center">
                <button
                  onClick={handleResolve}
                  className={`px-8 py-3 rounded-full font-heading text-sm font-bold bg-primary text-primary-foreground shadow-glow transition-all hover:scale-105 ${isTech ? "neon-border" : ""}`}
                >
                  {isTech ? "🚀 Resolve Conflicts" : "✨ Harmonize Schedule"}
                </button>
              </div>
            </>
          )}
        </div>
      </main>
    </PageTransition>
  );
};

export default ConflictsPage;
