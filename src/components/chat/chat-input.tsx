'use client';

import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, LoaderCircle, Sparkles } from 'lucide-react';

type ChatInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (value: string) => void;
  isLoading: boolean;
  textareaRef?: React.RefObject<HTMLTextAreaElement>;
};

export function ChatInput({ value, onChange, onSubmit, isLoading, textareaRef }: ChatInputProps) {

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || isLoading) return;
    onSubmit(value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(value);
    }
  };


  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 border-t border-white/5 bg-slate-950/95 px-5 py-4"
    >
      <div className="relative w-full">
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the vibe, layout, or interactions you want..."
          className="flex-1 resize-none border-white/10 bg-white/5 pr-12 text-slate-100 placeholder:text-slate-400 focus-visible:ring-emerald-400"
          rows={1}
          disabled={isLoading}
        />
        <Sparkles className="absolute top-1/2 -translate-y-1/2 right-4 h-5 w-5 text-emerald-300/70" />
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <p className="text-[11px] text-slate-400">Press Enter to send. Shift + Enter for a new line.</p>
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <Button type="submit" size="sm" disabled={isLoading || !value.trim()} className="gap-2 rounded-full bg-emerald-500/90 px-4 text-white hover:bg-emerald-400">
          {isLoading ? (
            <LoaderCircle className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          Ship it
        </Button>
      </div>
    </form>
  );
}
