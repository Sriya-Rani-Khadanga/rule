import React, { createContext, useContext, useState, useCallback, useEffect } from "react";

type ThemeMode = "cultural" | "tech";

interface ThemeContextType {
  mode: ThemeMode;
  toggle: () => void;
  isTransitioning: boolean;
}

const ThemeContext = createContext<ThemeContextType>({
  mode: "cultural",
  toggle: () => {},
  isTransitioning: false,
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>("cultural");
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;

    if (mode === "tech") {
      root.classList.add("tech", "dark");
      body.classList.add("tech", "dark");
    } else {
      root.classList.remove("tech", "dark");
      body.classList.remove("tech", "dark");
    }

    return () => {
      root.classList.remove("tech", "dark");
      body.classList.remove("tech", "dark");
    };
  }, [mode]);

  const toggle = useCallback(() => {
    setIsTransitioning(true);
    setTimeout(() => {
      setMode((prev) => (prev === "cultural" ? "tech" : "cultural"));
    }, 400);
    setTimeout(() => {
      setIsTransitioning(false);
    }, 800);
  }, []);

  return (
    <ThemeContext.Provider value={{ mode, toggle, isTransitioning }}>
      <div className="min-h-screen bg-background text-foreground transition-colors duration-700">
        {children}

        {isTransitioning && (
          <div className="fixed inset-0 z-[9999] pointer-events-none">
            <div
              className="absolute inset-x-0 h-full scanline-active"
              style={{
                background: mode === "cultural"
                  ? "linear-gradient(180deg, transparent 0%, hsl(185 100% 50% / 0.3) 45%, hsl(185 100% 50% / 0.8) 50%, hsl(185 100% 50% / 0.3) 55%, transparent 100%)"
                  : "linear-gradient(180deg, transparent 0%, hsl(36 90% 50% / 0.3) 45%, hsl(36 90% 50% / 0.8) 50%, hsl(36 90% 50% / 0.3) 55%, transparent 100%)",
              }}
            />
          </div>
        )}
      </div>
    </ThemeContext.Provider>
  );
};
