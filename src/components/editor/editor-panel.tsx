'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { type SelectedElement } from '@/app/page';
import { useEffect, useState, useTransition } from 'react';
import { X, LoaderCircle } from 'lucide-react';

type EditorPanelProps = {
  element: SelectedElement | null;
  onClose: () => void;
  onUpdate: (path: number[], instruction: string) => void;
};

export function EditorPanel({ element, onClose, onUpdate }: EditorPanelProps) {
  const [isPending, startTransition] = useTransition();
  const [textContent, setTextContent] = useState('');
  const [classNames, setClassNames] = useState('');

  useEffect(() => {
    if (element) {
      setTextContent(element.textContent);
      setClassNames(element.classNames);
    }
  }, [element]);

  if (!element) return null;

  const handleUpdate = (instruction: string) => {
    startTransition(() => {
      if (element.path) {
        onUpdate(element.path, instruction);
      }
    });
  };

  const isUpdating = isPending;

  return (
    <div className="absolute top-0 right-0 z-10 h-full w-[340px] bg-background/80 p-4 backdrop-blur-sm transition-transform transform-gpu animate-in slide-in-from-right-full duration-300">
      <Card className="h-full shadow-xl flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between p-4">
          <CardTitle className="text-base font-headline">Edit Element</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4 p-4 flex-1 overflow-y-auto">
          <div className="space-y-2">
            <Label htmlFor="tag-name">Tag</Label>
            <Input id="tag-name" value={`<${element.tagName.toLowerCase()}>`} disabled className="font-mono" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="text-content">Text Content</Label>
            <Textarea
              id="text-content"
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              rows={3}
              disabled={isUpdating}
            />
             <Button size="sm" onClick={() => handleUpdate(`Change the text content to: "${textContent}"`)} disabled={isUpdating}>
                {isUpdating ? <LoaderCircle className="animate-spin mr-2" /> : null}
                Update Text
             </Button>
          </div>
          <div className="space-y-2">
            <Label htmlFor="class-names">Tailwind Classes</Label>
            <Textarea
              id="class-names"
              value={classNames}
              onChange={(e) => setClassNames(e.target.value)}
              rows={4}
              disabled={isUpdating}
              className="font-mono"
            />
            <Button size="sm" onClick={() => handleUpdate(`Replace the classes with: "${classNames}"`)} disabled={isUpdating}>
               {isUpdating ? <LoaderCircle className="animate-spin mr-2" /> : null}
               Update Classes
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
