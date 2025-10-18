import { Moon, Sun } from "lucide-react";
import { Button } from "./ui/button";
import { Link, useLocation } from "react-router-dom";

export const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="glass-effect border-b border-border/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center neon-glow-hover transition-all duration-300">
              <span className="text-2xl font-bold text-primary-foreground">X</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Xe-roux
            </span>
          </Link>

          <nav className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              asChild
              className={isActive("/") ? "bg-primary/20 text-primary" : ""}
            >
              <Link to="/">Home</Link>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              asChild
              className={isActive("/history") ? "bg-primary/20 text-primary" : ""}
            >
              <Link to="/history">History</Link>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              asChild
              className={isActive("/about") ? "bg-primary/20 text-primary" : ""}
            >
              <Link to="/about">About</Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="glass-effect border-t border-border/50 mt-auto">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-4">
              <Link to="/about" className="hover:text-primary transition-colors">
                About
              </Link>
              <a href="#" className="hover:text-primary transition-colors">
                Privacy
              </a>
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                GitHub
              </a>
            </div>
            <p>© 2025 Xe-roux. Download responsibly.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};
