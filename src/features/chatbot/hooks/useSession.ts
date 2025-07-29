import { useState, useEffect, useCallback } from 'react';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import { appEventBus } from '@/lib/eventBus';
import { API_CONFIG } from '@/config';
import type { Session } from '@/types';

const USER_ID = 1;

export const useSession = () => {
  const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSessions = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${USER_ID}`);
      if (!response.ok) throw new Error("Failed to fetch sessions");
      const data: Session[] = await response.json();
      setSessions(data);
      if ((!currentSessionId || !data.some(s => s.id === currentSessionId)) && data.length > 0) {
        setCurrentSessionId(data[0].id);
      } else if (data.length === 0) {
        setCurrentSessionId(null);
      }
    } catch (error) {
      console.error("Error fetching sessions:", error);
    } finally {
      setIsLoading(false);
    }
  }, [currentSessionId, setCurrentSessionId]);

  const createNewSession = useCallback(async () => {
    try {
      const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${USER_ID}`, { method: 'POST' });
      const newSession: Session = await response.json();
      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
      return newSession;
    } catch (error) {
      console.error("Error creating new session:", error);
    }
  }, [setCurrentSessionId]);

  const deleteSession = useCallback(async (sessionIdToDelete: number) => {
    try {
      await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/${sessionIdToDelete}`, { method: 'DELETE' });
      const updatedSessions = sessions.filter(s => s.id !== sessionIdToDelete);
      setSessions(updatedSessions);
      if (currentSessionId === sessionIdToDelete) {
        setCurrentSessionId(updatedSessions[0]?.id || null);
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  }, [sessions, currentSessionId, setCurrentSessionId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  useEffect(() => {
    const handleStateChange = () => fetchSessions();
    appEventBus.on('state_change', handleStateChange);
    return () => appEventBus.off('state_change', handleStateChange);
  }, [fetchSessions]);

  return { sessions, isLoading, currentSessionId, setCurrentSessionId, createNewSession, deleteSession };
};
// import { useState, useEffect, useCallback } from 'react';
// import { useLocalStorage } from '@/hooks/useLocalStorage';
// import { appEventBus } from '@/lib/eventBus';
// import { API_CONFIG } from '@/config';
// import type { Session } from '@/types';

// const USER_ID = 1;

// export const useSession = () => {
//   const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
//   const [sessions, setSessions] = useState<Session[]>([]);
//   const [isLoading, setIsLoading] = useState(true);

//   const fetchSessions = useCallback(async () => {
//     setIsLoading(true);
//     try {
//       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${USER_ID}`);
//       if (!response.ok) throw new Error("Failed to fetch sessions");
//       const data: Session[] = await response.json();
//       setSessions(data);
//       if ((!currentSessionId || !data.some(s => s.id === currentSessionId)) && data.length > 0) {
//         setCurrentSessionId(data[0].id);
//       } else if (data.length === 0) {
//         setCurrentSessionId(null);
//       }
//     } catch (error) {
//       console.error("Error fetching sessions:", error);
//     } finally {
//       setIsLoading(false);
//     }
//   }, [currentSessionId, setCurrentSessionId]);

//   const createNewSession = useCallback(async () => {
//     try {
//       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${USER_ID}`, { method: 'POST' });
//       if (!response.ok) throw new Error("Failed to create new session");
//       const newSession: Session = await response.json();
//       setSessions(prev => [newSession, ...prev]);
//       setCurrentSessionId(newSession.id);
//     } catch (error) {
//       console.error("Error creating new session:", error);
//     }
//   }, [setCurrentSessionId]);

//   const deleteSession = useCallback(async (sessionIdToDelete: number) => {
//     try {
//       await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/${sessionIdToDelete}`, { method: 'DELETE' });
//       const updatedSessions = sessions.filter(s => s.id !== sessionIdToDelete);
//       setSessions(updatedSessions);
//       if (currentSessionId === sessionIdToDelete) {
//         setCurrentSessionId(updatedSessions[0]?.id || null);
//       }
//     } catch (error) {
//       console.error("Error deleting session:", error);
//     }
//   }, [sessions, currentSessionId, setCurrentSessionId]);

//   useEffect(() => {
//     fetchSessions();
//   }, [fetchSessions]);

//   useEffect(() => {
//     const handleStateChange = (data: { resource?: string }) => {
//       if (data?.resource === 'sessions') {
//         fetchSessions();
//       }
//     };
//     appEventBus.on('state_change', handleStateChange);
//     return () => {
//       appEventBus.off('state_change', handleStateChange);
//     };
//   }, [fetchSessions]);

//   return { sessions, isLoading, currentSessionId, setCurrentSessionId, createNewSession, deleteSession };
// };

// // import { useState, useEffect, useCallback } from 'react';
// // import { useLocalStorage } from '@/hooks/useLocalStorage';
// // import { appEventBus } from '@/lib/eventBus';
// // import { API_CONFIG } from '@/config'; // <-- The ONLY necessary change
// // import type { Session } from '@/types';

// // const USER_ID = 1;

// // export const useSession = () => {
// //   const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
// //   const [sessions, setSessions] = useState<Session[]>([]);
// //   const [isLoading, setIsLoading] = useState(true);
// //   const userId = USER_ID;

// //   const fetchSessions = useCallback(async () => {
// //     setIsLoading(true);
// //     try {
// //       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${userId}`);
// //       if (!response.ok) throw new Error("Failed to fetch sessions");
// //       const data: Session[] = await response.json();
// //       setSessions(data);

// //       if ((!currentSessionId || !data.some(s => s.id === currentSessionId)) && data.length > 0) {
// //         setCurrentSessionId(data[0].id);
// //       } else if (data.length === 0) {
// //         setCurrentSessionId(null);
// //       }
// //     } catch (error) {
// //       console.error("Error fetching sessions:", error);
// //       setSessions([]);
// //     } finally {
// //       setIsLoading(false);
// //     }
// //   }, [userId, currentSessionId, setCurrentSessionId]);

// //   const createNewSession = async (): Promise<Session | undefined> => {
// //     try {
// //       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${userId}`, { method: 'POST' });
// //       if (!response.ok) throw new Error("Failed to create new session");
// //       const newSession: Session = await response.json();
// //       setSessions(prev => [newSession, ...prev]);
// //       setCurrentSessionId(newSession.id);
// //       return newSession; // Return the session for auto-start
// //     } catch (error) {
// //       console.error("Error creating new session:", error);
// //       return undefined;
// //     }
// //   };

// //   const deleteSession = async (sessionIdToDelete: number) => {
// //     try {
// //       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/${sessionIdToDelete}`, { method: 'DELETE' });
// //       if (!response.ok) throw new Error("Failed to delete session");
// //       const updatedSessions = sessions.filter(s => s.id !== sessionIdToDelete);
// //       setSessions(updatedSessions);
// //       if (currentSessionId === sessionIdToDelete) {
// //         setCurrentSessionId(updatedSessions[0]?.id || null);
// //       }
// //     } catch (error) {
// //       console.error("Error deleting session:", error);
// //     }
// //   };

// //   useEffect(() => {
// //     fetchSessions();
// //   }, [fetchSessions]);

// //   // This is the working, robust pattern for event listeners in hooks.
// //   useEffect(() => {
// //     const handleStateChange = (data: { resource?: string }) => {
// //       if (data?.resource === 'sessions') {
// //         console.log('[EventBus] Sessions changed, refetching...');
// //         fetchSessions();
// //       }
// //     };
// //     appEventBus.on('state_change', handleStateChange);
// //     return () => {
// //       appEventBus.off('state_change', handleStateChange);
// //     };
// //   }, [fetchSessions]); // The dependency is correct.

// //   return {
// //     userId,
// //     sessions,
// //     isLoading,
// //     currentSessionId,
// //     setCurrentSessionId,
// //     createNewSession,
// //     deleteSession,
// //   };
// // };
// // // import { useState, useEffect, useCallback } from 'react';
// // // import { useLocalStorage } from '@/hooks/useLocalStorage';
// // // import { appEventBus } from '@/lib/eventBus';
// // // import type { AppConfig } from '@/config';
// // // import type { Session } from '@/types';

// // // const USER_ID = 1; // Keeping this simple as per the working logic

// // // export const useSession = (config: AppConfig | null) => { 
// // //   // const config = useConfig();
// // //   const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
// // //   const [sessions, setSessions] = useState<Session[]>([]);
// // //   const [isLoading, setIsLoading] = useState(true);
// // //   const userId = USER_ID;
// // //   // const SESSION_API_URL = `http://${config.api_host}:${config.api_port}/ai/sessions`;
// // //   const SESSION_API_URL = config ? `http://${config.api_host}:${config.api_port}/ai/sessions` : '';



// // //   const fetchSessions = useCallback(async () => {
// // //     setIsLoading(true);
// // //     try {
// // //       // const response = await fetch(`${API_CONFIG.SESSION_API_URL}/user/${userId}`);
// // //       const response = await fetch(`${SESSION_API_URL}/user/${userId}`);
// // //       if (!response.ok) throw new Error("Failed to fetch sessions");
// // //       const data: Session[] = await response.json();
// // //       setSessions(data);

// // //       if ((!currentSessionId || !data.some(s => s.id === currentSessionId)) && data.length > 0) {
// // //         setCurrentSessionId(data[0].id);
// // //       } else if (data.length === 0) {
// // //         setCurrentSessionId(null);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error fetching sessions:", error);
// // //       setSessions([]);
// // //     } finally {
// // //       setIsLoading(false);
// // //     }
// // //   }, [userId, currentSessionId, setCurrentSessionId]);

// // //   const createNewSession = async (): Promise<Session | undefined> => {
// // //     try {
// // //       // const response = await fetch(`${API_CONFIG.SESSION_API_URL}/user/${userId}`, { method: 'POST' });
// // //       const response = await fetch(`${SESSION_API_URL}/user/${userId}`, { method: 'POST' });
// // //       if (!response.ok) throw new Error("Failed to create new session");
// // //       const newSession: Session = await response.json();
      
// // //       setSessions(prev => [newSession, ...prev]);
// // //       setCurrentSessionId(newSession.id);
// // //       return newSession;
// // //     } catch (error) {
// // //       console.error("Error creating new session:", error);
// // //       return undefined;
// // //     }
// // //   };

// // //   const deleteSession = async (sessionIdToDelete: number) => {
// // //     try {
// // //       // const response = await fetch(`${API_CONFIG.SESSION_API_URL}/${sessionIdToDelete}`, { method: 'DELETE' });
// // //        const response = await fetch(`${SESSION_API_URL}/${sessionIdToDelete}`, { method: 'DELETE' });
// // //       if (!response.ok) throw new Error("Failed to delete session");

// // //       const updatedSessions = sessions.filter(s => s.id !== sessionIdToDelete);
// // //       setSessions(updatedSessions);

// // //       if (currentSessionId === sessionIdToDelete) {
// // //         setCurrentSessionId(updatedSessions[0]?.id || null);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error deleting session:", error);
// // //     }
// // //   };

// // //   useEffect(() => {
// // //     fetchSessions();
// // //   }, [fetchSessions]);

// // //   useEffect(() => {
// // //     const handleStateChange = (data: { resource?: string }) => {
// // //       if (data?.resource === 'sessions') {
// // //         fetchSessions();
// // //       }
// // //     };
// // //     appEventBus.on('state_change', handleStateChange);
// // //     return () => {
// // //       appEventBus.off('state_change', handleStateChange);
// // //     };
// // //   }, [fetchSessions]);

// // //   return {
// // //     userId,
// // //     sessions,
// // //     isLoading,
// // //     currentSessionId,
// // //     setCurrentSessionId,
// // //     createNewSession,
// // //     deleteSession,
// // //   };
// // // };
// // // // import { useState, useEffect, useCallback } from 'react';
// // // // import { useLocalStorage } from '@/hooks/useLocalStorage';
// // // // import { appEventBus } from '@/lib/eventBus';
// // // // import { API_CONFIG } from '@/config'; // <-- Import the new config
// // // // import type { Session } from '@/types';
// // // // import { connectionManager } from '@/lib/connectionManager';

// // // // // Hardcoding user ID 1 as per the seed data and original working logic.
// // // // const USER_ID = 1; 
// // // // type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

// // // // export const useSession = () => {
// // // //   const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
// // // //   const [sessions, setSessions] = useState<Session[]>([]);
// // // //   const [isLoading, setIsLoading] = useState(true);
// // // //   const [chatConnectionStatus, setChatConnectionStatus] = useState<ConnectionStatus>('disconnected');
// // // //   const userId = USER_ID;

// // // //   useEffect(() => {
// // // //     // This effect runs only once for the entire application's lifetime.
// // // //     connectionManager.onStatusChange = (newStatus: string) => {
// // // //       setChatConnectionStatus(newStatus as ConnectionStatus);
// // // //     };
// // // //     connectionManager.connect();
    
// // // //     // We don't clean up the connection here, it should persist.
// // // //   }, []); 

// // // //   const fetchSessions = useCallback(async () => {
// // // //     // No need to check for userId, it's a constant.
// // // //     setIsLoading(true);
// // // //     try {
// // // //       // Use the new, correct base URL from the config file.
// // // //       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${userId}`);
// // // //       if (!response.ok) throw new Error("Failed to fetch sessions");
// // // //       const data: Session[] = await response.json();
// // // //       setSessions(data);

// // // //       if ((!currentSessionId || !data.some(s => s.id === currentSessionId)) && data.length > 0) {
// // // //         setCurrentSessionId(data[0].id);
// // // //       } else if (data.length === 0) {
// // // //         setCurrentSessionId(null);
// // // //       }
// // // //     } catch (error) {
// // // //       console.error("Error fetching sessions:", error);
// // // //       setSessions([]);
// // // //     } finally {
// // // //       setIsLoading(false);
// // // //     }
// // // //   }, [userId, currentSessionId, setCurrentSessionId]);

// // // //   const createNewSession = async (): Promise<Session | undefined> => {
// // // //     try {
// // // //       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/user/${userId}`, { method: 'POST' });
// // // //       if (!response.ok) throw new Error("Failed to create new session");
// // // //       const newSession: Session = await response.json();
      
// // // //       setSessions(prev => [newSession, ...prev]);
// // // //       setCurrentSessionId(newSession.id);
// // // //       return newSession; // Return the session for the auto-start feature
// // // //     } catch (error) {
// // // //       console.error("Error creating new session:", error);
// // // //       return undefined;
// // // //     }
// // // //   };

// // // //    const deleteSession = async (sessionIdToDelete: number) => {
// // // //     try {
// // // //       const response = await fetch(`${API_CONFIG.HTTP_ROOT}/ai/sessions/${sessionIdToDelete}`, {
// // // //         method: 'DELETE',
// // // //       });
// // // //       if (!response.ok) throw new Error("Failed to delete session");

// // // //       const updatedSessions = sessions.filter(s => s.id !== sessionIdToDelete);
// // // //       setSessions(updatedSessions);

// // // //       if (currentSessionId === sessionIdToDelete) {
// // // //         setCurrentSessionId(updatedSessions[0]?.id || null);
// // // //       }
// // // //     } catch (error) {
// // // //       console.error("Error deleting session:", error);
// // // //     }
// // // //   };

// // // //   useEffect(() => {
// // // //     fetchSessions();
// // // //   }, [fetchSessions]);

// // // //   useEffect(() => {
// // // //     const handleStateChange = (data: { resource?: string }) => {
// // // //       if (data?.resource === 'sessions') {
// // // //         fetchSessions();
// // // //       }
// // // //     };
// // // //     appEventBus.on('state_change', handleStateChange);
// // // //     return () => {
// // // //       appEventBus.off('state_change', handleStateChange);
// // // //     };
// // // //   }, [fetchSessions]);

// // // //   return {
// // // //     userId,
// // // //     sessions,
// // // //     isLoading,
// // // //     currentSessionId,
// // // //     setCurrentSessionId,
// // // //     createNewSession,
// // // //     deleteSession,
// // // //     chatConnectionStatus, // <-- Expose the status
// // // //     reconnectChat: () => connectionManager.reconnect(),
// // // //   };
// // // // };
// // // // // import { useState, useEffect, useCallback } from 'react';
// // // // // import { useLocalStorage } from '@/hooks/useLocalStorage';
// // // // // import { API_CONFIG } from '@/config';
// // // // // import { appEventBus } from '@/lib/eventBus';
// // // // // import type { Session } from '@/types';

// // // // // const DUMMY_USER_ID = 1;

// // // // // export const useSession = () => {
// // // // //   const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
// // // // //   const [sessions, setSessions] = useState<Session[]>([]);
// // // // //   const [isLoading, setIsLoading] = useState(true);
// // // // //   const userId = DUMMY_USER_ID;

// // // // //   const fetchSessions = useCallback(async () => {
// // // // //     setIsLoading(true);
// // // // //     try {
// // // // //       const response = await fetch(`${API_CONFIG.SESSION_API_URL}/user/${userId}`);
// // // // //       if (!response.ok) throw new Error("Failed to fetch sessions");
// // // // //       const data: Session[] = await response.json();
// // // // //       setSessions(data);

// // // // //       if ((!currentSessionId || !data.some(s => s.id === currentSessionId)) && data.length > 0) {
// // // // //         setCurrentSessionId(data[0].id);
// // // // //       } else if (data.length === 0) {
// // // // //         setCurrentSessionId(null);
// // // // //       }
// // // // //     } catch (error) {
// // // // //       console.error("Error fetching sessions:", error);
// // // // //       setSessions([]);
// // // // //     } finally {
// // // // //       setIsLoading(false);
// // // // //     }
// // // // //   }, [userId, currentSessionId, setCurrentSessionId]);

// // // // //   const createNewSession = async (): Promise<Session | undefined> => {
// // // // //     try {
// // // // //       const response = await fetch(`${API_CONFIG.SESSION_API_URL}/user/${userId}`, { method: 'POST' });
// // // // //       if (!response.ok) throw new Error("Failed to create new session");
// // // // //       const newSession: Session = await response.json();
      
// // // // //       setSessions(prev => [newSession, ...prev]);
// // // // //       setCurrentSessionId(newSession.id);
      
// // // // //       // --- THE ONLY CHANGE IS HERE ---
// // // // //       // Return the newly created session object.
// // // // //       return newSession;
// // // // //     } catch (error) {
// // // // //       console.error("Error creating new session:", error);
// // // // //       return undefined;
// // // // //     }
// // // // //   };

// // // // //   const deleteSession = async (sessionIdToDelete: number) => {
// // // // //     try {
// // // // //       const response = await fetch(`${API_CONFIG.SESSION_API_URL}/${sessionIdToDelete}`, { method: 'DELETE' });
// // // // //       if (!response.ok) throw new Error("Failed to delete session");

// // // // //       const updatedSessions = sessions.filter(s => s.id !== sessionIdToDelete);
// // // // //       setSessions(updatedSessions);

// // // // //       if (currentSessionId === sessionIdToDelete) {
// // // // //         setCurrentSessionId(updatedSessions[0]?.id || null);
// // // // //       }
// // // // //     } catch (error) {
// // // // //       console.error("Error deleting session:", error);
// // // // //     }
// // // // //   };

// // // // //   useEffect(() => {
// // // // //     fetchSessions();
// // // // //   }, [fetchSessions]);

// // // // //   useEffect(() => {
// // // // //     const handleStateChange = (data: { resource?: string }) => {
// // // // //       if (data?.resource === 'sessions') {
// // // // //         fetchSessions();
// // // // //       }
// // // // //     };
// // // // //     appEventBus.on('state_change', handleStateChange);
// // // // //     return () => {
// // // // //       appEventBus.off('state_change', handleStateChange);
// // // // //     };
// // // // //   }, [fetchSessions]);

// // // // //   return {
// // // // //     userId,
// // // // //     sessions,
// // // // //     isLoading,
// // // // //     currentSessionId,
// // // // //     setCurrentSessionId,
// // // // //     createNewSession,
// // // // //     deleteSession,
// // // // //   };
// // // // // };
// // // // // // import { useState, useEffect, useCallback } from 'react';
// // // // // // import { useLocalStorage } from '@/hooks/useLocalStorage';
// // // // // // import { BRIDGE_API_HTTP_URL } from '@/lib/constants';
// // // // // // import { appEventBus } from '@/lib/eventBus';
// // // // // // import { API_CONFIG } from '@/config';

// // // // // // const DUMMY_USER_ID = 1;

// // // // // // export interface Session {
// // // // // //   id: number;
// // // // // //   title: string;
// // // // // //   created_at: string;
// // // // // //   updated_at: string
// // // // // // }

// // // // // // export const useSession = () => {
// // // // // //   const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
// // // // // //   const [sessions, setSessions] = useState<Session[]>([]);
// // // // // //   const [isLoading, setIsLoading] = useState(true);
// // // // // //   const userId = DUMMY_USER_ID;

// // // // // //   const fetchSessions = useCallback(async () => {
// // // // // //     try {
// // // // // //       setIsLoading(true);
// // // // // //       // const response = await fetch(`${BRIDGE_API_HTTP_URL}/sessions/user/${userId}`);
// // // // // //       const response = await fetch(`${API_CONFIG.SESSION_API_URL}/user/${userId}`);
// // // // // //       if (!response.ok) throw new Error("Failed to fetch sessions");
// // // // // //       const data: Session[] = await response.json();
// // // // // //       setSessions(data);

// // // // // //       // If no session is currently selected OR the selected session no longer exists,
// // // // // //       // automatically select the most recent one.
// // // // // //       if ((!currentSessionId || !data.some(s => s.id === currentSessionId)) && data.length > 0) {
// // // // // //         setCurrentSessionId(data[0].id);
// // // // // //       } else if (data.length === 0) {
// // // // // //         setCurrentSessionId(null);
// // // // // //       }
// // // // // //     } catch (error) {
// // // // // //       console.error("Error fetching sessions:", error);
// // // // // //       setSessions([]);
// // // // // //     } finally {
// // // // // //       setIsLoading(false);
// // // // // //     }
// // // // // //   }, [userId, currentSessionId, setCurrentSessionId]); // Add dependencies

// // // // // //   const createNewSession = async () => {
// // // // // //     try {
// // // // // //       const response = await fetch(`${BRIDGE_API_HTTP_URL}/sessions/user/${userId}`, { method: 'POST' });
// // // // // //       if (!response.ok) throw new Error("Failed to create new session");
// // // // // //       const newSession: Session = await response.json();
      
// // // // // //       // Manually update state to reflect the new session at the top
// // // // // //       setSessions(prev => [newSession, ...prev]);
// // // // // //       // CRITICAL: Immediately set the new session as active.
// // // // // //       setCurrentSessionId(newSession.id);
// // // // // //     } catch (error) {
// // // // // //       console.error("Error creating new session:", error);
// // // // // //     }
// // // // // //   };

// // // // // //    const deleteSession = async (sessionIdToDelete: number) => {
// // // // // //     try {
// // // // // //       const response = await fetch(`${BRIDGE_API_HTTP_URL}/sessions/${sessionIdToDelete}`, {
// // // // // //         method: 'DELETE',
// // // // // //       });
// // // // // //       if (!response.ok) throw new Error("Failed to delete session");

// // // // // //       // Update the local state to remove the deleted session instantly
// // // // // //       const updatedSessions = sessions.filter(s => s.id !== sessionIdToDelete);
// // // // // //       setSessions(updatedSessions);

// // // // // //       // --- CRITICAL EDGE CASE: Handle deleting the active session ---
// // // // // //       if (currentSessionId === sessionIdToDelete) {
// // // // // //         // If there are any sessions left, select the newest one (the first in the list).
// // // // // //         // Otherwise, set the current session to null.
// // // // // //         const newActiveSessionId = updatedSessions[0]?.id || null;
// // // // // //         setCurrentSessionId(newActiveSessionId);
// // // // // //       }
// // // // // //     } catch (error) {
// // // // // //       console.error("Error deleting session:", error);
// // // // // //       // Optionally show an error toast to the user
// // // // // //     }
// // // // // //   };


// // // // // //   useEffect(() => {
// // // // // //     fetchSessions();
// // // // // //   }, [fetchSessions]); // Fetch sessions on initial load

// // // // // //   useEffect(() => {
// // // // // //     const handleStateChange = (data: { resource?: string }) => {
// // // // // //       // Check if the update is relevant to the 'sessions' resource
// // // // // //       if (data?.resource === 'sessions') {
// // // // // //         console.log('[EventBus] Received "sessions" state change signal. Refetching sessions...');
// // // // // //         fetchSessions();
// // // // // //       }
// // // // // //     };

// // // // // //     appEventBus.on('state_change', handleStateChange);

// // // // // //     return () => {
// // // // // //       appEventBus.off('state_change', handleStateChange);
// // // // // //     };
// // // // // //   }, [fetchSessions]); // Dependency on fetchSessions is safe due to useCallback


// // // // // //   return {
// // // // // //     userId,
// // // // // //     sessions,
// // // // // //     isLoading,
// // // // // //     currentSessionId,
// // // // // //     setCurrentSessionId,
// // // // // //     createNewSession,
// // // // // //     deleteSession, // <-- Expose the new function
// // // // // //   };
// // // // // // };