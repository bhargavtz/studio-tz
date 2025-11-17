'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { type SelectedElement } from '@/app/page';
import { useEffect, useState, useTransition } from 'react';
import { X, LoaderCircle, WrapText, Brush, Ruler, Palette, Type, AlignLeft, AlignCenter, AlignRight, Sparkles } from 'lucide-react';

type EditorPanelProps = {
  element: SelectedElement | null;
  onClose: () => void;
  onUpdate: (path: number[], instruction: string) => void;
};

export function EditorPanel({ element, onClose, onUpdate }: EditorPanelProps) {
  const [isPending, startTransition] = useTransition();
  const [textContent, setTextContent] = useState('');
  const [classNames, setClassNames] = useState('');
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [padding, setPadding] = useState('');
  const [margin, setMargin] = useState('');
  const [bgColor, setBgColor] = useState('#ffffff');
  const [textColor, setTextColor] = useState('#000000');
  const [borderRadius, setBorderRadius] = useState('');
  const [opacity, setOpacity] = useState('100');
  const [fontSize, setFontSize] = useState('');
  const [fontWeight, setFontWeight] = useState('');
  const [lineHeight, setLineHeight] = useState('');
  const [letterSpacing, setLetterSpacing] = useState('');

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

  const handleQuickUpdate = (instruction: string) => {
    if (!instruction.trim()) return;
    handleUpdate(instruction);
  };

  const isUpdating = isPending;

  return (
    <div className="absolute top-0 right-0 z-10 h-full w-[340px] bg-background/80 p-4 backdrop-blur-sm transition-transform transform-gpu animate-in slide-in-from-right-full duration-300">
      <Card className="h-full shadow-xl flex flex-col bg-card/95">
        <CardHeader className="flex flex-row items-center justify-between p-4">
          <CardTitle className="text-base font-headline">Edit Element</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6 p-4 flex-1 overflow-y-auto">
          <div className="space-y-2">
            <Label htmlFor="tag-name" className="text-xs text-muted-foreground">Tag</Label>
            <Input id="tag-name" value={`<${element.tagName.toLowerCase()}>`} disabled className="font-mono text-sm" />
          </div>
          <div className="space-y-3">
            <Label htmlFor="text-content">Text Content</Label>
            <Textarea
              id="text-content"
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              rows={3}
              disabled={isUpdating}
            />
             <Button size="sm" onClick={() => handleUpdate(`Change the text content to: "${textContent}"`)} disabled={isUpdating} className="w-full">
                {isUpdating ? <LoaderCircle className="animate-spin" /> : <WrapText />}
                Update Text
             </Button>
          </div>
          <div className="space-y-3">
            <Label htmlFor="class-names">Tailwind Classes</Label>
            <Textarea
              id="class-names"
              value={classNames}
              onChange={(e) => setClassNames(e.target.value)}
              rows={4}
              disabled={isUpdating}
              className="font-mono text-xs"
            />
            <Button size="sm" onClick={() => handleUpdate(`Replace the classes with: "${classNames}"`)} disabled={isUpdating} className="w-full">
               {isUpdating ? <LoaderCircle className="animate-spin" /> : <Brush />}
               Update Classes
            </Button>
          </div>
          <div className="space-y-3 rounded-lg border border-border/40 p-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              <Ruler className="h-4 w-4" /> Layout
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs text-muted-foreground">Width</Label>
                <Input value={width} onChange={(e) => setWidth(e.target.value)} placeholder="e.g. 320px / w-full" disabled={isUpdating} />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Height</Label>
                <Input value={height} onChange={(e) => setHeight(e.target.value)} placeholder="auto" disabled={isUpdating} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs text-muted-foreground">Padding</Label>
                <Input value={padding} onChange={(e) => setPadding(e.target.value)} placeholder="e.g. px-6 py-3" disabled={isUpdating} />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Margin</Label>
                <Input value={margin} onChange={(e) => setMargin(e.target.value)} placeholder="e.g. mt-8" disabled={isUpdating} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="secondary" size="sm" disabled={!width || isUpdating} onClick={() => handleQuickUpdate(`Set the selected element's width to ${width}.`)}>Apply width</Button>
              <Button variant="secondary" size="sm" disabled={!height || isUpdating} onClick={() => handleQuickUpdate(`Set the selected element's height to ${height}.`)}>Apply height</Button>
              <Button variant="secondary" size="sm" disabled={!padding || isUpdating} onClick={() => handleQuickUpdate(`Update the padding of the selected element to ${padding}.`)}>Apply padding</Button>
              <Button variant="secondary" size="sm" disabled={!margin || isUpdating} onClick={() => handleQuickUpdate(`Update the margin of the selected element to ${margin}.`)}>Apply margin</Button>
            </div>
          </div>

          <div className="space-y-3 rounded-lg border border-border/40 p-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              <Palette className="h-4 w-4" /> Appearance
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs text-muted-foreground">Background</Label>
                <Input type="color" value={bgColor} onChange={(e) => setBgColor(e.target.value)} disabled={isUpdating} className="h-10" />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Text</Label>
                <Input type="color" value={textColor} onChange={(e) => setTextColor(e.target.value)} disabled={isUpdating} className="h-10" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs text-muted-foreground">Border radius</Label>
                <Input value={borderRadius} onChange={(e) => setBorderRadius(e.target.value)} placeholder="e.g. 12px / rounded-xl" disabled={isUpdating} />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Opacity %</Label>
                <Input type="number" min={0} max={100} value={opacity} onChange={(e) => setOpacity(e.target.value)} disabled={isUpdating} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate(`Set the selected element's background color to ${bgColor}.`)}>Background</Button>
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate(`Set the selected element's text color to ${textColor}.`)}>Text color</Button>
              <Button variant="secondary" size="sm" disabled={!borderRadius || isUpdating} onClick={() => handleQuickUpdate(`Apply a border radius of ${borderRadius} to the selected element.`)}>Corner radius</Button>
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate(`Set the opacity of the selected element to ${opacity}%.`)}>Opacity</Button>
            </div>
          </div>

          <div className="space-y-3 rounded-lg border border-border/40 p-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              <Type className="h-4 w-4" /> Typography
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs text-muted-foreground">Font size</Label>
                <Input value={fontSize} onChange={(e) => setFontSize(e.target.value)} placeholder="e.g. 18px / text-lg" disabled={isUpdating} />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Font weight</Label>
                <Input value={fontWeight} onChange={(e) => setFontWeight(e.target.value)} placeholder="e.g. 600 / font-semibold" disabled={isUpdating} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs text-muted-foreground">Line height</Label>
                <Input value={lineHeight} onChange={(e) => setLineHeight(e.target.value)} placeholder="e.g. 1.5 / leading-relaxed" disabled={isUpdating} />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Letter spacing</Label>
                <Input value={letterSpacing} onChange={(e) => setLetterSpacing(e.target.value)} placeholder="e.g. 0.02em / tracking-wide" disabled={isUpdating} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="secondary" size="sm" disabled={!fontSize || isUpdating} onClick={() => handleQuickUpdate(`Set the font size of the selected element to ${fontSize}.`)}>Apply font size</Button>
              <Button variant="secondary" size="sm" disabled={!fontWeight || isUpdating} onClick={() => handleQuickUpdate(`Set the font weight of the selected element to ${fontWeight}.`)}>Apply weight</Button>
              <Button variant="secondary" size="sm" disabled={!lineHeight || isUpdating} onClick={() => handleQuickUpdate(`Update the line height to ${lineHeight}.`)}>Line height</Button>
              <Button variant="secondary" size="sm" disabled={!letterSpacing || isUpdating} onClick={() => handleQuickUpdate(`Update the letter spacing to ${letterSpacing}.`)}>Letter spacing</Button>
            </div>
            <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
              <span>Alignment</span>
              <div className="flex gap-2">
                <Button type="button" variant="ghost" size="icon" disabled={isUpdating} onClick={() => handleQuickUpdate('Align the text/content of the selected element to the left.')}> <AlignLeft className="h-4 w-4" /> </Button>
                <Button type="button" variant="ghost" size="icon" disabled={isUpdating} onClick={() => handleQuickUpdate('Center the text/content of the selected element.')}> <AlignCenter className="h-4 w-4" /> </Button>
                <Button type="button" variant="ghost" size="icon" disabled={isUpdating} onClick={() => handleQuickUpdate('Align the text/content of the selected element to the right.')}> <AlignRight className="h-4 w-4" /> </Button>
              </div>
            </div>
          </div>

          <div className="space-y-2 rounded-lg border border-border/40 p-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              <Sparkles className="h-4 w-4" /> Quick styling
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate('Apply a modern gradient background to the selected element (e.g., from #6366f1 to #ec4899).')}>Gradient bg</Button>
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate('Add a soft drop shadow to the selected element for elevation.')}>Drop shadow</Button>
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate('Add a subtle border (1px) with 20% opacity to define the element.')}>Border</Button>
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate('Apply a glassmorphism effect (transparent background, blur, border) to the selected element.')}>Glass effect</Button>
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate('Make the selected element pill-shaped with generous rounding and balanced padding.')}>Pill shape</Button>
              <Button variant="secondary" size="sm" disabled={isUpdating} onClick={() => handleQuickUpdate('Animate this element with a gentle hover scale and shadow transition.')}>Hover animate</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
