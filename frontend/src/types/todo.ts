export interface Todo {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  user_id: string;
}