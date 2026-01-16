import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogTrigger, DialogTitle } from '@/components/ui/dialog';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const TodoChatbot = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you\'d like to do!',
      sender: 'bot',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Check for inappropriate terms before sending to API
      const userInputLower = inputValue.toLowerCase().trim();
      const inappropriateTerms = ['duffer', 'idiot', 'stupid', 'dummy', 'fool', 'moron', 'jerk', 'asshole', 'dumb'];

      if (inappropriateTerms.some(term => userInputLower.includes(term))) {
        // Don't send inappropriate content to API, respond with standard message
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!",
          sender: 'bot',
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, botMessage]);
      } else {
        // Call the backend API to process the message through the AI agent
        const response = await fetch('/api/chatbot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({ message: inputValue }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          sender: 'bot',
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px] max-h-[500px] bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      <div className="p-4 bg-gradient-to-r from-green-500 to-teal-600 text-white">
        <h2 className="text-xl font-bold">AI Todo Assistant</h2>
        <p className="text-sm opacity-90">Ask me to manage your tasks</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-xs sm:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
              }`}
            >
              <p>{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.sender === 'user' ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'
              }`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 max-w-xs px-4 py-2 rounded-lg">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={isLoading || !inputValue.trim()}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

const AIChatbotButton = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="bg-[#4F6F52] hover:bg-[#4F6F52]/90 text-white dark:bg-[#4F6F52] dark:hover:bg-[#4F6F52]/90 w-full"
        >
          AI Todo Assistant
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg max-w-full w-full h-[70vh] flex flex-col">
        <DialogTitle className="sr-only">AI Todo Assistant</DialogTitle>
        <CardContent className="p-0 flex-1 flex flex-col">
          <TodoChatbot />
        </CardContent>
      </DialogContent>
    </Dialog>
  );
};

export default AIChatbotButton;