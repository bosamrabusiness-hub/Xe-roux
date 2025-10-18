import { useState } from "react";
import { Layout } from "@/components/Layout";
import { PasteBar } from "@/components/PasteBar";
import { VideoPreview } from "@/components/VideoPreview";

const Home = () => {
  const [videoUrl, setVideoUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUrlSubmit = (url: string) => {
    setLoading(true);
    setVideoUrl(url);
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4 pt-8 md:pt-16 animate-fade-in">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent">
            Download Videos Instantly
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Fast, free, and secure video downloads from your favorite platforms
          </p>
        </div>

        {/* Paste Bar */}
        <PasteBar onUrlSubmit={handleUrlSubmit} isLoading={loading} />

        {/* Video Preview */}
        {videoUrl && (
          <VideoPreview
            videoUrl={videoUrl}
            onLoadEnd={() => setLoading(false)}
          />
        )}

      </div>
    </Layout>
  );
};

export default Home;
