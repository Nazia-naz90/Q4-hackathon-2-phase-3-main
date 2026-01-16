'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
      // If authenticated, redirect to dashboard
      router.push('/dashboard');
    } else {
      // If not authenticated, redirect to login
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FDFBF7] dark:bg-[#FDFBF7] p-4">
      <div className="text-center max-w-sm w-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4F6F52] mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">Redirecting...</p>
      </div>
    </div>
  );
}