'use client';

import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage, type Message } from './chat-message';
import { ChatInput } from './chat-input';
import { useEffect, useMemo, useRef, useState } from 'react';
import { ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

type ChatPanelProps = {
  messages: Message[];
  isLoading: boolean;
  onSubmit: (value: string) => void;
};

export function ChatPanel({ messages, isLoading, onSubmit }: ChatPanelProps) {
  const viewportRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const [draftPrompt, setDraftPrompt] = useState('');
  const [showInspiration, setShowInspiration] = useState(true);

  const quickPrompts = useMemo(
    () => [
      'Create a luxury SaaS hero with neon glow',
      'Design a bold ecommerce launch page',
      'Craft a portfolio with glassmorphism cards',
      'Generate a fintech dashboard with charts',
      'Build a vibrant festival landing page',
      'Make a minimalist pricing section',
    ],
    []
  );

  const handleQuickPrompt = (prompt: string) => {
    if (isLoading) return;
    setDraftPrompt(prompt);
    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  };

  const handleSubmitPrompt = (value: string) => {
    if (!value.trim()) return;
    onSubmit(value);
    setDraftPrompt('');
  };

  useEffect(() => {
    const viewport = viewportRef.current;
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex h-full flex-col bg-slate-950 text-slate-100">
        <div className="relative border-b border-white/5 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4 py-4 shadow-sm">
            <div className="relative z-10 space-y-3">
                <div className="flex items-center gap-2 text-emerald-300">
                  <Sparkles className="h-3.5 w-3.5" />
                  <p className="text-[11px] uppercase tracking-[0.35em]">Next Inai</p>
                </div>
                <div>
                  <h2 className="font-headline text-xl font-semibold">Chat with AI</h2>
                  <p className="text-xs text-slate-300">Describe what you want to build or tweak, and I&apos;ll refresh the preview instantly.</p>
                </div>
                <div className="rounded-xl border border-white/10 bg-slate-900/70 p-3">
                  <div className="flex items-center justify-between text-[11px] text-slate-300">
                    <p className="text-slate-300/90">Need inspiration? Tap a preset below.</p>
                    <button
                      type="button"
                      onClick={() => setShowInspiration((prev) => !prev)}
                      className="flex items-center gap-1 rounded-full border border-white/10 px-2 py-0.5 text-[10px] uppercase tracking-wide text-white/80 hover:border-emerald-300/60"
                    >
                      {showInspiration ? 'Hide' : 'Show'} deck
                      {showInspiration ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                    </button>
                  </div>
                  {showInspiration && (
                    <div className="mt-3 flex max-h-28 flex-wrap gap-1.5 overflow-y-auto pr-1">
                      {quickPrompts.map((prompt) => (
                        <button
                          type="button"
                          key={prompt}
                          onClick={() => handleQuickPrompt(prompt)}
                          disabled={isLoading}
                          className="rounded-full border border-white/10 bg-white/5 px-3 py-0.5 text-[11px] font-medium text-slate-200 backdrop-blur transition hover:border-emerald-300/60 hover:text-white disabled:opacity-50"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
            </div>
            <div className="pointer-events-none absolute inset-y-0 right-0 h-full w-1/2 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.25),_transparent_60%)]" />
        </div>
      <ScrollArea className="flex-1" viewportRef={viewportRef}>
        <div className="space-y-5 px-4 py-5">
            {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} />
            ))}
        </div>
      </ScrollArea>
      <ChatInput
        value={draftPrompt}
        onChange={setDraftPrompt}
        onSubmit={handleSubmitPrompt}
        isLoading={isLoading}
        textareaRef={inputRef}
      />
    </div>
  );
}
