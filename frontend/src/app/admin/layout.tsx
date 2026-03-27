'use client';

import { useState, useEffect } from 'react';
import { Sidebar } from '@/components/sidebar';
import { ModeToggle } from '@/components/mode-toggle';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Bell, Menu } from 'lucide-react';
import { authAPI } from '@/lib/authAPI';
import { cn } from '@/lib/utils';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isAdmin, setIsAdmin] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [username, setUsername] = useState('User');

  useEffect(() => {
    setIsAdmin(authAPI.isAdmin());
    setUsername(
      localStorage.getItem('username') ||
      localStorage.getItem('email')?.split('@')[0] ||
      'User'
    );
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar isAdmin={true} />

      {/* Main Content Area */}
      <div className={cn('transition-all duration-500 ease-out', 'lg:ml-64')}>
        {/* Top Header */}
        <header className="sticky top-0 z-30 h-16 bg-background/80 backdrop-blur-xl border-b border-white/5 px-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Mobile Menu Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden text-white/60 hover:text-white"
            >
              <Menu className="w-5 h-5" />
            </Button>
          </div>

          <div className="flex items-center gap-3">
            {/* Notifications */}
            <Button
              variant="ghost"
              size="icon"
              className="text-white/60 hover:text-white relative"
            >
              <Bell className="w-5 h-5" strokeWidth={1.5} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[hsl(175,80%,50%)] rounded-full" />
            </Button>

            {/* Theme Toggle */}
            <ModeToggle />

            {/* User Avatar */}
            <div className="flex items-center gap-3 pl-3 border-l border-white/5">
              <div className="hidden sm:flex items-center gap-2">
                <Avatar className="w-8 h-8 ring-2 ring-white/10">
                  <AvatarFallback className="bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] text-white text-sm font-semibold">
                    {username.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <span className="text-sm text-white/80 hidden md:block">{username}</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
