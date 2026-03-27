'use client';

import { useState, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { todoAPI } from '@/lib/todoAPI';
import { Todo, Tag } from '@/types/todo';
import { AuthGuard } from '@/components/auth-guard';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import {
  Search,
  Plus,
  Calendar,
  Filter,
  Clock,
  CheckCircle2,
  Circle,
  AlertCircle,
  Tag as TagIcon,
  Trash2,
  Edit3,
  ChevronDown,
  TrendingUp,
  Target,
  Award
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { AIChatbot } from '@/components/ai-chatbot';

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

// Helper function to check if due date is overdue
const isOverdue = (dueDate: string) => {
  return new Date(dueDate) < new Date();
};

// Helper function to format due date display
const formatDueDate = (dueDate: string) => {
  const date = new Date(dueDate);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { text: `${Math.abs(diffDays)}d overdue`, overdue: true };
  } else if (diffDays === 0) {
    return { text: 'Due today', overdue: true };
  } else if (diffDays === 1) {
    return { text: 'Due tomorrow', overdue: false };
  } else if (diffDays <= 7) {
    return { text: `Due in ${diffDays}d`, overdue: false };
  } else {
    return { text: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), overdue: false };
  }
};

const PRIORITY_COLORS = {
  low: 'bg-[hsl(190,75%,55%)]',
  medium: 'bg-[hsl(280,70%,60%)]',
  high: 'bg-[hsl(0,70%,55%)]'
};

