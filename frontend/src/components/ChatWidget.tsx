'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Loader2, Bot, User } from 'lucide-react';
import { useSession } from "@/lib/auth-client";
import { useTasks } from "@/context/TaskContext";

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { data: session } = useSession();
  const { refreshTasks } = useTasks();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !session) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Check for inappropriate terms before sending to API
      const userInputLower = input.toLowerCase().trim();
      const inappropriateTerms = ['duffer', 'idiot', 'stupid', 'dummy', 'fool', 'moron', 'jerk', 'asshole', 'dumb'];

      if (inappropriateTerms.some(term => userInputLower.includes(term))) {
        // Don't send inappropriate content to API, respond with standard message
        const assistantMessage: Message = {
          role: 'assistant',
          content: "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!"
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const response = await fetch('/api/chatbot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.session.token}`
          },
          body: JSON.stringify({ message: input })
        });

        if (!response.ok) {
          throw new Error('Failed to talk to agent');
        }

        const data = await response.json();
        const assistantMessage: Message = { role: 'assistant', content: data.response };
        setMessages(prev => [...prev, assistantMessage]);
        await refreshTasks();
      }
    } catch (error) {
      console.error('Chat Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please make sure the AI Agent is running.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!session) return null; // Hide if not logged in

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`p-4 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-110 active:scale-95 ${
          isOpen 
            ? 'bg-destructive text-destructive-foreground rotate-90' 
            : 'bg-primary text-primary-foreground'
        }`}
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="absolute bottom-20 right-0 w-[350px] sm:w-[400px] h-[550px] bg-card border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-10 fade-in-20 duration-300">
          
          {/* Header */}
          <div className="bg-primary p-4 flex items-center gap-3 shadow-md">
            <div className="bg-primary-foreground/20 p-2 rounded-lg">
                <Bot className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h3 className="font-bold text-primary-foreground text-lg">Todo AI</h3>
              <p className="text-xs text-primary-foreground/80 flex items-center gap-1">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Online & Ready
              </p>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-background/50 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 opacity-70">
                <div className="bg-muted p-4 rounded-full mb-4">
                    <Bot className="w-8 h-8 text-muted-foreground" />
                </div>
                <p className="text-muted-foreground font-medium">Hello {session.user.name}!</p>
                <p className="text-sm text-muted-foreground/80 mt-1">
                  Tell me to create, update, or delete tasks for you.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                    <button 
                        onClick={() => setInput("Add a task to check emails")}
                        className="text-xs bg-muted hover:bg-muted/80 text-muted-foreground px-3 py-2 rounded-full border border-border transition-colors"
                    >
                        "Add a task to check emails"
                    </button>
                    <button 
                         onClick={() => setInput("Show my pending tasks")}
                         className="text-xs bg-muted hover:bg-muted/80 text-muted-foreground px-3 py-2 rounded-full border border-border transition-colors"
                    >
                        "Show my pending tasks"
                    </button>
                </div>
              </div>
            )}
            
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0 mt-1">
                        <Bot className="w-5 h-5 text-muted-foreground" />
                    </div>
                )}
                
                <div
                  className={`max-w-[80%] p-3.5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                    m.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-none'
                      : 'bg-muted text-foreground border border-border rounded-tl-none'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{m.content}</div>
                </div>

                {m.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-1">
                        <User className="w-5 h-5 text-primary" />
                    </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-3 justify-start">
                 <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                    <Bot className="w-5 h-5 text-muted-foreground" />
                </div>
                <div className="bg-muted border border-border p-4 rounded-2xl rounded-tl-none flex items-center gap-2">
                  <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSend} className="p-4 bg-card border-t border-border flex gap-3 items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your command..."
              disabled={isLoading}
              className="flex-1 bg-muted/50 border border-border text-foreground rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:bg-background transition-all placeholder:text-muted-foreground"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-primary hover:bg-primary/90 text-primary-foreground p-3 rounded-xl disabled:opacity-50 disabled:hover:bg-primary transition-all shadow-lg shadow-primary/20"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}