
// import { useState, useEffect, useCallback, useMemo, useRef, type ChangeEvent, type FormEvent } from 'react';
// import { appEventBus } from '@/lib/eventBus';
// import type { Message, ConnectionStatus } from '@/types';
// import { connectionManager } from '@/lib/connectionManager';
// import { API_CONFIG } from '@/config';
// import { useSessionContext } from '@/context/SessionContext';

// // Global state to prevent duplicate initialization
// let globalConnectionState: ConnectionStatus = 'disconnected';
// let globalConnectionError: string | null = null;
// let isGloballyInitialized = false;
// const globalStateListeners = new Set<(state: { status: ConnectionStatus; error: string | null }) => void>();

// // Singleton connection manager
// const initializeGlobalConnection = () => {
//   if (isGloballyInitialized) {
//     return;
//   }
  
//   isGloballyInitialized = true;
  
//   const handleStatusChange = (newStatus: string) => {
//     globalConnectionState = newStatus as ConnectionStatus;
    
//     if (newStatus === 'connecting' || newStatus === 'connected') {
//       globalConnectionError = null;
//     }
    
//     if (newStatus === 'error') {
//       globalConnectionError = 'Failed to connect to the server. Please check your internet connection.';
//     }
    
//     globalStateListeners.forEach(listener => {
//       listener({ status: globalConnectionState, error: globalConnectionError });
//     });
//   };
  
//   connectionManager.onStatusChange = handleStatusChange;
//   connectionManager.connect();
// };

// export const useChat = () => {
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [input, setInput] = useState('');
//   const [status, setStatus] = useState<ConnectionStatus>(globalConnectionState);
//   const [connectionError, setConnectionError] = useState<string | null>(globalConnectionError);
  
//   const { currentSessionId, createNewSession } = useSessionContext();
  
//   const messageHandlerRef = useRef<(content: string) => void>(() => {});
  
//   const isLoading = useMemo(() => status !== 'connected', [status]);
//   const isDisabled = useMemo(() => status !== 'connected', [status]);

//   // Subscribe to global connection state
//   useEffect(() => {
//     initializeGlobalConnection();
    
//     const stateListener = (state: { status: ConnectionStatus; error: string | null }) => {
//       setStatus(state.status);
//       setConnectionError(state.error);
//     };
    
//     globalStateListeners.add(stateListener);
//     setStatus(globalConnectionState);
//     setConnectionError(globalConnectionError);
    
//     return () => {
//       globalStateListeners.delete(stateListener);
//     };
//   }, []);

//   // Stable message handler using the event bus
//   useEffect(() => {
//     messageHandlerRef.current = (content: string) => {
//       setMessages(prev => [...prev, { 
//         id: crypto.randomUUID(), 
//         role: 'assistant', 
//         content 
//       }]);
//     };
    
//     const handler = (content: string) => messageHandlerRef.current?.(content);
//     appEventBus.on('chat_message', handler);
    
//     return () => {
//       appEventBus.off('chat_message', handler);
//     };
//   }, []);

//   // Load history when session changes
//   useEffect(() => {
//     let mounted = true;
    
//     const loadHistory = async () => {
//       if (!currentSessionId) {
//         if (mounted) setMessages([]);
//         return;
//       }
      
//       try {
//         const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/${currentSessionId}/messages`);
//         if (!response.ok) throw new Error("Failed to fetch message history");
        
//         const history = await response.json();
//         if (mounted) {
//           setMessages(history.map((m: any) => ({ 
//             ...m, 
//             id: crypto.randomUUID() 
//           })));
//         }
//       } catch (error) {
//         console.error("Error loading chat history:", error);
//       }
//     };
    
//     loadHistory();
    
//     return () => {
//       mounted = false;
//     };
//   }, [currentSessionId]);

//   const handleInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
//     setInput(e.target.value);
//   }, []);

//   const handleSubmit = useCallback(async (e: FormEvent<HTMLFormElement>) => {
//     e.preventDefault();
//     const trimmedInput = input.trim();
//     if (!trimmedInput || status !== 'connected') {
//       return;
//     }

//     let sessionIdToUse = currentSessionId;
//     if (!sessionIdToUse) {
//       const newSession = await createNewSession();
//       if (newSession) {
//         sessionIdToUse = newSession.id;
//       } else {
//         return;
//       }
//     }

//     const userMessage: Message = { 
//       id: crypto.randomUUID(), 
//       role: 'user', 
//       content: trimmedInput 
//     };
    
//     setMessages(prev => [...prev, userMessage]);
    
//     const success = connectionManager.sendMessage(JSON.stringify({ 
//       prompt: trimmedInput, 
//       sessionId: sessionIdToUse 
//     }));
    
//     if (success) {
//       setInput('');
//     }
//   }, [input, status, currentSessionId, createNewSession]);
  
//   const reconnect = useCallback(() => {
//     connectionManager.reconnect();
//   }, []);

//   return { 
//     messages, 
//     input, 
//     status, 
//     isLoading, 
//     isDisabled,
//     connectionError,
//     handleInputChange, 
//     handleSubmit, 
//     reconnect 
//   };
// };
import { useState, useEffect, useCallback, useMemo, useRef, type ChangeEvent, type FormEvent } from 'react';
import { appEventBus } from '@/lib/eventBus';
import type { Message, ConnectionStatus } from '@/types';
import { connectionManager } from '@/lib/connectionManager';
import { API_CONFIG } from '@/config';
import { useSessionContext } from '@/context/SessionContext';

// Global state to prevent duplicate initialization
let globalConnectionState: ConnectionStatus = 'disconnected';
let globalConnectionError: string | null = null;
let isGloballyInitialized = false;
const globalStateListeners = new Set<(state: { status: ConnectionStatus; error: string | null }) => void>();

