'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  BarChart3,
  ChevronLeft,
  LogOut,
  Settings,
  Leaf
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { authAPI } from '@/lib/authAPI';
import { toast } from 'sonner';

interface SidebarProps {
  isAdmin?: boolean;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

export function Sidebar({ isAdmin = false }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [username, setUsername] = useState('User');
  const [userRole, setUserRole] = useState('Member');
  const pathname = usePathname();

  useEffect(() => {
    setUsername(
      localStorage.getItem('username') ||
      localStorage.getItem('email')?.split('@')[0] ||
      'User'
    );
    setUserRole(authAPI.isAdmin() ? 'Administrator' : 'Member');
  }, []);

  const handleLogout = () => {
    authAPI.logout();
    toast.success('Logged out successfully');
    window.location.href = '/login';
  };

  const navItems: NavItem[] = [
    {
      name: 'Tasks',
      href: '/dashboard',
      icon: LayoutDashboard,
    },
    ...(isAdmin
      ? [
          {
            name: 'Admin',
            href: '/admin',
            icon: BarChart3,
          },
        ]
      : []),
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isExpanded && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsExpanded(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 h-full z-50 transition-all duration-500 ease-out',
          'bg-[hsl(220,20%,8%)]/80 backdrop-blur-xl border-r border-white/5',
          isExpanded ? 'w-64' : 'w-[72px]',
          'hidden lg:flex lg:flex-col'
        )}
      >
        {/* Logo Section */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/5">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] flex items-center justify-center shadow-lg shadow-[hsl(175,80%,50%)]/20">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            {isExpanded && (
              <span className="font-semibold text-white/90 whitespace-nowrap bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
                Tropical Tasks
              </span>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsExpanded(!isExpanded)}
            className="h-8 w-8 text-white/40 hover:text-white hover:bg-white/5 transition-all duration-200"
          >
            <ChevronLeft
              className={cn(
                'w-4 h-4 transition-transform duration-300',
                !isExpanded && 'rotate-180'
              )}
            />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto scrollbar-dark">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link key={item.href} href={item.href}>
                <div
                  className={cn(
                    'group relative flex items-center gap-3 px-3 py-2.5 rounded-lg',
                    'transition-all duration-300 ease-out',
                    'cursor-pointer',
                    isActive
                      ? 'bg-white/5 text-white'
                      : 'text-white/60 hover:text-white hover:bg-white/5'
                  )}
                >
                  {/* Active Indicator - Left Border with Glow */}
                  {isActive && (
                    <>
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-8 rounded-r-full bg-gradient-to-b from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] shadow-[0_0_12px_hsl(175,80%,50%)]" />
                      <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-[hsl(175,80%,50%)]/5 to-[hsl(280,70%,60%)]/5" />
                    </>
                  )}

                  <Icon
                    className={cn(
                      'w-5 h-5 flex-shrink-0 transition-all duration-300',
                      isActive
                        ? 'text-white opacity-100'
                        : 'opacity-60 group-hover:opacity-100'
                    )}
                    strokeWidth={1.5}
                  />

                  {isExpanded && (
                    <span
                      className={cn(
                        'font-medium text-sm transition-all duration-300',
                        isActive ? 'text-white' : 'text-white/80'
                      )}
                    >
                      {item.name}
                    </span>
                  )}

                  {/* Tooltip for collapsed state */}
                  {!isExpanded && (
                    <div className="absolute left-full ml-2 px-2 py-1.5 bg-[hsl(220,20%,12%)] border border-white/10 rounded-md text-white text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 shadow-xl">
                      {item.name}
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Bottom Section */}
        <div className="p-3 border-t border-white/5 space-y-1">
          {/* Settings (Visual Only) */}
          <div
            className={cn(
              'group relative flex items-center gap-3 px-3 py-2.5 rounded-lg',
              'text-white/60 hover:text-white hover:bg-white/5',
              'transition-all duration-300 cursor-pointer'
            )}
          >
            <Settings
              className="w-5 h-5 flex-shrink-0 opacity-60 group-hover:opacity-100 transition-all duration-300"
              strokeWidth={1.5}
            />
            {isExpanded && (
              <span className="font-medium text-sm text-white/80">Settings</span>
            )}
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className={cn(
              'group w-full flex items-center gap-3 px-3 py-2.5 rounded-lg',
              'text-white/60 hover:text-red-400 hover:bg-red-500/10',
              'transition-all duration-300'
            )}
          >
            <LogOut
              className="w-5 h-5 flex-shrink-0 opacity-60 group-hover:opacity-100 transition-all duration-300"
              strokeWidth={1.5}
            />
            {isExpanded && (
              <span className="font-medium text-sm">Log out</span>
            )}
          </button>
        </div>

        {/* User Info */}
        {isExpanded && (
          <div className="p-4 border-t border-white/5">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] flex items-center justify-center shadow-lg">
                <span className="text-white text-sm font-semibold">
                  {username.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {username}
                </p>
                <p className="text-xs text-white/40 truncate">
                  {userRole}
                </p>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Mobile Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 h-full z-50 transition-transform duration-300 lg:hidden',
          'bg-[hsl(220,20%,8%)] border-r border-white/5',
          'w-64',
          isExpanded ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] flex items-center justify-center shadow-lg">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-white">Tropical Tasks</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsExpanded(false)}
            className="h-8 w-8 text-white/40 hover:text-white"
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
        </div>

        <nav className="flex-1 py-6 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link key={item.href} href={item.href}>
                <div
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg',
                    isActive
                      ? 'bg-white/5 text-white'
                      : 'text-white/60 hover:text-white hover:bg-white/5'
                  )}
                >
                  {isActive && (
                    <div className="absolute left-0 w-[3px] h-8 rounded-r-full bg-gradient-to-b from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)]" />
                  )}
                  <Icon className="w-5 h-5" strokeWidth={1.5} />
                  <span className="font-medium text-sm">{item.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-white/5">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut className="w-5 h-5" strokeWidth={1.5} />
            <span className="font-medium text-sm">Log out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
