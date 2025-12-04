import { Plus, MessageSquare, Trash2, CloudRain } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Chat } from '@/types/chat';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface ChatSidebarProps {
  chats: Chat[];
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
  onClearAll: () => void;
}

export const ChatSidebar = ({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  onClearAll,
}: ChatSidebarProps) => {
  return (
    <aside className="w-72 h-full gradient-sidebar border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <a href="/" className="flex items-center gap-2 mb-4 hover:opacity-80 transition-opacity">
          <CloudRain className="w-6 h-6 text-primary" />
          <span className="font-semibold text-foreground">Rainfall Predictor</span>
        </a>
        <Button
          onClick={onNewChat}
          variant="hero"
          className="w-full"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </Button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2">
        {chats.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No chats yet. Start a new conversation!
          </div>
        ) : (
          <div className="space-y-1">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={cn(
                  'group flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-all duration-200',
                  activeChatId === chat.id
                    ? 'bg-accent shadow-soft'
                    : 'hover:bg-accent/50'
                )}
                onClick={() => onSelectChat(chat.id)}
              >
                <MessageSquare className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate text-foreground">
                    {chat.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {format(chat.updatedAt, 'MMM d, h:mm a')}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-all"
                >
                  <Trash2 className="w-4 h-4 text-destructive" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {chats.length > 0 && (
        <div className="p-4 border-t border-border">
          <Button
            onClick={onClearAll}
            variant="ghost"
            size="sm"
            className="w-full text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="w-4 h-4" />
            Clear all chats
          </Button>
        </div>
      )}
    </aside>
  );
};
