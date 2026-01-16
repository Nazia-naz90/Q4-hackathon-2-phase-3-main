'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { authAPI } from '@/lib/authAPI';
import { toast } from 'sonner';

const formSchema = z.object({
  username: z.string().min(2, {
    message: 'Username must be at least 2 characters.',
  }),
  email: z.string().email({
    message: 'Please enter a valid email address.',
  }),
  password: z.string().min(6, {
    message: 'Password must be at least 6 characters.',
  }),
});

export default function SignupPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    try {
      const response = await authAPI.signup(values.email, values.password, values.username);

      toast.success('Account created successfully!');
      router.push('/login');
    } catch (error) {
      console.error('Signup error:', error);
      toast.error('Failed to create account. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FDFBF7] dark:bg-[#FDFBF7] p-4">
      <Card className="w-full max-w-sm sm:max-w-md shadow-lg bg-white border-[#D2E3C8] dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
        <CardHeader className="space-y-1 px-4 sm:px-6 py-6">
          <CardTitle className="text-xl sm:text-2xl font-bold text-center text-[#4F6F52] dark:text-[#4F6F52]">Create Account</CardTitle>
          <CardDescription className="text-center text-sm text-[#3A3A3A] dark:text-[#3A3A3A]">
            Enter your details to create a new account
          </CardDescription>
        </CardHeader>
        <CardContent className="px-4 sm:px-6 pb-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[#3A3A3A] dark:text-[#3A3A3A]">Username</FormLabel>
                    <FormControl>
                      <Input placeholder="johndoe" {...field} className="bg-white border-[#D2E3C8] text-[#3A3A3A] dark:bg-[#FDFBF7] dark:border-[#D2E3C8] dark:text-[#3A3A3A]" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[#3A3A3A] dark:text-[#3A3A3A]">Email</FormLabel>
                    <FormControl>
                      <Input placeholder="john@example.com" type="email" {...field} className="bg-white border-[#D2E3C8] text-[#3A3A3A] dark:bg-[#FDFBF7] dark:border-[#D2E3C8] dark:text-[#3A3A3A]" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[#3A3A3A] dark:text-[#3A3A3A]">Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••" {...field} className="bg-white border-[#D2E3C8] text-[#3A3A3A] dark:bg-[#FDFBF7] dark:border-[#D2E3C8] dark:text-[#3A3A3A]" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full bg-[#4F6F52] hover:bg-[#4F6F52]/90 dark:bg-[#4F6F52] dark:hover:bg-[#4F6F52]/90" disabled={isLoading}>
                {isLoading ? 'Creating Account...' : 'Sign Up'}
              </Button>
            </form>
          </Form>
          <div className="mt-4 text-center text-sm text-[#3A3A3A] dark:text-[#3A3A3A]">
            Already have an account?{' '}
            <a href="/login" className="font-medium text-[#86A789] hover:text-[#86A789]/80 dark:text-[#86A789] dark:hover:text-[#86A789]/80">
              Sign in
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}