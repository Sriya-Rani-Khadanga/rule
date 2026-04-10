import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@/contexts/ThemeContext";
import { useStore, TaalEvent } from "@/store/useStore";
import Header from "@/components/Header";
import BackgroundEffects from "@/components/BackgroundEffects";
import PageTransition from "@/components/PageTransition";

interface EventForm {
  name: string;
  date: string;
  startTime: string;
  endTime: string;
  priority: number;
  category: string;
}

const emptyEvent: EventForm = {
  name: "",
  date: "",
  startTime: "",
  endTime: "",
  priority: 50,
  category: "work",
};

const categories = [
  { value: "work", label: "💼 Work", emoji: "💼" },
  { value: "personal", label: "🏠 Personal", emoji: "🏠" },
  { value: "health", label: "🏃 Health", emoji: "🏃" },
  { value: "social", label: "🎉 Social", emoji: "🎉" },
  { value: "education", label: "📚 Education", emoji: "📚" },
];

const getPriorityColor = (value: number, isTech: boolean) => {
  if (value < 33) return isTech ? "hsl(185, 100%, 50%)" : "hsl(45, 90%, 55%)";
  if (value < 66) return isTech ? "hsl(220, 80%, 60%)" : "hsl(36, 90%, 50%)";
  return isTech ? "hsl(260, 80%, 60%)" : "hsl(340, 65%, 47%)";
};

const getPriorityLabel = (value: number) => {
  if (value < 33) return "Low";
  if (value < 66) return "Medium";
  return "High";
};

const InputPage = () => {
  const { mode } = useTheme();
  const isTech = mode === "tech";
  const navigate = useNavigate();
  const { setEvents: setStoreEvents, setResolution } = useStore();
  const [events, setEvents] = useState<EventForm[]>([{ ...emptyEvent }]);

  const updateEvent = (index: number, field: keyof EventForm, value: string | number) => {
    setEvents((prev) =>
      prev.map((e, i) => (i === index ? { ...e, [field]: value } : e))
    );
  };

  const addEvent = () => {
    setEvents((prev) => [...prev, { ...emptyEvent }]);
  };

  const removeEvent = (index: number) => {
    if (events.length > 1) {
      setEvents((prev) => prev.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = () => {
    // Convert form events to TaalEvent with IDs and push to Zustand store
    const taalEvents: TaalEvent[] = events
      .filter((e) => e.name && e.date && e.startTime && e.endTime)
      .map((e) => ({
        id: crypto.randomUUID(),
        ...e,
      }));

    if (taalEvents.length === 0) return;

    setStoreEvents(taalEvents);
    setResolution(null); // clear old results
    navigate("/conflicts");
  };

  return (
    <PageTransition>
      <Header />
      <BackgroundEffects />
      <main className="relative z-10 min-h-screen pt-24 pb-16 px-6">
        <div className="container mx-auto max-w-3xl">
          {/* Page title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className={`text-4xl md:text-5xl font-heading font-bold mb-3 ${isTech ? "neon-glow" : ""}`}>
              {isTech ? "⚡ Mission Input" : "🪷 Add Your Events"}
            </h1>
            <p className="text-muted-foreground font-body text-lg">
              {isTech ? "Enter event parameters for conflict analysis." : "Tell us what's on your plate — we'll find the harmony."}
            </p>
          </motion.div>

          {/* Event Cards */}
          <div className="space-y-6">
            {events.map((event, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass rounded-2xl p-6 relative group"
              >
                {events.length > 1 && (
                  <button
                    onClick={() => removeEvent(index)}
                    className="absolute top-4 right-4 w-8 h-8 rounded-full bg-destructive/10 text-destructive flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-sm font-bold"
                  >
                    ×
                  </button>
                )}

                <div className="flex items-center gap-2 mb-5">
                  <span className="text-lg font-heading text-primary">
                    {isTech ? `Event #${index + 1}` : `Event ${index + 1}`}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-heading text-muted-foreground mb-1.5">Event Name</label>
                    <input
                      type="text"
                      value={event.name}
                      onChange={(e) => updateEvent(index, "name", e.target.value)}
                      placeholder={isTech ? "Operation codename..." : "e.g., Morning Yoga 🧘"}
                      className="w-full px-4 py-3 rounded-xl bg-background/50 border border-border text-foreground font-body placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-heading text-muted-foreground mb-1.5">Date</label>
                    <input
                      type="date"
                      value={event.date}
                      onChange={(e) => updateEvent(index, "date", e.target.value)}
                      className="w-full px-4 py-3 rounded-xl bg-background/50 border border-border text-foreground font-body focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-heading text-muted-foreground mb-1.5">Category</label>
                    <select
                      value={event.category}
                      onChange={(e) => updateEvent(index, "category", e.target.value)}
                      className="w-full px-4 py-3 rounded-xl bg-background/50 border border-border text-foreground font-body focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    >
                      {categories.map((cat) => (
                        <option key={cat.value} value={cat.value}>{cat.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-heading text-muted-foreground mb-1.5">Start Time</label>
                    <input
                      type="time"
                      value={event.startTime}
                      onChange={(e) => updateEvent(index, "startTime", e.target.value)}
                      className="w-full px-4 py-3 rounded-xl bg-background/50 border border-border text-foreground font-body focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-heading text-muted-foreground mb-1.5">End Time</label>
                    <input
                      type="time"
                      value={event.endTime}
                      onChange={(e) => updateEvent(index, "endTime", e.target.value)}
                      className="w-full px-4 py-3 rounded-xl bg-background/50 border border-border text-foreground font-body focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                  </div>
                </div>

                {/* Priority Slider */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-heading text-muted-foreground">Priority</label>
                    <span
                      className="text-sm font-heading font-bold px-3 py-0.5 rounded-full"
                      style={{
                        color: getPriorityColor(event.priority, isTech),
                        backgroundColor: `${getPriorityColor(event.priority, isTech)}20`,
                      }}
                    >
                      {getPriorityLabel(event.priority)}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={event.priority}
                    onChange={(e) => updateEvent(index, "priority", parseInt(e.target.value))}
                    className="w-full h-2 rounded-full appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(90deg, ${isTech ? "hsl(185,100%,50%)" : "hsl(45,90%,55%)"} 0%, ${isTech ? "hsl(260,80%,60%)" : "hsl(340,65%,47%)"} 100%)`,
                    }}
                  />
                </div>
              </motion.div>
            ))}
          </div>

          {/* Action buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 mt-8 justify-center"
          >
            <button
              onClick={addEvent}
              className="px-8 py-3 rounded-full font-heading text-sm border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-all"
            >
              + Add Another Event
            </button>
            <button
              onClick={handleSubmit}
              className={`px-8 py-3 rounded-full font-heading text-sm font-bold bg-primary text-primary-foreground shadow-glow transition-all hover:scale-105 ${isTech ? "neon-border" : ""}`}
            >
              {isTech ? "🚀 Analyze Conflicts" : "🪷 Find Balance"}
            </button>
          </motion.div>
        </div>
      </main>
    </PageTransition>
  );
};

export default InputPage;
