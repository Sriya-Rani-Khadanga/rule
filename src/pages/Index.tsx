import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@/contexts/ThemeContext";
import Header from "@/components/Header";
import HeroButton from "@/components/HeroButton";
import BackgroundEffects from "@/components/BackgroundEffects";
import TaalMelLogo from "@/components/TaalMelLogo";
import PageTransition from "@/components/PageTransition";

const Index = () => {
  const { mode } = useTheme();
  const isTech = mode === "tech";
  const navigate = useNavigate();

  return (
    <PageTransition>
      <Header />
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <BackgroundEffects />

        <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="flex justify-center mb-8"
          >
            <TaalMelLogo size="lg" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className={`text-5xl md:text-7xl lg:text-8xl font-heading font-bold mb-6 tracking-tight transition-all duration-700 ${isTech ? "neon-glow" : ""}`}
          >
            <span>Taal</span>
            <span className="font-hindi text-primary">मेल</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-xl md:text-2xl text-muted-foreground mb-12 font-body"
          >
            Optimize. Balance. Experience More.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            onClick={() => navigate("/input")}
          >
            <HeroButton />
          </motion.div>

          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 1.2, delay: 0.8 }}
            className="mt-16 mx-auto h-px w-64 bg-gradient-to-r from-transparent via-primary to-transparent"
          />

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1 }}
            className="mt-8 flex flex-wrap justify-center gap-3"
          >
            {["Conflict Resolution", "Smart Scheduling", "Visual Heatmaps"].map((label) => (
              <span
                key={label}
                className="px-4 py-2 rounded-full text-sm font-body glass neon-border text-muted-foreground"
              >
                {label}
              </span>
            ))}
          </motion.div>
        </div>
      </section>
    </PageTransition>
  );
};

export default Index;
