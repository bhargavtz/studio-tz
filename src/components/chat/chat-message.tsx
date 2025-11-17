import { cn } from '@/lib/utils';
import { Bot, User, Sparkles } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useEffect, useRef } from 'react';
import Prism from 'prismjs';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-markup';

export type Message = {
  role: 'user' | 'assistant';
  content: string;
  code?: string;
  language?: 'html' | 'css' | 'js';
};

export function ChatMessage({ message }: { message: Message }) {
  const isAssistant = message.role === 'assistant';
  const codeLanguageClass =
    message.language === 'css'
      ? 'language-css'
      : message.language === 'js'
        ? 'language-javascript'
        : 'language-html';

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (message.code && containerRef.current) {
      Prism.highlightAllUnder(containerRef.current);
    }
  }, [message.code, message.language]);

  return (
    <div
      className={cn(
        'flex items-start gap-3',
        !isAssistant && 'justify-end'
      )}
    >
        {isAssistant && (
            <Avatar className="h-8 w-8 border bg-primary text-primary-foreground">
                <AvatarFallback className="bg-transparent">
                    <Sparkles className="h-5 w-5" />
                </AvatarFallback>
            </Avatar>
        )}
      <div
        ref={containerRef}
        className={cn(
          'rounded-lg px-4 py-2.5 text-sm shadow-sm',
          message.code ? 'w-full max-w-full' : 'max-w-md md:max-w-lg',
          isAssistant
            ? 'bg-card text-card-foreground'
            : 'bg-primary text-primary-foreground'
        )}
      >
        {message.code ? (
          <div className="space-y-1">
            {message.content && (
              <p className="text-xs text-muted-foreground">{message.content}</p>
            )}
            <pre className="mt-1 max-h-[28rem] overflow-auto rounded border border-border bg-background px-3 py-2 text-xs font-mono">
              <code className={`whitespace-pre-wrap break-words ${codeLanguageClass}`}>
                {message.code}
              </code>
            </pre>
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{message.content}</p>
        )}
      </div>
        {!isAssistant && (
            <Avatar className="h-8 w-8 border">
                <AvatarFallback className="bg-transparent">
                <User />
                </AvatarFallback>
            </Avatar>
        )}
    </div>
  );
}
