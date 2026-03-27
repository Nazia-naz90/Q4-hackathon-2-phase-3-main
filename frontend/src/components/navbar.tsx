'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ModeToggle } from '@/components/mode-toggle';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { LogOut, User, Settings, BarChart3, LayoutDashboard } from 'lucide-react';
import { authAPI } from '@/lib/authAPI';
import { toast } from 'sonner';

export function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [username, setUsername] = useState<string>('');
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const storedUsername = localStorage.getItem('username') || '';
    const email = localStorage.getItem('email') || '';
    setUsername(storedUsername || email.split('@')[0] || 'User');
    setIsAdmin(authAPI.isAdmin());
  }, []);

  const handleLogout = () => {
    authAPI.logout();
    toast.success('Logged out successfully');
    router.push('/login');
  };

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/50 glass">
      <div className="container flex h-16 items-center justify-between px-4 mx-auto">
        <div className="flex items-center gap-8">
          <a href="/dashboard" className="flex items-center gap-3 group">
            <span className="text-3xl transition-transform group-hover:scale-110">🌴</span>
            <span className="text-xl font-bold gradient-text hidden sm:inline-block">
              Tropical Tasks
            </span>
          </a>
          <div className="hidden md:flex items-center gap-2">
            <Button
              variant={isActive('/dashboard') ? 'secondary' : 'ghost'}
              onClick={() => router.push('/dashboard')}
              className={cn(
                "text-sm transition-all duration-300",
                isActive('/dashboard') && "glow-border"
              )}
            >
              <LayoutDashboard className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
            {isAdmin && (
              <Button
                variant={isActive('/admin') ? 'secondary' : 'ghost'}
                onClick={() => router.push('/admin')}
                className={cn(
                  "text-sm transition-all duration-300",
                  isActive('/admin') && "glow-border"
                )}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                Admin
              </Button>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <ModeToggle />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full ring-2 ring-border/30 hover:ring-primary/50 transition-all duration-300">
                <Avatar className="h-10 w-10">
                  <AvatarImage alt={username} />
                  <AvatarFallback className="bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] text-white font-semibold">
                    {username.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 bg-card border-border" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none text-foreground">{username}</p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {isAdmin ? 'Administrator' : 'User'}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border" />
              <DropdownMenuItem onClick={() => router.push('/dashboard')} className="cursor-pointer">
                <User className="mr-2 h-4 w-4" />
                <span>Dashboard</span>
              </DropdownMenuItem>
              {isAdmin && (
                <DropdownMenuItem onClick={() => router.push('/admin')} className="cursor-pointer">
                  <BarChart3 className="mr-2 h-4 w-4" />
                  <span>Admin Panel</span>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator className="bg-border" />
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-destructive focus:text-destructive">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </nav>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
