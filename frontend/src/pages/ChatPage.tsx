import { useState } from 'react';
import { ChatSidebar } from '@/components/ChatSidebar';
import { ChatArea } from '@/components/ChatArea';
import { useChat } from '@/hooks/useChat';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';

const ChatPage = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const {
    chats,
    activeChat,
    activeChatId,
    isLoading,
    setActiveChatId,
    createNewChat,
    sendMessage,
    deleteChat,
    clearAllChats,
  } = useChat();

  const handleSelectChat = (chatId: string) => {
    setActiveChatId(chatId);
    setSidebarOpen(false);
  };

  const handleNewChat = () => {
    createNewChat();
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen w-full bg-background relative">
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-3 left-3 z-50 md:hidden"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        <Menu className="w-5 h-5" />
      </Button>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed md:relative inset-y-0 left-0 z-40
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        <ChatSidebar
          chats={chats}
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
          onDeleteChat={deleteChat}
          onClearAll={clearAllChats}
        />
      </div>

      {/* Chat Area */}
      <ChatArea
        chat={activeChat}
        isLoading={isLoading}
        onSendMessage={sendMessage}
      />
    </div>
  );
};

export default ChatPage;
