import { useState, useEffect, useMemo } from "react";
import { Download, Clock, FileVideo, Music, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { useToast } from "@/hooks/use-toast";
// simple slug helper
const slug = (str: string) =>
  str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");

interface VideoPreviewProps {
  videoUrl: string;
  onLoadEnd?: () => void;
}

export const VideoPreview = ({ videoUrl, onLoadEnd }: VideoPreviewProps) => {
  const [formatExt, setFormatExt] = useState<string>("mp4");
  const [quality, setQuality] = useState<string>("");
  const [formats, setFormats] = useState<any[]>([]);
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);
  const { toast } = useToast();

  // NEW: track when preview data has been fully fetched
  const [loaded, setLoaded] = useState(false);

  const [formatId, setFormatId] = useState<string>("mp4");
  // Keep formatId synced with selections
  useEffect(() => {
    const match = formats.find((f) => f.ext === formatExt && f.resolution === quality);
    if (match) {
      setFormatId(match.format_id ?? match.formatId ?? match.id ?? "mp4");
    } else {
      const fallback = formats.find((f) => f.ext === formatExt);
      if (fallback) {
        setFormatId(fallback.format_id ?? fallback.formatId ?? fallback.id ?? formatExt);
      } else {
        setFormatId(formatExt);
      }
    }
  }, [formats, formatExt, quality]);

  // derive quality options for current format and show all qualities available
  const qualityOptions = Array.from(
    new Set(
      formats
        .filter((f) => f.ext === formatExt)
        .map((f) => f.resolution)
    )
  );

  // derive available extra extensions (avoid duplicates with defaults and case differences)
  const defaultExts = ["mp4", "mp3"];
  const extraExts = Array.from(
    new Set(
      formats
        .map((f) => f.ext.toLowerCase())
        .filter((ext) => !defaultExts.includes(ext))
    )
  );

  // Ensure selected quality is valid for current format
  useEffect(() => {
    const qs = formats.filter((f) => f.ext === formatExt).map((f) => f.resolution);
    if (qs.length && !qs.includes(quality)) {
      setQuality(qs[0]);
    }
  }, [formatExt, formats]);

  // Mock video data - in real app, this would come from API
  const [videoData, setVideoData] = useState({
    title: "",
    thumbnail: "",
    duration: "",
  });

  // Format duration once whenever videoData.duration changes
  const formattedDuration = useMemo(() => formatDuration(videoData.duration), [videoData.duration]);
  useEffect(() => {
    if (!videoUrl) return;

    // reset loaded state on every new request
    setLoaded(false);

    const controller = new AbortController();
    const fetchPreview = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/preview`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: videoUrl }),
          signal: controller.signal,
        });
        if (!res.ok) throw new Error("Failed to fetch preview");
        const data = await res.json();
        setVideoData({
          title: data.title || "Unknown title",
          thumbnail: data.thumbnail || data.thumbnail_url || "",
          duration: data.duration || "",
        });
        setFormats(data.formats || []);
        // default selections
        const defaultFormat = data.formats?.[0];
        if (defaultFormat) {
          setFormatExt(defaultFormat.ext);
          setQuality(defaultFormat.resolution);
        }
        // mark loaded only when data successfully fetched
        setLoaded(true);
        onLoadEnd?.();
      } catch (err) {
        console.error(err);
        toast({
          title: "Preview failed",
          description: "Unable to fetch video details.",
          variant: "destructive",
        });
        // keep loaded as false so component remains hidden on error
      } finally {
        // Always notify parent that loading has finished, even on error/abort
        onLoadEnd?.();
      }
    };

   fetchPreview();

   return () => controller.abort();
 }, [videoUrl]);

 const handleDownload = async () => {
   setDownloading(true);
   setProgress(0);

   try {
     // ensure we have a quality selected
     let chosenQuality = quality;
     if (!chosenQuality) {
       const qs = formats.filter((f) => f.ext === formatExt).map((f) => f.resolution);
       if (qs.length) chosenQuality = qs[0];
     }
     // 1. Kick-off download task on backend
     const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
     const enqueueRes = await fetch(`${apiBase}/download`, {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({
         url: videoUrl,
         format: formatId,
         resolution: chosenQuality,
         filename: `${slug(videoData.title || "video")}.${formatExt}`,
       }),
     });

     if (!enqueueRes.ok) throw new Error("Failed to enqueue download");
     const { downloadId } = await enqueueRes.json();

     // 2. Poll status every 2s
     const pollInterval = 2000;
     const intervalId = setInterval(async () => {
       try {
         const statusRes = await fetch(`${apiBase}/download/status/${downloadId}`);
         if (!statusRes.ok) throw new Error("Status error");
         const statusData = await statusRes.json();

         const percent = statusData?.info?.progressPercent ?? 0;
         setProgress(percent);

         // finished?
         const state = statusData?.state || statusData?.info?.status;
         if (state === "finished" || state === "SUCCESS") {
           clearInterval(intervalId);
           setProgress(100);

           // 3. Fetch file
           const fileRes = await fetch(`${apiBase}/download/file/${downloadId}`);
           if (!fileRes.ok) throw new Error("File fetch failed");
           const blob = await fileRes.blob();

           // derive filename from disposition or fallback
           const disposition = fileRes.headers.get("Content-Disposition");
           let filename = "video";
           if (disposition) {
             const match = disposition.match(/filename="?([^";]+)"?/);
             if (match?.[1]) filename = match[1];
           }
           const urlObj = window.URL.createObjectURL(blob);
           const link = document.createElement("a");
           link.href = urlObj;
           link.download = filename;
           document.body.appendChild(link);
           link.click();
           link.remove();
           window.URL.revokeObjectURL(urlObj);

           toast({
             title: "Download Complete! 🎉",
             description: "Your video has been downloaded successfully.",
           });
           setDownloading(false);
         }
       } catch (err) {
         console.error(err);
         // If error happens, stop polling and notify
         clearInterval(intervalId);
         setDownloading(false);
         toast({
           title: "Download failed",
           description: "Unable to download the video. Please try again later.",
           variant: "destructive",
         });
       }
     }, pollInterval);
   } catch (error) {
     console.error(error);
     toast({
       title: "Download failed",
       description: (error as Error).message || "Unable to start download.",
       variant: "destructive",
     });
     setDownloading(false);
   }
 };
  
  // return nothing until preview data is ready
  if (!loaded) return null;

  return (
    <div className="w-full max-w-3xl mx-auto mt-8 animate-slide-up">
      <div className="glass-effect rounded-2xl overflow-hidden shadow-card">
        {/* Thumbnail */}
        <div className="relative aspect-video bg-muted">
          <img
            src={videoData.thumbnail}
            alt={videoData.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute bottom-3 right-3 bg-black/80 backdrop-blur-sm px-2 py-1 rounded-lg flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span className="text-xs font-medium">{formattedDuration}</span>
          </div>
        </div>

       {/* Content */}
       <div className="p-6 space-y-6">
         <div>
           <h3 className="text-xl font-semibold mb-2">{videoData.title}</h3>
           <p className="text-sm text-muted-foreground">Ready to download</p>
         </div>

         {/* Format and Quality Selection */}
         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
           <div className="space-y-2">
             <label className="text-sm font-medium flex items-center gap-2">
               <FileVideo className="h-4 w-4 text-primary" />
               Format
             </label>
             <Select value={formatExt} onValueChange={(val)=>{setFormatExt(val); setQuality("");}}>
               <SelectTrigger className="bg-input/50 border-border/50 rounded-xl">
                 <SelectValue />
               </SelectTrigger>
               <SelectContent>
                 <SelectItem value="mp4">MP4 (Video)</SelectItem>
                 <SelectItem value="mp3">MP3 (Audio)</SelectItem>
                 {extraExts.map((ext) => (
                   <SelectItem key={ext} value={ext}>{ext.toUpperCase()}</SelectItem>
                 ))}
               </SelectContent>
             </Select>
           </div>

           <div className="space-y-2">
             <label className="text-sm font-medium flex items-center gap-2">
               <Music className="h-4 w-4 text-primary" />
               Quality
             </label>
             <Select value={quality} onValueChange={setQuality}>
               <SelectTrigger className="bg-input/50 border-border/50 rounded-xl">
                 <SelectValue />
               </SelectTrigger>
               <SelectContent>
                 {qualityOptions.map((q) => (
                   <SelectItem key={q} value={q}>{q}</SelectItem>
                 ))}
               </SelectContent>
             </Select>
           </div>
         </div>

         {/* Download Button */}
         <div className="space-y-4">
            {/* Progress bar removed – button itself shows loading animation */}
           <Button
             onClick={handleDownload}
             disabled={downloading}
             className={`w-full h-14 text-lg bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl neon-glow-hover transition-all duration-300 ${downloading ? "cursor-wait opacity-80" : ""}`}
           >
             {downloading ? (
               <>
                 <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                 Downloading...
               </>
             ) : (
               <>
                 <Download className="mr-2 h-5 w-5" />
                 Download Now
               </>
             )}
           </Button>
         </div>
       </div>
     </div>
   </div>
 );
};

// ----------------------------------------------------------------
// Helper to format raw duration (seconds or existing hh:mm:ss string)
const formatDuration = (raw: number | string): string => {
  if (raw == null) return "";
  // if already contains ':' assume formatted
  if (typeof raw === "string" && raw.includes(":")) return raw;
  const total = typeof raw === "number" ? raw : parseInt(String(raw));
  if (isNaN(total)) return String(raw);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const seconds = total % 60;
  const pad = (n: number) => n.toString().padStart(2, "0");
  if (hours > 0) {
    return `${hours}:${pad(minutes)}:${pad(seconds)}`;
  }
  return `${minutes}:${pad(seconds)}`;
};
