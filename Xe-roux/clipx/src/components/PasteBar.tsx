import { useState, useEffect } from "react";
import { Link2, Sparkles, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useToast } from "@/hooks/use-toast";
import { FaYoutube, FaFacebookF, FaTiktok, FaInstagram, FaVimeoV } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";

interface PasteBarProps {
  onUrlSubmit: (url: string) => void;
  isLoading: boolean;
}

export const PasteBar = ({ onUrlSubmit, isLoading }: PasteBarProps) => {
  const [url, setUrl] = useState("");
  const [hasClipboard, setHasClipboard] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    // Check clipboard on mount
    checkClipboard();
  }, []);

  const checkClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text && (text.includes("youtube.com") || text.includes("youtu.be") || 
          text.includes("facebook.com") || text.includes("tiktok.com") ||
          text.includes("instagram.com") || text.includes("twitter.com") || 
          text.includes("vimeo.com"))) {
        setHasClipboard(true);
      }
    } catch (err) {
      // Clipboard access denied or not available
    }
  };

  const handlePasteFromClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setUrl(text);
      setHasClipboard(false);
      toast({
        title: "Link pasted!",
        description: "Ready to download",
      });
    } catch (err) {
      toast({
        title: "Clipboard access denied",
        description: "Please paste the link manually",
        variant: "destructive",
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      let finalUrl = url.trim();
      // If user forgot the scheme (http/https), default to https://
      if (!/^https?:\/\//i.test(finalUrl)) {
        finalUrl = `https://${finalUrl}`;
      }
      onUrlSubmit(finalUrl);
    } else {
      toast({
        title: "Empty link",
        description: "Please enter a valid video URL",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto animate-slide-up">
      <form onSubmit={handleSubmit} className="relative">
        <div className={`glass-effect rounded-2xl p-2 border-2 transition-all duration-300 ${
          hasClipboard ? "neon-glow border-primary animate-pulse-glow" : "border-border/50"
        }`}>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Link2 className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground h-5 w-5" />
              <Input
                type="url"
                placeholder="Paste video or playlist link..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="pl-12 pr-4 h-14 bg-input/50 border-0 focus-visible:ring-2 focus-visible:ring-primary rounded-xl text-base"
              />
            </div>
            
            {hasClipboard && (
              <Button
                type="button"
                onClick={handlePasteFromClipboard}
                size="lg"
                variant="secondary"
                className="px-6 rounded-xl"
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Paste
              </Button>
            )}
            
            <Button
              type="submit"
              size="lg"
              disabled={isLoading}
              className="px-8 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl neon-glow-hover transition-all duration-300 flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Fetching...
                </>
              ) : (
                "Get Video"
              )}
            </Button>


          </div>
        </div>
      </form>
      
      <div className="flex justify-center gap-6 text-muted-foreground text-2xl mt-4">
        {[FaYoutube, FaFacebookF, FaTiktok, FaInstagram, FaXTwitter, FaVimeoV].map((Icon, idx) => (
          <Icon
            key={idx}
            className="cursor-pointer transition-transform duration-300 hover:scale-125 hover:text-primary"
          />
        ))}
      </div>
    </div>
  );
};
