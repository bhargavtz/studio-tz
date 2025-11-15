'use client';

import { Button } from '@/components/ui/button';
import { downloadProject } from '@/lib/zip';
import { Download, Bot } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

type HeaderProps = {
  htmlContent: string;
  cssContent: string;
  jsContent: string;
};

export function Header({ htmlContent, cssContent, jsContent }: HeaderProps) {
  const { toast } = useToast();

  const handleDownload = async () => {
    try {
      await downloadProject(htmlContent, cssContent, jsContent);
      toast({
        title: 'Project Zipped!',
        description: 'Your project has been downloaded.',
      });
    } catch (error) {
      console.error("Failed to download project:", error);
      toast({
        variant: 'destructive',
        title: 'Download Failed',
        description: 'There was an error creating the zip file.',
      });
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex h-16 items-center justify-between border-b bg-background/90 px-4 backdrop-blur-sm md:px-6">
      <div className="flex items-center gap-3">
        <Bot className="h-7 w-7 text-primary" />
        <h1 className="text-xl font-bold font-headline text-foreground">
          WebForgeAI
        </h1>
      </div>
      <Button onClick={handleDownload} variant="outline" className="bg-accent text-accent-foreground hover:bg-accent/90">
        <Download className="mr-2 h-4 w-4" />
        Download Project
      </Button>
    </header>
  );
}
