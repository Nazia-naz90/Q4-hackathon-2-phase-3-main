export interface Todo {
  id: string;
  title: string;
  description?: string;
  status: string; // "pending" or "completed"
  priority?: string; // "low", "medium", or "high"
  due_date?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
  completed_at?: string;
  user_id: string;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  user_id: string;
}