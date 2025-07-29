// Enhanced useTodos hook
import { useState, useEffect, useCallback, useRef } from 'react';
import * as todoApi from '../api/todoApi';
import type { TodoList, TodoItem } from '@/types';
import { appEventBus } from '@/lib/eventBus';
import { connectionManager } from '@/lib/connectionManager';

export const useTodos = () => {
  const [lists, setLists] = useState<TodoList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAllLists = useCallback(async () => {
    try {
      setError(null);
      const fetchedLists = await todoApi.fetchLists();
      setLists(fetchedLists);
    } catch (err: any) {
      setError(err.message || 'Failed to load lists.');
      console.error('Error fetching todos:', err);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchAllLists().finally(() => setLoading(false));
  }, [fetchAllLists]);

  const fetchAllListsRef = useRef(fetchAllLists);
  useEffect(() => {
    fetchAllListsRef.current = fetchAllLists;
  }, [fetchAllLists]);

  // Listen for ANY state_change, not just todos
  useEffect(() => {
    const handleStateChange = (data: { resource?: string }) => {
      // Refresh todos for ANY resource change or specifically for todos
      if (!data?.resource || data?.resource === 'todos') {
        fetchAllListsRef.current();
      }
    };

    appEventBus.on('state_change', handleStateChange);

    return () => {
      appEventBus.off('state_change', handleStateChange);
    };
  }, []);

  // Enhanced API call wrapper that FORCES a broadcast
  const performApiCall = async (apiCall: Promise<any>, actionName?: string) => {
    try {
      setError(null);
      setLoading(true);
      
      await apiCall;
      
      // FORCE refresh local data immediately
      await fetchAllLists();
      
      // Send a manual state change broadcast
      // Method 1: Use the connection manager if available
      if (connectionManager && typeof connectionManager.sendMessage === 'function') {
        connectionManager.sendMessage(JSON.stringify({
          type: 'force_state_change',
          resource: 'todos',
          action: actionName,
          timestamp: Date.now()
        }));
      }
      
      // Method 2: Also emit locally to trigger other hooks immediately
      appEventBus.emit('state_change', { resource: 'todos' });
      
      return true;
    } catch (err: any) {
      console.error('API call failed:', actionName, err);
      setError(err.message || 'An operation failed.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Wrapped CRUD functions
  const addList = (title: string) => 
    performApiCall(todoApi.createList(title), 'addList');
    
  const removeList = (listId: number) => 
    performApiCall(todoApi.deleteList(listId), 'removeList');
    
  const editListTitle = (listId: number, newTitle: string) => 
    performApiCall(todoApi.updateListTitle(listId, newTitle), 'editListTitle');
    
  const addItem = (listId: number, title: string) => 
    performApiCall(todoApi.createItem(listId, title), 'addItem');
    
  const removeItem = (listId: number, itemId: number) => 
    performApiCall(todoApi.deleteItem(listId, itemId), 'removeItem');
    
  const toggleItemCompletion = (listId: number, item: TodoItem) => 
    performApiCall(
      todoApi.updateItemCompletion(listId, item.id, !item.completed), 
      'toggleItemCompletion'
    );

  return {
    lists,
    loading,
    error,
    addList,
    removeList,
    editListTitle,
    addItem,
    removeItem,
    toggleItemCompletion
  };
};
// // Step 1: Enhanced useTodos hook - the key fix
// import { useState, useEffect, useCallback, useRef } from 'react';
// import * as todoApi from '../api/todoApi';
// import type { TodoList, TodoItem } from '@/types';
// import { appEventBus } from '@/lib/eventBus';
// import { connectionManager } from '@/lib/connectionManager';

// export const useTodos = () => {
//   const [lists, setLists] = useState<TodoList[]>([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);

//   const fetchAllLists = useCallback(async () => {
//     try {
//       setError(null);
//       const fetchedLists = await todoApi.fetchLists();
//       setLists(fetchedLists);
//       console.log('✅ Todos fetched:', fetchedLists.length, 'lists');
//     } catch (err: any) {
//       setError(err.message || 'Failed to load lists.');
//       console.error('❌ Error fetching todos:', err);
//     }
//   }, []);

//   useEffect(() => {
//     setLoading(true);
//     fetchAllLists().finally(() => setLoading(false));
//   }, [fetchAllLists]);

//   const fetchAllListsRef = useRef(fetchAllLists);
//   useEffect(() => {
//     fetchAllListsRef.current = fetchAllLists;
//   }, [fetchAllLists]);

//   // THE CRITICAL FIX: Listen for ANY state_change, not just todos
//   useEffect(() => {
//     const handleStateChange = (data: { resource?: string }) => {
//       console.log('🔄 State change received:', data);
      
//       // Refresh todos for ANY resource change or specifically for todos
//       if (!data?.resource || data?.resource === 'todos') {
//         console.log('🔄 Refreshing todos due to state change');
//         fetchAllListsRef.current();
//       }
//     };

//     appEventBus.on('state_change', handleStateChange);
//     console.log('👂 Listening for state_change events');

//     return () => {
//       appEventBus.off('state_change', handleStateChange);
//       console.log('👂 Stopped listening for state_change events');
//     };
//   }, []);

//   // Enhanced API call wrapper that FORCES a broadcast
//   const performApiCall = async (apiCall: Promise<any>, actionName?: string) => {
//     try {
//       setError(null);
//       setLoading(true);
      
//       console.log('🚀 Performing API call:', actionName);
//       await apiCall;
      
//       // FORCE refresh local data immediately
//       await fetchAllLists();
      
//       // CRITICAL: Send a manual state change broadcast
//       console.log('📡 Broadcasting state change for todos');
      
//       // Method 1: Use the connection manager if available
//       if (connectionManager && typeof connectionManager.sendMessage === 'function') {
//         connectionManager.sendMessage(JSON.stringify({
//           type: 'force_state_change',
//           resource: 'todos',
//           action: actionName,
//           timestamp: Date.now()
//         }));
//       }
      
//       // Method 2: Also emit locally to trigger other hooks immediately
//       appEventBus.emit('state_change', { resource: 'todos' });
      
//       console.log('✅ API call completed:', actionName);
//       return true;
//     } catch (err: any) {
//       console.error('❌ API call failed:', actionName, err);
//       setError(err.message || 'An operation failed.');
//       return false;
//     } finally {
//       setLoading(false);
//     }
//   };

//   // Wrapped CRUD functions
//   const addList = (title: string) => 
//     performApiCall(todoApi.createList(title), 'addList');
    
//   const removeList = (listId: number) => 
//     performApiCall(todoApi.deleteList(listId), 'removeList');
    
//   const editListTitle = (listId: number, newTitle: string) => 
//     performApiCall(todoApi.updateListTitle(listId, newTitle), 'editListTitle');
    
//   const addItem = (listId: number, title: string) => 
//     performApiCall(todoApi.createItem(listId, title), 'addItem');
    
//   const removeItem = (listId: number, itemId: number) => 
//     performApiCall(todoApi.deleteItem(listId, itemId), 'removeItem');
    
//   const toggleItemCompletion = (listId: number, item: TodoItem) => 
//     performApiCall(
//       todoApi.updateItemCompletion(listId, item.id, !item.completed), 
//       'toggleItemCompletion'
//     );

//   return {
//     lists,
//     loading,
//     error,
//     addList,
//     removeList,
//     editListTitle,
//     addItem,
//     removeItem,
//     toggleItemCompletion
//   };
// };
