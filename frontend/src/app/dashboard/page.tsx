'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { todoAPI } from '@/lib/todoAPI';
import { Todo } from '@/types/todo';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import FloatingAIButton from '@/components/FloatingAIButton';

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

export default function DashboardPage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [editForm, setEditForm] = useState<{
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
  }>({
    title: '',
    description: '',
    priority: 'medium'
  });

  // Calculate statistics for the dashboard
  const completedCount = todos.filter(todo => todo.status === 'completed').length;
  const pendingCount = todos.filter(todo => todo.status === 'pending').length;
  const totalTasks = todos.length;
  const completedPercentage = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  const chartData = [
    { name: 'Completed', value: completedCount },
    { name: 'Pending', value: pendingCount },
  ];

  const COLORS = ['#55a868', '#4c72b0']; // #55a868 for completed, #4c72b0 for pending

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

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodo.trim()) return;

    try {
      const newTodoItem = await todoAPI.create({
        title: newTodo,
        description: '',
        priority: 'medium',
      });

      setTodos([newTodoItem, ...todos]);
      setNewTodo('');
      toast.success('Task added successfully!');
    } catch (error) {
      console.error('Error adding todo:', error);
      toast.error('Failed to add task');
    }
  };

  const handleToggleTodo = async (id: string) => {
    try {
      const todo = todos.find(t => t.id === id);
      if (!todo) return;

      const newStatus = todo.status === 'completed' ? 'pending' : 'completed';
      const updatedTodo = await todoAPI.update(id, {
        status: newStatus
      });

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
    } catch (error: any) {
      console.error('Error deleting todo:', error);

      // Check if it's a 404 error specifically
      if (error.response?.status === 404) {
        toast.error('Task not found or does not belong to you. It may have been deleted by another session.');
        // Refetch tasks to sync with server
        fetchTodos();
      } else {
        toast.error('Failed to delete task. Please try again.');
      }
    }
  };

  const handleEditClick = (todo: Todo) => {
    // Validate that the task exists before opening the edit dialog
    const taskExists = todos.some(t => t.id === todo.id);
    if (!taskExists) {
      toast.error('Task not found. Please refresh the page.');
      return;
    }

    setEditingTodo(todo);
    setEditForm({
      title: todo.title,
      description: todo.description || '',
      priority: todo.priority || 'medium'
    });
  };

  const handleEditSubmit = async () => {
    if (!editingTodo) return;

    try {
      const updatedTodo = await todoAPI.update(editingTodo.id, {
        title: editForm.title,
        description: editForm.description,
        priority: editForm.priority
      });

      // Update the local state with the updated task
      setTodos(prevTodos => prevTodos.map(todo =>
        todo.id === editingTodo.id ? updatedTodo : todo
      ));

      setEditingTodo(null);
      toast.success('Task updated successfully!');
    } catch (error: any) {
      console.error('Error updating todo:', error);

      // Check if it's a 404 error specifically
      if (error.response?.status === 404) {
        toast.error('Task not found. It may have been deleted by another session.');
        // Close the edit dialog and refetch tasks to sync with server
        setEditingTodo(null);
        fetchTodos(); // Refresh the task list
      } else {
        toast.error('Failed to update task. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600 dark:text-gray-300">Loading tasks...</div>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-6 relative">
      {/* Top Row: Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-[#4F6F52] dark:text-[#4F6F52]">{totalTasks}</div>
            <div className="text-[#3A3A3A] dark:text-[#3A3A3A]">Total Tasks</div>
          </CardContent>
        </Card>
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-[#4F6F52] dark:text-[#4F6F52]">{pendingCount}</div>
            <div className="text-[#3A3A3A] dark:text-[#3A3A3A]">Active Tasks</div>
          </CardContent>
        </Card>
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-[#4F6F52] dark:text-[#4F6F52]">{completedPercentage}%</div>
            <div className="text-[#3A3A3A] dark:text-[#3A3A3A]">Completed</div>
          </CardContent>
        </Card>
      </div>

      {/* Add Task Card */}
      <Card className="bg-[#FDFBF7] border-[#D2E3C8] dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
        <CardHeader>
          <CardTitle className="text-[#4F6F52] dark:text-[#4F6F52]">Add New Task</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAddTodo} className="flex flex-col sm:flex-row gap-2">
            <Input
              value={newTodo}
              onChange={(e) => setNewTodo(e.target.value)}
              placeholder="Enter a new task..."
              className="flex-1 bg-white dark:bg-gray-800 dark:text-white"
            />
            <Button type="submit" className="bg-[#4F6F52] hover:bg-[#4F6F52]/90 dark:bg-[#4F6F52] dark:hover:bg-[#4F6F52]/90">
              Add Task
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Middle Row: Pie Chart and Todo List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart Section */}
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardHeader>
            <CardTitle className="text-[#4F6F52] dark:text-[#4F6F52]">Task Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${percent ? (percent * 100).toFixed(0) : '0'}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
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
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div className="text-center p-3 rounded-lg bg-gray-100 dark:bg-gray-700">
                <div className="text-2xl font-bold text-teal-600 dark:text-teal-400">{completedCount}</div>
                <div className="text-gray-600 dark:text-gray-300">Completed</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-gray-100 dark:bg-gray-700">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{pendingCount}</div>
                <div className="text-gray-600 dark:text-gray-300">Pending</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Todo List Section */}
        <Card className="border-[#D2E3C8] bg-white dark:bg-[#FDFBF7] dark:border-[#D2E3C8]">
          <CardHeader>
            <CardTitle className="text-[#4F6F52] dark:text-[#4F6F52]">Your Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            {todos.length === 0 ? (
              <div className="text-center py-8 text-[#3A3A3A] dark:text-[#3A3A3A]">
                <p>No tasks yet. Add a new task to get started!</p>
              </div>
            ) : (
              <ul className="space-y-3 max-h-[400px] overflow-y-auto">
                {todos.map((todo) => (
                  <li
                    key={todo.id}
                    className={`flex flex-col p-4 rounded-lg border ${
                      todo.status === 'completed'
                        ? 'bg-white border-[#D2E3C8] dark:bg-[#FDFBF7] dark:border-[#D2E3C8]'  // White/cream background with subtle border for completed tasks
                        : 'bg-white border-[#D2E3C8] dark:bg-[#FDFBF7] dark:border-[#D2E3C8]'  // White/cream background with subtle border for pending tasks
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                      <div className="flex items-center space-x-3 flex-1 min-w-0">
                        <Checkbox
                          id={todo.id}
                          checked={todo.status === 'completed'}
                          onCheckedChange={() => handleToggleTodo(todo.id)}
                          className="data-[state=checked]:bg-[#4F6F52] data-[state=checked]:text-white dark:data-[state=checked]:bg-[#4F6F52]"  // Sage Green for checked state
                        />
                        <div className="flex-1 min-w-0">
                          <label
                            htmlFor={todo.id}
                            className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 break-words ${
                              todo.status === 'completed' ? 'line-through text-[#86A789]/50 dark:text-[#86A789]/50' : 'text-[#3A3A3A] dark:text-[#3A3A3A]'  // Completed tasks with strike-through and 50% opacity Soft Moss color
                            }`}
                          >
                            {todo.title}
                          </label>
                          <Badge
                            variant={todo.priority === 'high' ? 'destructive' :
                                   todo.priority === 'medium' ? 'secondary' : 'outline'}
                            className="mt-1 sm:mt-0 ml-0 sm:ml-2 bg-[#86A789] text-white dark:bg-[#86A789] dark:text-white"  // Soft Moss color for badges
                          >
                            {todo.priority ? (todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1)) : "Medium"}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex space-x-2 flex-shrink-0">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditClick(todo)}
                          className="dark:border-teal-600 dark:text-teal-400 text-xs sm:text-sm"
                        >
                          Edit
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteTodo(todo.id)}
                          className="dark:bg-red-700 dark:hover:bg-red-800 text-xs sm:text-sm"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Created: {formatDate(todo.created_at)}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* AI Assistant is now a floating button - see FloatingAIButton component */}
      </div>

      {/* Edit Task Modal */}
      <Dialog open={!!editingTodo} onOpenChange={(open) => !open && setEditingTodo(null)}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-[#4F6F52]">Edit Task</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-foreground">Task Title</Label>
              <Input
                id="title"
                value={editForm.title}
                onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                className="text-white !important placeholder:text-gray-400 !important bg-slate-800 !important border-slate-600 !important"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description" className="text-foreground">Description</Label>
              <Input
                id="description"
                value={editForm.description}
                onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                className="text-white !important placeholder:text-gray-400 !important bg-slate-800 !important border-slate-600 !important"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="priority" className="text-foreground">Priority</Label>
              <Select value={editForm.priority} onValueChange={(value: 'low' | 'medium' | 'high') => setEditForm({...editForm, priority: value})}>
                <SelectTrigger className="text-white !important placeholder:text-gray-400 !important bg-slate-800 !important border-slate-600 !important">
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => setEditingTodo(null)} className="order-2 sm:order-1">
              Cancel
            </Button>
            <Button type="button" className="order-1 sm:order-2 bg-[#4F6F52] hover:bg-[#4F6F52]/90 text-white" onClick={handleEditSubmit}>
              Update Task
            </Button>
          </div>
        </DialogContent>
      </Dialog>
      </div>
      <FloatingAIButton
        onTaskCreated={() => fetchTodos()}
        onDeleteTask={() => fetchTodos()}
        onTaskUpdated={() => fetchTodos()}
      />
    </>
  );
}