// Singleton connection manager
const initializeGlobalConnection = () => {
  if (isGloballyInitialized) {
    console.log('🌐 Global connection already initialized');
    return;
  }
  
  console.log('🌐 Initializing global connection...');
  isGloballyInitialized = true;
  
  const handleStatusChange = (newStatus: string) => {
    console.log('🌐 Global status update:', newStatus);
    const prevStatus = globalConnectionState;
    globalConnectionState = newStatus as ConnectionStatus;
    
    // Clear error when connecting or connected
    if (newStatus === 'connecting' || newStatus === 'connected') {
      globalConnectionError = null;
    }
    
    // Set error message for failed connections
    if (newStatus === 'error') {
      globalConnectionError = 'Failed to connect to the server. Please check your internet connection.';
    }
    
    // Notify all listeners
    globalStateListeners.forEach(listener => {
      listener({ status: globalConnectionState, error: globalConnectionError });
    });
    
    console.log('🌐 Notified', globalStateListeners.size, 'listeners of status change from', prevStatus, 'to', newStatus);
  };
  
  connectionManager.onStatusChange = handleStatusChange;
  connectionManager.connect();
};

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState<ConnectionStatus>(globalConnectionState);
  const [connectionError, setConnectionError] = useState<string | null>(globalConnectionError);
  
  // Get session data from the central context.
  const { currentSessionId, createNewSession } = useSessionContext();
  
  // Use refs to avoid recreating objects/functions
  const messageHandlerRef = useRef<(content: string) => void>(() => {});
  const instanceId = useRef(Math.random().toString(36).substr(2, 9));
  
  console.log('🎯 useChat instance', instanceId.current, 'initialized with status:', status);
  
  // Memoize derived state to prevent unnecessary re-renders
  const isLoading = useMemo(() => status !== 'connected', [status]);
  const isDisabled = useMemo(() => status !== 'connected', [status]);

  // Subscribe to global connection state
  useEffect(() => {
    console.log('🎯 useChat instance', instanceId.current, 'subscribing to global state');
    
    // Initialize global connection if needed
    initializeGlobalConnection();
    
    // Subscribe to state changes
    const stateListener = (state: { status: ConnectionStatus; error: string | null }) => {
      console.log('🎯 useChat instance', instanceId.current, 'received state update:', state);
      setStatus(state.status);
      setConnectionError(state.error);
    };
    
    globalStateListeners.add(stateListener);
    
    // Sync initial state
    setStatus(globalConnectionState);
    setConnectionError(globalConnectionError);
    
    return () => {
      console.log('🎯 useChat instance', instanceId.current, 'unsubscribing from global state');
      globalStateListeners.delete(stateListener);
    };
  }, []);

  // Stable message handler
  useEffect(() => {
    messageHandlerRef.current = (content: string) => {
      setMessages(prev => [...prev, { 
        id: crypto.randomUUID(), 
        role: 'assistant', 
        content 
      }]);
    };
    
    const handler = (content: string) => messageHandlerRef.current?.(content);
    appEventBus.on('chat_message', handler);
    
    return () => {
      appEventBus.off('chat_message', handler);
    };
  }, []);

  // Load history when session changes
  useEffect(() => {
    let mounted = true;
    
    const loadHistory = async () => {
      if (!currentSessionId) {
        if (mounted) setMessages([]);
        return;
      }
      
      try {
        const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/${currentSessionId}/messages`);
        if (!response.ok) throw new Error("Failed to fetch message history");
        
        const history = await response.json();
        if (mounted) {
          setMessages(history.map((m: any) => ({ 
            ...m, 
            id: crypto.randomUUID() 
          })));
        }
      } catch (error) {
        console.error("Error loading chat history:", error);
      }
    };
    
    loadHistory();
    
    return () => {
      mounted = false;
    };
  }, [currentSessionId]);

  // Memoized input change handler
  const handleInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  }, []);

  // Memoized submit handler
  const handleSubmit = useCallback(async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmedInput = input.trim();
    if (!trimmedInput || status !== 'connected') {
      console.log('🎯 useChat instance', instanceId.current, 'submit blocked - input:', !!trimmedInput, 'status:', status);
      return;
    }

    let sessionIdToUse = currentSessionId;
    if (!sessionIdToUse) {
      const newSession = await createNewSession();
      if (newSession) {
        sessionIdToUse = newSession.id;
      } else {
        return;
      }
    }

    const userMessage: Message = { 
      id: crypto.randomUUID(), 
      role: 'user', 
      content: trimmedInput 
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    const success = connectionManager.sendMessage(JSON.stringify({ 
      prompt: trimmedInput, 
      sessionId: sessionIdToUse 
    }));
    
    if (success) {
      setInput('');
    } else {
      console.warn('🎯 useChat instance', instanceId.current, 'failed to send message');
    }
  }, [input, status, currentSessionId, createNewSession]);
  
  // Memoized reconnect handler
  const reconnect = useCallback(() => {
    console.log('🎯 useChat instance', instanceId.current, 'manual reconnect triggered');
    connectionManager.reconnect();
  }, []);

  // Debug current state
  useEffect(() => {
    console.log('🎯 useChat instance', instanceId.current, 'state - status:', status, 'isLoading:', isLoading, 'isDisabled:', isDisabled, 'error:', connectionError);
  }, [status, isLoading, isDisabled, connectionError]);

  return { 
    messages, 
    input, 
    status, 
    isLoading, 
    isDisabled,
    connectionError,
    handleInputChange, 
    handleSubmit, 
    reconnect 
  };
};
