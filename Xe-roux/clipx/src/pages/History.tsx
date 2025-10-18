import { Layout } from "@/components/Layout";
import { Download, Trash2, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const History = () => {
  // Mock history data
  const downloads = [
    {
      id: 1,
      title: "Amazing Travel Vlog - Beautiful Destinations",
      thumbnail: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400&q=80",
      url: "https://youtube.com/watch?v=example1",
      date: "2024-01-15",
      format: "MP4",
      quality: "1080p",
    },
    {
      id: 2,
      title: "Cooking Tutorial - Easy Recipes",
      thumbnail: "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400&q=80",
      url: "https://youtube.com/watch?v=example2",
      date: "2024-01-14",
      format: "MP4",
      quality: "720p",
    },
    {
      id: 3,
      title: "Music Video - Trending Song",
      thumbnail: "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=400&q=80",
      url: "https://youtube.com/watch?v=example3",
      date: "2024-01-13",
      format: "MP3",
      quality: "320kbps",
    },
  ];

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Download History</h1>
            <p className="text-muted-foreground">Your recent downloads</p>
          </div>
          <Button variant="outline" className="rounded-xl">
            <Trash2 className="mr-2 h-4 w-4" />
            Clear All
          </Button>
        </div>

        <div className="grid gap-4">
          {downloads.map((download) => (
            <Card key={download.id} className="glass-effect border-border/50 rounded-2xl overflow-hidden">
              <div className="flex flex-col md:flex-row gap-4 p-4">
                {/* Thumbnail */}
                <div className="relative w-full md:w-48 aspect-video rounded-xl overflow-hidden flex-shrink-0">
                  <img
                    src={download.thumbnail}
                    alt={download.title}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Content */}
                <div className="flex-1 space-y-3">
                  <div>
                    <h3 className="font-semibold text-lg line-clamp-2">{download.title}</h3>
                    <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(download.date).toLocaleDateString()}
                      </span>
                      <span className="px-2 py-0.5 bg-primary/20 text-primary rounded-lg">
                        {download.format}
                      </span>
                      <span>{download.quality}</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Re-download
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="rounded-xl"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default History;
