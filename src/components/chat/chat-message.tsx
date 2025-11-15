import { cn } from '@/lib/utils';
import { Bot, User } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export function ChatMessage({ message }: { message: Message }) {
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={cn(
        'flex items-start gap-3',
        !isAssistant && 'flex-row-reverse'
      )}
    >
      <Avatar className="h-8 w-8 border">
        <AvatarFallback className="bg-transparent">
          {isAssistant ? <Bot /> : <User />}
        </AvatarFallback>
      </Avatar>
      <div
        className={cn(
          'max-w-sm rounded-lg px-4 py-2.5 text-sm shadow-sm md:max-w-md',
          isAssistant
            ? 'bg-card text-card-foreground'
            : 'bg-primary text-primary-foreground'
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
