'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { authAPI } from '@/lib/authAPI';
import { ModeToggle } from '@/components/mode-toggle';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const checkAdmin = async () => {
      const adminStatus = await authAPI.isAdmin();
      setIsAdmin(adminStatus);
    };
    checkAdmin();
  }, []);

  const handleLogout = () => {
    authAPI.logout();
    window.location.href = '/login';
  };

  const navItems = [
    { name: 'Tasks', href: '/dashboard' },
    ...(isAdmin ? [{ name: 'Admin Dashboard', href: '/admin' }] : []),
  ];

  return (
    <div className="flex flex-col min-h-screen bg-[#FDFBF7] dark:bg-[#FDFBF7]">
      {/* Mobile Header */}
      <header className="lg:hidden bg-[#4F6F52] text-white p-4 shadow-md">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold">Tropical Tasks</h1>
          <div className="flex items-center space-x-2">
            <ModeToggle />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="text-white hover:bg-[#86A789]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
            </Button>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar - Hidden on mobile unless open */}
        <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#4F6F52] text-white transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:flex lg:flex-col ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}>
          <div className="p-4 border-b border-[#86A789]">
            <h1 className="text-xl font-bold">Tropical Tasks</h1>
          </div>
          <nav className="p-2 flex-1">
            <ul>
              {navItems.map((item) => (
                <li key={item.href} className="mb-1">
                  <Link href={item.href} onClick={() => setIsSidebarOpen(false)}>
                    <Button
                      variant="ghost"
                      className={`w-full justify-start text-white hover:bg-[#86A789] ${
                        pathname === item.href ? 'bg-[#86A789]' : ''
                      }`}
                    >
                      {item.name}
                    </Button>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <div className="p-4 border-t border-[#86A789]">
            <Button
              onClick={handleLogout}
              variant="outline"
              className="w-full text-white border-white hover:bg-[#86A789]"
            >
              Logout
            </Button>
          </div>
        </aside>

        {/* Overlay for mobile */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          ></div>
        )}

        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-6 bg-[#FDFBF7] dark:bg-[#FDFBF7]">
          <div className="hidden lg:block">
            <header className="bg-white dark:bg-[#FDFBF7] shadow-sm p-4 flex justify-between items-center border-b border-[#D2E3C8]">
              <h2 className="text-xl font-semibold text-[#3A3A3A] dark:text-[#3A3A3A]">
                Task Management
              </h2>
              <div className="flex items-center space-x-4">
                <ModeToggle />
                <span className="text-[#3A3A3A] dark:text-[#3A3A3A]">Welcome back!</span>
              </div>
            </header>
          </div>
          <div className="pt-4 lg:pt-0">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}