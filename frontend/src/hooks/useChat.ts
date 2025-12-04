import { useState, useEffect, useCallback } from 'react';
import { Chat, Message } from '@/types/chat';

const STORAGE_KEY = 'rainfall-predictor-chats';

const generateId = () => Math.random().toString(36).substring(2, 15);

const getStoredChats = (): Chat[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const chats = JSON.parse(stored);
      return chats.map((chat: Chat) => ({
        ...chat,
        createdAt: new Date(chat.createdAt),
        updatedAt: new Date(chat.updatedAt),
        messages: chat.messages.map((msg: Message) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
      }));
    }
  } catch (error) {
    console.error('Error loading chats:', error);
  }
  return [];
};

const saveChats = (chats: Chat[]) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
  } catch (error) {
    console.error('Error saving chats:', error);
  }
};

const generateResponse = (userMessage: string): string => {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('rain') || lowerMessage.includes('rainfall')) {
    const responses = [
      "Based on current atmospheric conditions, there's a 65% chance of rainfall in the next 24 hours. The humidity levels are elevated, and a low-pressure system is approaching.",
      "Looking at the latest weather patterns, light to moderate rainfall is expected. Make sure to carry an umbrella!",
      "The precipitation forecast shows scattered showers likely in the afternoon. Cloud cover is increasing from the west.",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }
  
  if (lowerMessage.includes('weather') || lowerMessage.includes('forecast')) {
    return "The current weather analysis shows partly cloudy skies with temperatures around 72°F (22°C). Wind speeds are moderate at 12 mph from the southwest. There's a 40% chance of precipitation later today.";
  }
  
  if (lowerMessage.includes('temperature') || lowerMessage.includes('hot') || lowerMessage.includes('cold')) {
    return "Current temperature readings indicate mild conditions. Expect temperatures to range between 68-78°F (20-26°C) throughout the day. The humidity is at 55%, making it feel comfortable.";
  }
  
  if (lowerMessage.includes('storm') || lowerMessage.includes('thunder')) {
    return "No severe weather alerts at this time. However, there's a developing system that could bring thunderstorms in 48-72 hours. I'll keep monitoring the situation.";
  }
  
  if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
    return "Hello! I'm your Rainfall Predictor assistant. I can help you with weather forecasts, rainfall predictions, and climate insights. What would you like to know about the weather today?";
  }
  
  if (lowerMessage.includes('help')) {
    return "I can help you with:\n• Rainfall predictions and forecasts\n• Current weather conditions\n• Temperature analysis\n• Storm tracking\n• Climate insights\n\nJust ask me any weather-related question!";
  }
  
  return "I'm here to help with weather and rainfall predictions. You can ask me about current conditions, forecasts, rainfall chances, temperature trends, or storm tracking. What would you like to know?";
};

export const useChat = () => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const storedChats = getStoredChats();
    setChats(storedChats);
    if (storedChats.length > 0) {
      setActiveChatId(storedChats[0].id);
    }
  }, []);

  useEffect(() => {
    if (chats.length > 0) {
      saveChats(chats);
    }
  }, [chats]);

  const activeChat = chats.find((chat) => chat.id === activeChatId) || null;

  const createNewChat = useCallback(() => {
    const newChat: Chat = {
      id: generateId(),
      name: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    return newChat.id;
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    let chatId = activeChatId;
    
    if (!chatId) {
      chatId = createNewChat();
    }

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setChats((prev) =>
      prev.map((chat) => {
        if (chat.id === chatId) {
          const isFirstMessage = chat.messages.length === 0;
          return {
            ...chat,
            name: isFirstMessage ? content.slice(0, 30) + (content.length > 30 ? '...' : '') : chat.name,
            messages: [...chat.messages, userMessage],
            updatedAt: new Date(),
          };
        }
        return chat;
      })
    );

    setIsLoading(true);

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 1000));

    const responseContent = generateResponse(content);
    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: responseContent,
      timestamp: new Date(),
    };

    setChats((prev) =>
      prev.map((chat) => {
        if (chat.id === chatId) {
          return {
            ...chat,
            messages: [...chat.messages, assistantMessage],
            updatedAt: new Date(),
          };
        }
        return chat;
      })
    );

    setIsLoading(false);
  }, [activeChatId, createNewChat]);

  const deleteChat = useCallback((chatId: string) => {
    setChats((prev) => {
      const filtered = prev.filter((chat) => chat.id !== chatId);
      if (activeChatId === chatId) {
        setActiveChatId(filtered.length > 0 ? filtered[0].id : null);
      }
      if (filtered.length === 0) {
        localStorage.removeItem(STORAGE_KEY);
      }
      return filtered;
    });
  }, [activeChatId]);

  const clearAllChats = useCallback(() => {
    setChats([]);
    setActiveChatId(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return {
    chats,
    activeChat,
    activeChatId,
    isLoading,
    setActiveChatId,
    createNewChat,
    sendMessage,
    deleteChat,
    clearAllChats,
  };
};
