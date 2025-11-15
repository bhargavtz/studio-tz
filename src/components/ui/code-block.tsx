'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Check, Clipboard } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

type CodeBlockProps = {
  code: string;
  language?: string;
};

export function CodeBlock({ code, language = 'html' }: CodeBlockProps) {
  const [hasCopied, setHasCopied] = useState(false);
  const { toast } = useToast();

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
    <div className="relative h-full rounded-md bg-gray-900 font-code text-sm">
      <div className="absolute top-2 right-2">
        <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-400 hover:text-white hover:bg-gray-700" onClick={copyToClipboard}>
          {hasCopied ? <Check className="h-4 w-4" /> : <Clipboard className="h-4 w-4" />}
          <span className="sr-only">Copy code</span>
        </Button>
      </div>
      <pre className="h-full w-full overflow-auto p-4 pt-12 rounded-md">
        <code className={`language-${language} text-white`}>
          {code}
        </code>
      </pre>
    </div>
  );
}