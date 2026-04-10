import { Link, useLocation } from "react-router-dom";
import TaalMelLogo from "@/components/TaalMelLogo";
import ModeToggle from "@/components/ModeToggle";
import { useTheme } from "@/contexts/ThemeContext";

const navItems = [
  { path: "/", label: "Home" },
  { path: "/input", label: "Schedule" },
  { path: "/conflicts", label: "Conflicts" },
  { path: "/results", label: "Results" },
];

const Header = () => {
  const location = useLocation();
  const { mode } = useTheme();
  const isTech = mode === "tech";

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
        <Link to="/">
          <TaalMelLogo size="sm" />
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  px-4 py-2 rounded-full text-sm font-heading transition-all duration-300
                  ${isActive
                    ? "bg-primary text-primary-foreground shadow-glow"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }
                `}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <ModeToggle />
      </div>
    </header>
  );
};

export default Header;
