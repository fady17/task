import { API_CONFIG } from '@/config';
import type { TodoList, TodoItem } from '../../../types';

// Use the dynamic base URL from the config
const API_BASE = API_CONFIG.HTTP_ROOT;

// A helper function for making requests to avoid repetition
async function makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown API error occurred.' }));
    throw new Error(errorData.detail);
  }
  if (response.status === 204) {
    return null as T;
  }
  return response.json();
}

// List API Functions
export const fetchLists = () => makeRequest<TodoList[]>('/lists/');
export const createList = (title: string) => makeRequest<TodoList>('/lists/', { method: 'POST', body: JSON.stringify({ title }) });
export const updateListTitle = (listId: number, title: string) => makeRequest<TodoList>(`/lists/${listId}`, { method: 'PUT', body: JSON.stringify({ title }) });
export const deleteList = (listId: number) => makeRequest<void>(`/lists/${listId}`, { method: 'DELETE' });

// Item API Functions - FIXED: Added /lists prefix
export const createItem = (listId: number, title: string) => makeRequest<TodoItem>(`/lists/${listId}/items/`, { method: 'POST', body: JSON.stringify({ title }) });
export const deleteItem = (listId: number, itemId: number) => makeRequest<void>(`/lists/${listId}/items/${itemId}`, { method: 'DELETE' });
export const updateItemCompletion = (listId: number, itemId: number, completed: boolean) => makeRequest<TodoItem>(`/lists/${listId}/items/${itemId}`, { method: 'PUT', body: JSON.stringify({ completed }) });
// import { API_CONFIG } from '@/config'; // <-- Import the new config
// import type { TodoList, TodoItem } from '../../../types';

// // --- THE FIX: Use the dynamic base URL from the config ---
// const API_BASE = API_CONFIG.HTTP_ROOT;

// // A helper function for making requests to avoid repetition
// async function makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
//   // The full URL is now constructed correctly, e.g., https://<host>/api/lists/
//   const response = await fetch(`${API_BASE}${endpoint}`, {
//     headers: { 'Content-Type': 'application/json' },
//     ...options,
//   });
//   if (!response.ok) {
//     const errorData = await response.json().catch(() => ({ detail: 'An unknown API error occurred.' }));
//     throw new Error(errorData.detail);
//   }
//   if (response.status === 204) {
//     return null as T;
//   }
//   return response.json();
// }

// // List API Functions
// export const fetchLists = () => makeRequest<TodoList[]>('/lists/');
// export const createList = (title: string) => makeRequest<TodoList>('/lists/', { method: 'POST', body: JSON.stringify({ title }) });
// export const updateListTitle = (listId: number, title: string) => makeRequest<TodoList>(`/lists/${listId}`, { method: 'PUT', body: JSON.stringify({ title }) });
// export const deleteList = (listId: number) => makeRequest<void>(`/lists/${listId}`, { method: 'DELETE' });

// // Item API Functions
// export const createItem = (listId: number, title: string) => makeRequest<TodoItem>(`/${listId}/items/`, { method: 'POST', body: JSON.stringify({ title }) });
// export const deleteItem = (listId: number, itemId: number) => makeRequest<void>(`/${listId}/items/${itemId}`, { method: 'DELETE' });
// export const updateItemCompletion = (listId: number, itemId: number, completed: boolean) => makeRequest<TodoItem>(`/${listId}/items/${itemId}`, { method: 'PUT', body: JSON.stringify({ completed }) });
// // // import { API_CONFIG } from '@/config';
// // import type { TodoList, TodoItem } from '../../../types';

// // // const API_BASE = 'http://127.0.0.1:8000';
// // // const API_BASE = API_CONFIG.HTTP_ROOT;

// // // A helper function for making requests to avoid repetition
// // async function makeRequest<T>(baseUrl: string,endpoint: string, options: RequestInit = {}): Promise<T> {
// //    const response = await fetch(`${baseUrl}${endpoint}`, {
// //     headers: { 'Content-Type': 'application/json' },
// //     ...options,
// //   });
// //   if (!response.ok) {
// //     const errorData = await response.json().catch(() => ({ detail: 'An unknown API error occurred.' }));
// //     throw new Error(errorData.detail);
// //   }
// //   if (response.status === 204) { // No Content
// //     return null as T;
// //   }
// //   return response.json();
// // }

// // // List API Functions
// // // export const fetchLists = () => makeRequest<TodoList[]>(baseUrl, '/lists/');
// // export const fetchLists = (baseUrl: string) => makeRequest<TodoList[]>(baseUrl, '/lists/');
// // export const createList = (baseUrl: string, title: string) => makeRequest<TodoList>(baseUrl,'/lists/', { method: 'POST', body: JSON.stringify({ title }) });
// // export const updateListTitle = (baseUrl: string, listId: number, title: string) => makeRequest<TodoList>(baseUrl,`/lists/${listId}`, { method: 'PUT', body: JSON.stringify({ title }) });
// // export const deleteList = (baseUrl: string, listId: number) => makeRequest<void>(baseUrl, `/lists/${listId}`, { method: 'DELETE' });

// // // Item API Functions
// // export const createItem = (baseUrl: string, listId: number, title: string) => makeRequest<TodoItem>(baseUrl, `/${listId}/items/`, { method: 'POST', body: JSON.stringify({ title }) });
// // export const deleteItem = (baseUrl: string, listId: number, itemId: number) => makeRequest<void>(baseUrl, `/${listId}/items/${itemId}`, { method: 'DELETE' });
// // export const updateItemCompletion = (baseUrl: string, listId: number, itemId: number, completed: boolean) => makeRequest<TodoItem>(baseUrl, `/${listId}/items/${itemId}`, { method: 'PUT', body: JSON.stringify({ completed }) });