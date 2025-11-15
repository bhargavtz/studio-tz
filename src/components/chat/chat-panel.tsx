'use client';

import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage, type Message } from './chat-message';
import { ChatInput } from './chat-input';
import { useEffect, useRef } from 'react';

type ChatPanelProps = {
  messages: Message[];
  isLoading: boolean;
  onSubmit: (value: string) => void;
};

export function ChatPanel({ messages, isLoading, onSubmit }: ChatPanelProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex h-full flex-col bg-card">
      <ScrollArea className="flex-1" ref={scrollAreaRef}>
        <div className="space-y-6 p-4">
            {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} />
            ))}
             {isLoading && messages[messages.length - 1].role === 'user' && (
              <ChatMessage message={{ role: 'assistant', content: 'Thinking...' }} />
            )}
        </div>
      </ScrollArea>
      <ChatInput onSubmit={onSubmit} isLoading={isLoading} />
    </div>
  );
}
