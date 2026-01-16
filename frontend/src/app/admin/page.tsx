'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { todoAPI } from '@/lib/todoAPI';
import { isAdmin } from '@/lib/auth-client';
import { Todo } from '@/types/todo';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';

// Helper function to format date
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

interface AdminStats {
  total_users: number;
  total_tasks: number;
  tasks_by_priority: {
    low: number;
    medium: number;
    high: number;
  };
  tasks_by_status: {
    pending: number;
    completed: number;
  };
  recent_task_activity: {
    date: string;
    count: number;
  }[];
}

export default function AdminDashboardPage() {
  const [adminStats, setAdminStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [hasAccess, setHasAccess] = useState<boolean | null>(null);
  const router = useRouter();

  // Check if user has admin access
  useEffect(() => {
    const checkAccess = () => {
      const userIsAdmin = isAdmin();
      if (!userIsAdmin) {
        setHasAccess(false);
        // Redirect to home page or dashboard after a short delay
        setTimeout(() => {
          router.push('/');
        }, 2000);
      } else {
        setHasAccess(true);
        fetchAdminStats();
      }
    };

    checkAccess();
  }, [router]);

  const fetchAdminStats = async () => {
    try {
      const data = await todoAPI.getAdminStats();
      setAdminStats(data);
    } catch (error: any) {
      console.error('Error fetching admin stats:', error);
      // If we get a 403, it means the user lost admin access
      if (error.response?.status === 403) {
        setHasAccess(false);
        router.push('/');
      }
    } finally {
      setLoading(false);
    }
  };

  if (hasAccess === false) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <div className="text-lg text-red-600 dark:text-red-400">Access Denied: Admin privileges required</div>
        <div className="text-sm text-gray-600 dark:text-gray-300">Redirecting to home page...</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600 dark:text-gray-300">Loading admin data...</div>
      </div>
    );
  }

  if (!adminStats) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600 dark:text-gray-300">Failed to load admin data</div>
      </div>
    );
  }

  // Prepare data for charts
  const statusChartData = [
    { name: 'Completed', value: adminStats.tasks_by_status.completed },
    { name: 'Pending', value: adminStats.tasks_by_status.pending },
  ];

  const priorityChartData = [
    { name: 'Low', value: adminStats.tasks_by_priority.low },
    { name: 'Medium', value: adminStats.tasks_by_priority.medium },
    { name: 'High', value: adminStats.tasks_by_priority.high },
  ];

  const COLORS = ['#55a868', '#4c72b0']; // #55a868 for completed, #4c72b0 for pending
  const PRIORITY_COLORS = ['#55a868', '#ff9f40', '#e74c3c']; // Green for low, orange for medium, red for high

  return (
    <div className="space-y-6">
      {/* Top Row: Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardContent className="p-4 text-center">
            <div className="text-2xl sm:text-3xl font-bold text-[#4F6F52] dark:text-[#4F6F52]">{adminStats.total_users}</div>
            <div className="text-sm sm:text-[#3A3A3A] dark:text-[#3A3A3A]">Total Users</div>
          </CardContent>
        </Card>
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardContent className="p-4 text-center">
            <div className="text-2xl sm:text-3xl font-bold text-[#4F6F52] dark:text-[#4F6F52]">{adminStats.total_tasks}</div>
            <div className="text-sm sm:text-[#3A3A3A] dark:text-[#3A3A3A]">Total Tasks</div>
          </CardContent>
        </Card>
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardContent className="p-4 text-center">
            <div className="text-2xl sm:text-3xl font-bold text-[#4F6F52] dark:text-[#4F6F52]">{adminStats.tasks_by_status.completed}</div>
            <div className="text-sm sm:text-[#3A3A3A] dark:text-[#3A3A3A]">Completed Tasks</div>
          </CardContent>
        </Card>
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardContent className="p-4 text-center">
            <div className="text-2xl sm:text-3xl font-bold text-[#4F6F52] dark:text-[#4F6F52]">{adminStats.tasks_by_status.pending}</div>
            <div className="text-sm sm:text-[#3A3A3A] dark:text-[#3A3A3A]">Pending Tasks</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid - Responsive */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pie Chart - Task Status */}
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8] lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-[#4F6F52] dark:text-[#4F6F52] text-base sm:text-lg">Task Status Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${percent ? (percent * 100).toFixed(0) : '0'}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [value, 'Tasks']}
                    labelFormatter={(name) => `${name} Tasks`}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      borderColor: 'hsl(var(--border))',
                      borderRadius: '0.5rem',
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Bar Chart - Task Priority */}
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8] lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-[#4F6F52] dark:text-[#4F6F52] text-base sm:text-lg">Tasks by Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={priorityChartData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      borderColor: 'hsl(var(--border))',
                      borderRadius: '0.5rem',
                    }}
                  />
                  <Legend />
                  <Bar dataKey="value" name="Task Count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Line Chart - Recent Task Activity */}
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8] lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-[#4F6F52] dark:text-[#4F6F52] text-base sm:text-lg">Recent Task Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={adminStats.recent_task_activity}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      borderColor: 'hsl(var(--border))',
                      borderRadius: '0.5rem',
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    name="Tasks Created"
                    stroke="#8884d8"
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}