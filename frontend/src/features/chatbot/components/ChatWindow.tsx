import { useEffect, useRef } from 'react';
import type { Message } from '../../../types';
import { ChatMessage } from './ChatMessage';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}
      {isLoading && messages.length > 0 && messages[messages.length-1].role === 'user' && (
        <div className="flex items-start gap-4">
            <div className="animate-pulse rounded-lg bg-muted p-3 text-sm">Thinking...</div>
        </div>
      )}
    </div>
  );
}