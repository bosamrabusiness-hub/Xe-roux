import { Clipboard } from "lucide-react";
import { Button } from "./ui/button";
import { useToast } from "@/hooks/use-toast";

interface FloatingPasteButtonProps {
  onPaste: (url: string) => void;
}

export const FloatingPasteButton = ({ onPaste }: FloatingPasteButtonProps) => {
  const { toast } = useToast();

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text.trim()) {
        onPaste(text);
        toast({
          title: "Link pasted!",
          description: "Processing video...",
        });
      }
    } catch (err) {
      toast({
        title: "Clipboard access denied",
        description: "Please paste the link manually",
        variant: "destructive",
      });
    }
  };

  return (
    <Button
      onClick={handlePaste}
      size="lg"
      className="fixed bottom-8 right-8 w-14 h-14 rounded-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-glow neon-glow-hover transition-all duration-300 z-40"
    >
      <Clipboard className="h-6 w-6" />
    </Button>
  );
};
