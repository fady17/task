export interface Session {
  id: number;
  title: string;
  created_at: string; // ISO 8601 date string
  updated_at: string; 
}
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

// This matches the response from our Bridge API
export interface ApiResponse {
  role: 'assistant';
  content: string;
}

export interface TodoItem {
  id: number;
  title: string;
  completed: boolean;
  list_id: number;
}

export interface TodoListStats {
  total_items: number;
  completed_items: number;
  percentage_complete: number;
}

export interface TodoList {
  id: number;
  title: string;
  items: TodoItem[];
  stats: TodoListStats;
}