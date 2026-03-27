'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export function AuthGuard({ children, requireAdmin = false }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');

      // If no token, redirect to login
      if (!token) {
        if (pathname !== '/login' && pathname !== '/signup') {
          router.push('/login');
        } else {
          setIsAuthorized(true);
          setIsLoading(false);
        }
        return;
      }

      // If admin required, check admin status
      if (requireAdmin) {
        const isAdmin = localStorage.getItem('is_admin') === 'true';
        if (!isAdmin) {
          router.push('/dashboard');
          return;
        }
      }

      // Token exists and user is authorized
      setIsAuthorized(true);
      setIsLoading(false);
    };

    // Add timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      checkAuth();
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [router, pathname, requireAdmin]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[hsl(175,80%,50%)] mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthorized) {
    return null;
  }

  return <>{children}</>;
}
