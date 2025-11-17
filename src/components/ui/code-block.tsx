'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Check, Clipboard } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import Prism from 'prismjs';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-markup';

type CodeBlockProps = {
  code: string;
  language?: string;
};

export function CodeBlock({ code, language = 'html' }: CodeBlockProps) {
  const [hasCopied, setHasCopied] = useState(false);
  const { toast } = useToast();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    Prism.highlightAllUnder(containerRef.current);
  }, [code, language]);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code).then(() => {
      setHasCopied(true);
      toast({ title: 'Copied to clipboard!' });
      setTimeout(() => setHasCopied(false), 2000);
    }).catch(err => {
        toast({ variant: 'destructive', title: 'Failed to copy', description: 'Could not copy code to clipboard.' });
    });
  };

  return (
    <div ref={containerRef} className="relative w-full rounded-md bg-gray-950 font-code text-sm">
      <div className="absolute top-2 right-2 z-10">
        <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-400 hover:text-white hover:bg-gray-800" onClick={copyToClipboard}>
          {hasCopied ? <Check className="h-4 w-4" /> : <Clipboard className="h-4 w-4" />}
          <span className="sr-only">Copy code</span>
        </Button>
      </div>
      <pre className="max-h-[70vh] w-full overflow-auto p-4 pt-12 rounded-md">
        <code className={`language-${language}`}>
          {code}
        </code>
      </pre>
    </div>
  );
}
