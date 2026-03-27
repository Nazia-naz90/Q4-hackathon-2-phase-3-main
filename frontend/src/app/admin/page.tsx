'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { todoAPI } from '@/lib/todoAPI';
import { AuthGuard } from '@/components/auth-guard';
import { Users, CheckCircle, AlertCircle, BarChart3, TrendingUp, Activity } from 'lucide-react';
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

  useEffect(() => {
    fetchAdminStats();
  }, []);

  const fetchAdminStats = async () => {
    try {
      const data = await todoAPI.getAdminStats();
      setAdminStats(data);
    } catch (error) {
      console.error('Error fetching admin stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AuthGuard requireAdmin>
        <div className="min-h-screen bg-background scrollbar-dark">
          <div className="flex justify-center items-center h-64">
            <div className="text-lg text-muted-foreground animate-pulse">Loading admin data...</div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  if (!adminStats) {
    return (
      <AuthGuard requireAdmin>
        <div className="min-h-screen bg-background scrollbar-dark">
          <div className="flex justify-center items-center h-64">
            <div className="text-lg text-muted-foreground">Failed to load admin data</div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  const statusChartData = [
    { name: 'Completed', value: adminStats.tasks_by_status.completed },
    { name: 'Pending', value: adminStats.tasks_by_status.pending },
  ];

  const priorityChartData = [
    { name: 'Low', value: adminStats.tasks_by_priority.low },
    { name: 'Medium', value: adminStats.tasks_by_priority.medium },
    { name: 'High', value: adminStats.tasks_by_priority.high },
  ];

  const COLORS = ['hsl(175, 80%, 50%)', 'hsl(280, 70%, 60%)'];
  const PRIORITY_COLORS = ['hsl(190, 75%, 55%)', 'hsl(280, 70%, 60%)', 'hsl(0, 70%, 55%)'];

  return (
    <AuthGuard requireAdmin>
      <div className="min-h-screen bg-background scrollbar-dark">
        <main className="container mx-auto px-4 py-8 space-y-8">
          <div className="animate-fade-in">
            <h1 className="text-4xl font-bold gradient-text">Admin Dashboard</h1>
            <p className="text-muted-foreground mt-2">
              Overview of all users and tasks in the system
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-[hsl(280,70%,60%)] to-[hsl(260,75%,65%)] shadow-lg">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-[hsl(280,70%,60%)]">{adminStats.total_users}</div>
                    <div className="text-sm text-muted-foreground">Total Users</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(190,75%,55%)] shadow-lg">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-[hsl(175,80%,50%)]">{adminStats.total_tasks}</div>
                    <div className="text-sm text-muted-foreground">Total Tasks</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-[hsl(175,80%,50%)] shadow-lg">
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-[hsl(175,80%,50%)]">{adminStats.tasks_by_status.completed}</div>
                    <div className="text-sm text-muted-foreground">Completed</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-[hsl(280,70%,60%)] shadow-lg">
                    <AlertCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-[hsl(280,70%,60%)]">{adminStats.tasks_by_status.pending}</div>
                    <div className="text-sm text-muted-foreground">Pending</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-scale-in">
            {/* Pie Chart - Task Status */}
            <Card className="border-border bg-card shadow-lg">
              <CardHeader>
                <CardTitle className="text-foreground flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-[hsl(175,80%,50%)]" />
                  Task Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusChartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {statusChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(220, 20%, 12%)', 
                          border: '1px solid hsl(220, 20%, 20%)',
                          borderRadius: '8px',
                          color: 'hsl(220, 15%, 95%)'
                        }} 
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Bar Chart - Task Priority */}
            <Card className="border-border bg-card shadow-lg">
              <CardHeader>
                <CardTitle className="text-foreground flex items-center gap-2">
                  <Activity className="w-5 h-5 text-[hsl(280,70%,60%)]" />
                  Tasks by Priority
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={priorityChartData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 20%, 20%)" />
                      <XAxis dataKey="name" stroke="hsl(220, 15%, 65%)" />
                      <YAxis stroke="hsl(220, 15%, 65%)" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(220, 20%, 12%)', 
                          border: '1px solid hsl(220, 20%, 20%)',
                          borderRadius: '8px',
                          color: 'hsl(220, 15%, 95%)'
                        }} 
                      />
                      <Legend />
                      <Bar dataKey="value" name="Task Count" radius={[8, 8, 0, 0]}>
                        {priorityChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={PRIORITY_COLORS[index % PRIORITY_COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Line Chart - Recent Task Activity */}
            <Card className="border-border bg-card shadow-lg">
              <CardHeader>
                <CardTitle className="text-foreground flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-[hsl(190,75%,55%)]" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={adminStats.recent_task_activity}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 20%, 20%)" />
                      <XAxis dataKey="date" stroke="hsl(220, 15%, 65%)" />
                      <YAxis stroke="hsl(220, 15%, 65%)" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(220, 20%, 12%)', 
                          border: '1px solid hsl(220, 20%, 20%)',
                          borderRadius: '8px',
                          color: 'hsl(220, 15%, 95%)'
                        }} 
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="count"
                        name="Tasks Created"
                        stroke="url(#activityGradient)"
                        strokeWidth={3}
                        activeDot={{ r: 8, fill: 'hsl(175, 80%, 50%)' }}
                      />
                      <defs>
                        <linearGradient id="activityGradient" x1="0" y1="0" x2="1" y2="0">
                          <stop offset="0%" stopColor="hsl(175, 80%, 50%)" />
                          <stop offset="100%" stopColor="hsl(280, 70%, 60%)" />
                        </linearGradient>
                      </defs>
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
