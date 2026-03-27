'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Leaf } from 'lucide-react';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background scrollbar-dark">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-[hsl(175,80%,50%)]/10 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-[hsl(280,70%,60%)]/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      <div className="text-center relative z-10">
        <div className="mb-6 inline-flex items-center justify-center">
          <div className="p-4 rounded-2xl bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] shadow-lg animate-pulse-glow">
            <Leaf className="w-12 h-12 text-white" />
          </div>
        </div>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[hsl(175,80%,50%)] mx-auto mb-4"></div>
        <p className="text-muted-foreground text-lg">Redirecting...</p>
      </div>
    </div>
  );
}
