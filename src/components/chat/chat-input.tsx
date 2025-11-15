'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, LoaderCircle, Sparkles } from 'lucide-react';

type ChatInputProps = {
  onSubmit: (value: string) => void;
  isLoading: boolean;
};

export function ChatInput({ onSubmit, isLoading }: ChatInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    onSubmit(inputValue);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-start gap-3 border-t p-4 bg-card"
    >
      <div className="relative w-full">
        <Textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., 'Create a pricing table...'"
          className="flex-1 resize-none pr-12"
          rows={1}
          disabled={isLoading}
        />
        <Sparkles className="absolute top-1/2 -translate-y-1/2 right-4 h-5 w-5 text-muted-foreground" />
      </div>
      <Button type="submit" size="icon" disabled={isLoading || !inputValue.trim()}>
        {isLoading ? (
          <LoaderCircle className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
        <span className="sr-only">Send</span>
      </Button>
    </form>
  );
}
