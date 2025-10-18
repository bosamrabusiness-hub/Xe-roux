import { Layout } from "@/components/Layout";
import { Card } from "@/components/ui/card";
import { Shield, Zap, Heart, Github } from "lucide-react";
import { Button } from "@/components/ui/button";

const About = () => {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        {/* Hero */}
        <div className="text-center space-y-4">
          <div className="w-20 h-20 rounded-2xl bg-primary flex items-center justify-center mx-auto neon-glow">
            <span className="text-4xl font-bold text-primary-foreground">X</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            About Xe-roux
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Your trusted companion for downloading videos from across the web
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="glass-effect border-border/50 rounded-2xl p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center mx-auto">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Lightning Fast</h3>
              <p className="text-sm text-muted-foreground">
                Download videos in seconds with optimized processing
              </p>
            </div>
          </Card>

          <Card className="glass-effect border-border/50 rounded-2xl p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center mx-auto">
              <Shield className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Private & Secure</h3>
              <p className="text-sm text-muted-foreground">
                We don't store your videos or track your downloads
              </p>
            </div>
          </Card>

          <Card className="glass-effect border-border/50 rounded-2xl p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center mx-auto">
              <Heart className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Always Free</h3>
              <p className="text-sm text-muted-foreground">
                No subscriptions, no hidden fees, just pure downloading
              </p>
            </div>
          </Card>
        </div>

        {/* About Content */}
        <Card className="glass-effect border-border/50 rounded-2xl p-8 space-y-6">
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">What is Xe-roux?</h2>
            <p className="text-muted-foreground leading-relaxed">
              Xe-roux is a modern, user-friendly video downloader that supports multiple platforms 
              including YouTube, Facebook, TikTok, Instagram, Twitter, and Vimeo. Our mission is 
              to provide a fast, secure, and completely free service for downloading videos in 
              various formats and qualities.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-bold">How to Use</h2>
            <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
              <li>Copy the video URL from your favorite platform</li>
              <li>Paste it into the Xe-roux input field</li>
              <li>Select your preferred format and quality</li>
              <li>Click download and enjoy your video!</li>
            </ol>
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Disclaimer</h2>
            <p className="text-muted-foreground leading-relaxed text-sm">
              Xe-roux is provided for personal use only. Please respect copyright laws and content 
              creators' rights. Do not use this tool to download copyrighted content without 
              permission from the owner. We are not responsible for any misuse of this service.
            </p>
          </div>
        </Card>

        {/* CTA */}
        <div className="text-center space-y-4 pt-4">
          <p className="text-muted-foreground">Want to contribute or report an issue?</p>
          <Button 
            variant="outline" 
            className="rounded-xl"
            asChild
          >
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">
              <Github className="mr-2 h-4 w-4" />
              Visit our GitHub
            </a>
          </Button>
        </div>
      </div>
    </Layout>
  );
};

export default About;