export default function DashboardPage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  // Form states
  const [newTodo, setNewTodo] = useState({
    title: '',
    description: '',
    priority: 'medium',
    due_date: ''
  });

  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    due_date: ''
  });

  // Calculate statistics
  const stats = useMemo(() => {
    const completedCount = todos.filter(todo => todo.status === 'completed').length;
    const pendingCount = todos.filter(todo => todo.status === 'pending').length;
    const totalTasks = todos.length;
    const completedPercentage = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;
    const overdueCount = todos.filter(todo =>
      todo.status === 'pending' && todo.due_date && isOverdue(todo.due_date)
    ).length;

    return { completedCount, pendingCount, totalTasks, completedPercentage, overdueCount };
  }, [todos]);

  const chartData = [
    { name: 'Completed', value: stats.completedCount },
    { name: 'Pending', value: stats.pendingCount },
  ];

  const COLORS = ['hsl(175, 80%, 50%)', 'hsl(280, 70%, 60%)'];

  // Fetch todos on component mount
  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      const data = await todoAPI.getAll();
      setTodos(data);
    } catch (error) {
      console.error('Error fetching todos:', error);
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  // Filter and search todos
  const filteredTodos = useMemo(() => {
    return todos.filter(todo => {
      const matchesSearch = todo.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        todo.description?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === 'all' || todo.status === statusFilter;
      const matchesPriority = priorityFilter === 'all' || todo.priority === priorityFilter;

      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [todos, searchQuery, statusFilter, priorityFilter]);

  const handleCreateTodo = async () => {
    if (!newTodo.title.trim()) {
      toast.error('Please enter a task title');
      return;
    }

    try {
      const createdTodo = await todoAPI.create({
        title: newTodo.title,
        description: newTodo.description,
        status: 'pending',
        priority: newTodo.priority as 'low' | 'medium' | 'high',
        due_date: newTodo.due_date || undefined
      });

      setTodos([createdTodo, ...todos]);
      setNewTodo({ title: '', description: '', priority: 'medium', due_date: '' });
      setIsCreateDialogOpen(false);
      toast.success('Task created successfully!');
    } catch (error) {
      console.error('Error creating todo:', error);
      toast.error('Failed to create task');
    }
  };

  const handleToggleTodo = async (id: string) => {
    try {
      const todo = todos.find(t => t.id === id);
      if (!todo) return;

      const newStatus = todo.status === 'completed' ? 'pending' : 'completed';
      const updatedTodo = await todoAPI.update(id, { status: newStatus });

      setTodos(todos.map(todo =>
        todo.id === id ? updatedTodo : todo
      ));
      toast.success('Task updated!');
    } catch (error) {
      console.error('Error toggling todo:', error);
      toast.error('Failed to update task');
    }
  };

  const handleDeleteTodo = async (id: string) => {
    try {
      await todoAPI.delete(id);
      setTodos(todos.filter(todo => todo.id !== id));
      toast.success('Task deleted!');
    } catch (error) {
      console.error('Error deleting todo:', error);
      toast.error('Failed to delete task');
    }
  };

  const handleEditSubmit = async () => {
    if (!editingTodo) return;

    try {
      const updatedTodo = await todoAPI.update(editingTodo.id, {
        title: editForm.title,
        description: editForm.description,
        priority: editForm.priority as 'low' | 'medium' | 'high',
        due_date: editForm.due_date || undefined
      });

      setTodos(todos.map(todo =>
        todo.id === editingTodo.id ? updatedTodo : todo
      ));
      setEditingTodo(null);
      toast.success('Task updated successfully!');
    } catch (error) {
      console.error('Error updating todo:', error);
      toast.error('Failed to update task');
    }
  };

  const openEditDialog = (todo: Todo) => {
    setEditingTodo(todo);
    setEditForm({
      title: todo.title,
      description: todo.description || '',
      priority: todo.priority || 'medium',
      due_date: todo.due_date || ''
    });
  };

  if (loading) {
    return (
      <AuthGuard>
        <div className="min-h-screen bg-background scrollbar-dark">
          <div className="flex justify-center items-center h-64">
            <div className="text-lg text-muted-foreground animate-pulse">Loading tasks...</div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-background scrollbar-dark">
        <main className="container mx-auto px-4 py-8 space-y-8">
          {/* Welcome Section */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 animate-fade-in">
            <div>
              <h1 className="text-4xl font-bold gradient-text">My Tasks</h1>
              <p className="text-muted-foreground mt-2">
                Manage your tasks efficiently and boost productivity
              </p>
            </div>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="gradient" className="gap-2 shadow-lg hover:shadow-xl">
                  <Plus className="w-4 h-4" />
                  New Task
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[500px] bg-card border-border">
                <DialogHeader>
                  <DialogTitle className="text-xl font-bold gradient-text">Create New Task</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Task Title *</Label>
                    <Input
                      id="title"
                      value={newTodo.title}
                      onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
                      placeholder="Enter task title..."
                      className="bg-input border-border"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={newTodo.description}
                      onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
                      placeholder="Enter description..."
                      className="bg-input border-border"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="priority">Priority</Label>
                      <Select value={newTodo.priority} onValueChange={(value) => setNewTodo({...newTodo, priority: value})}>
                        <SelectTrigger className="bg-input border-border">
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="due_date">Due Date</Label>
                      <Input
                        id="due_date"
                        type="datetime-local"
                        value={newTodo.due_date}
                        onChange={(e) => setNewTodo({...newTodo, due_date: e.target.value})}
                        className="bg-input border-border"
                      />
                    </div>
                  </div>
                </div>
                <div className="flex justify-end gap-3">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button variant="gradient" onClick={handleCreateTodo}>
                    Create Task
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-[hsl(175,80%,50%)] to-[hsl(280,70%,60%)] shadow-lg">
                    <Target className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-foreground">{stats.totalTasks}</div>
                    <div className="text-sm text-muted-foreground">Total Tasks</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-[hsl(190,75%,55%)] shadow-lg">
                    <Clock className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-[hsl(190,75%,55%)]">{stats.pendingCount}</div>
                    <div className="text-sm text-muted-foreground">Active</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-[hsl(175,80%,50%)] shadow-lg">
                    <CheckCircle2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-[hsl(175,80%,50%)]">{stats.completedPercentage}%</div>
                    <div className="text-sm text-muted-foreground">Completed</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-border bg-card shadow-lg card-lift">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-[hsl(0,70%,55%)] shadow-lg">
                    <AlertCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-[hsl(0,70%,55%)]">{stats.overdueCount}</div>
                    <div className="text-sm text-muted-foreground">Overdue</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Search and Filters */}
          <Card className="border-border bg-card shadow-lg animate-scale-in">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search tasks..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 bg-input border-border"
                  />
                </div>
                <div className="flex gap-2">
                  <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as any)}>
                    <SelectTrigger className="w-[150px] bg-input border-border">
                      <Filter className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={priorityFilter} onValueChange={(v) => setPriorityFilter(v as any)}>
                    <SelectTrigger className="w-[150px] bg-input border-border">
                      <ChevronDown className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Priority</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Task List */}
            <div className="lg:col-span-2">
              <Card className="border-border bg-card shadow-lg animate-scale-in">
                <CardHeader>
                  <CardTitle className="text-foreground flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-[hsl(175,80%,50%)]" />
                    Tasks ({filteredTodos.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {filteredTodos.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-muted-foreground mb-4">
                        {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all'
                          ? 'No tasks match your filters'
                          : 'No tasks yet. Create one to get started!'}
                      </div>
                      {!searchQuery && statusFilter === 'all' && priorityFilter === 'all' && (
                        <Button
                          variant="gradient"
                          onClick={() => setIsCreateDialogOpen(true)}
                          className="mt-4"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Create Task
                        </Button>
                      )}
                    </div>
                  ) : (
                    <ul className="space-y-3 scrollbar-dark max-h-[600px] overflow-y-auto pr-2">
                      {filteredTodos.map((todo) => {
                        const dueDateInfo = todo.due_date ? formatDueDate(todo.due_date) : null;
                        return (
                          <li
                            key={todo.id}
                            className={cn(
                              "flex flex-col p-4 rounded-xl border transition-all duration-300 card-lift",
                              todo.status === 'completed'
                                ? 'bg-muted/50 border-border/50'
                                : 'bg-card border-border hover:border-[hsl(175,80%,50%)]/50'
                            )}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex items-start gap-3 flex-1">
                                <Checkbox
                                  id={todo.id}
                                  checked={todo.status === 'completed'}
                                  onCheckedChange={() => handleToggleTodo(todo.id)}
                                  className={cn(
                                    "mt-1 data-[state=checked]:bg-[hsl(175,80%,50%)] data-[state=checked]:border-[hsl(175,80%,50%)]",
                                    "transition-all duration-200"
                                  )}
                                />
                                <div className="flex-1">
                                  <label
                                    htmlFor={todo.id}
                                    className={cn(
                                      "font-medium cursor-pointer transition-all duration-200",
                                      todo.status === 'completed'
                                        ? 'line-through text-muted-foreground'
                                        : 'text-foreground'
                                    )}
                                  >
                                    {todo.title}
                                  </label>
                                  {todo.description && (
                                    <p className="text-sm text-muted-foreground mt-1">
                                      {todo.description}
                                    </p>
                                  )}
                                  <div className="flex flex-wrap items-center gap-2 mt-2">
                                    <Badge
                                      variant={todo.priority === 'high' ? 'destructive' :
                                             todo.priority === 'medium' ? 'secondary' : 'outline'}
                                      className={cn(
                                        "text-xs transition-all duration-200",
                                        todo.priority === 'high' && 'bg-[hsl(0,70%,55%)] hover:bg-[hsl(0,70%,50%)]',
                                        todo.priority === 'medium' && 'bg-[hsl(280,70%,60%)] hover:bg-[hsl(280,70%,55%)] text-white',
                                        todo.priority === 'low' && 'bg-[hsl(190,75%,55%)] hover:bg-[hsl(190,75%,50%)] text-white'
                                      )}
                                    >
                                      {todo.priority ? todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1) : "Medium"}
                                    </Badge>
                                    {dueDateInfo && (
                                      <Badge
                                        variant="outline"
                                        className={cn(
                                          "text-xs gap-1 transition-all duration-200",
                                          dueDateInfo.overdue 
                                            ? 'border-[hsl(0,70%,55%)] text-[hsl(0,70%,55%)]' 
                                            : 'border-border text-muted-foreground'
                                        )}
                                      >
                                        <Calendar className="w-3 h-3" />
                                        {dueDateInfo.text}
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => openEditDialog(todo)}
                                  className="h-8 w-8 hover:bg-accent transition-colors"
                                >
                                  <Edit3 className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleDeleteTodo(todo.id)}
                                  className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10 transition-colors"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Sidebar - Chart */}
            <div className="space-y-6">
              <Card className="border-border bg-card shadow-lg animate-scale-in">
                <CardHeader>
                  <CardTitle className="text-foreground flex items-center gap-2">
                    <Award className="w-5 h-5 text-[hsl(280,70%,60%)]" />
                    Task Overview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {chartData.map((entry, index) => (
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
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="text-center p-4 rounded-xl bg-[hsl(175,80%,50%)]/10 border border-[hsl(175,80%,50%)]/20">
                      <div className="text-2xl font-bold text-[hsl(175,80%,50%)]">{stats.completedCount}</div>
                      <div className="text-sm text-muted-foreground">Completed</div>
                    </div>
                    <div className="text-center p-4 rounded-xl bg-[hsl(190,75%,55%)]/10 border border-[hsl(190,75%,55%)]/20">
                      <div className="text-2xl font-bold text-[hsl(190,75%,55%)]">{stats.pendingCount}</div>
                      <div className="text-sm text-muted-foreground">Pending</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Stats Card */}
              <Card className="border-border bg-card shadow-lg animate-scale-in" style={{ animationDelay: '0.1s' }}>
                <CardHeader>
                  <CardTitle className="text-foreground">Productivity Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-center py-4">
                    <div className="relative w-32 h-32">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke="hsl(220, 20%, 15%)"
                          strokeWidth="16"
                          fill="none"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke="url(#gradient)"
                          strokeWidth="16"
                          fill="none"
                          strokeDasharray={`${(stats.completedPercentage / 100) * 351.86} 351.86`}
                          strokeLinecap="round"
                          className="transition-all duration-1000 ease-out"
                        />
                        <defs>
                          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="hsl(175, 80%, 50%)" />
                            <stop offset="100%" stopColor="hsl(280, 70%, 60%)" />
                          </linearGradient>
                        </defs>
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-3xl font-bold gradient-text">{stats.completedPercentage}%</span>
                      </div>
                    </div>
                  </div>
                  <p className="text-center text-sm text-muted-foreground">
                    {stats.completedPercentage >= 80 ? '🎉 Excellent!' : stats.completedPercentage >= 50 ? '👍 Good progress!' : '💪 Keep going!'}
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>

        {/* Edit Dialog */}
        <Dialog open={!!editingTodo} onOpenChange={(open) => !open && setEditingTodo(null)}>
          <DialogContent className="sm:max-w-[500px] bg-card border-border">
            <DialogHeader>
              <DialogTitle className="text-xl font-bold gradient-text">Edit Task</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-title">Task Title</Label>
                <Input
                  id="edit-title"
                  value={editForm.title}
                  onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                  className="bg-input border-border"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Input
                  id="edit-description"
                  value={editForm.description}
                  onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                  className="bg-input border-border"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-priority">Priority</Label>
                  <Select value={editForm.priority} onValueChange={(value) => setEditForm({...editForm, priority: value})}>
                    <SelectTrigger className="bg-input border-border">
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-due-date">Due Date</Label>
                  <Input
                    id="edit-due-date"
                    type="datetime-local"
                    value={editForm.due_date}
                    onChange={(e) => setEditForm({...editForm, due_date: e.target.value})}
                    className="bg-input border-border"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setEditingTodo(null)}>
                Cancel
              </Button>
              <Button variant="gradient" onClick={handleEditSubmit}>
                Update Task
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* AI Chatbot */}
        <AIChatbot />
      </div>
    </AuthGuard>
  );
}
