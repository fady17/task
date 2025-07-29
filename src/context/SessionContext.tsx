import { createContext, useContext, type ReactNode } from 'react';
import { useSession } from '@/features/chatbot/hooks/useSession';
import type { Session } from '@/types';

// Define the exact shape of the data and functions that useSession returns.
export interface SessionContextType {
  sessions: Session[];
  isLoading: boolean;
  currentSessionId: number | null;
  setCurrentSessionId: (id: number | null) => void;
  createNewSession: () => Promise<Session | undefined>;
  deleteSession: (sessionId: number) => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

// The provider component. Its only job is to call the hook once.
export function SessionProvider({ children }: { children: ReactNode }) {
  const sessionData = useSession();
  return (
    <SessionContext.Provider value={sessionData}>
      {children}
    </SessionContext.Provider>
  );
}

// The consumer hook that all other components will use.
export function useSessionContext() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSessionContext must be used within a SessionProvider');
  }
  return context;
}
// import { createContext, useContext, type ReactNode } from 'react';
// import { useSession } from '@/features/chatbot/hooks/useSession';
// import type { Session } from '@/types';

// // The context type MUST match what useSession returns.
// interface SessionContextType {
//   userId: number;
//   sessions: Session[];
//   isLoading: boolean;
//   currentSessionId: number | null;
//   setCurrentSessionId: (id: number | null) => void;
//   createNewSession: () => Promise<Session | undefined>;
//   deleteSession: (sessionId: number) => Promise<void>; 
// }

// const SessionContext = createContext<SessionContextType | undefined>(undefined);

// export function SessionProvider({ children }: { children: ReactNode }) {
//   const sessionData = useSession();
//   return (
//     <SessionContext.Provider value={sessionData}>
//       {children}
//     </SessionContext.Provider>
//   );
// }

// export function useSessionContext() {
//   const context = useContext(SessionContext);
//   if (context === undefined) {
//     throw new Error('useSessionContext must be used within a SessionProvider');
//   }
//   return context;
// }
// // import  { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
// // import { useLocalStorage } from '@/hooks/useLocalStorage';
// // import { appEventBus } from '@/lib/eventBus';
// // import { useConfig } from '@/context/ConfigContext';
// // import type { Session } from '@/types';

// // const USER_ID = 1;

// // // Define the shape of the data the context will provide.
// // interface SessionContextType {
// //   userId: number;
// //   sessions: Session[];
// //   isLoading: boolean;
// //   currentSessionId: number | null;
// //   setCurrentSessionId: (id: number | null) => void;
// //   createNewSession: () => Promise<Session | undefined>;
// //   deleteSession: (sessionId: number) => Promise<void>;
// // }

// // const SessionContext = createContext<SessionContextType | undefined>(undefined);

// // export function SessionProvider({ children }: { children: ReactNode }) {
// //   // --- ALL LOGIC FROM useSession IS NOW HERE ---
// //   const config = useConfig(); // Get the global config
// //   const [currentSessionId, setCurrentSessionId] = useLocalStorage<number | null>('currentSessionId', null);
// //   const [sessions, setSessions] = useState<Session[]>([]);
// //   const [isLoading, setIsLoading] = useState(true);
// //   const userId = USER_ID;

// //   // Build the dynamic URL inside the provider
// //   const SESSION_API_URL = config ? `http://${config.api_host}:${config.api_port}/ai/sessions` : '';

// //   const fetchSessions = useCallback(async () => {
// //     if (!SESSION_API_URL) return; // Don't fetch if config isn't ready
// //     setIsLoading(true);
// //     try {
// //       const response = await fetch(`${SESSION_API_URL}/user/${userId}`);
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
// //   }, [userId, currentSessionId, setCurrentSessionId, SESSION_API_URL]);

// //   const createNewSession = async (): Promise<Session | undefined> => {
// //     if (!SESSION_API_URL) return undefined;
// //     try {
// //       const response = await fetch(`${SESSION_API_URL}/user/${userId}`, { method: 'POST' });
// //       if (!response.ok) throw new Error("Failed to create new session");
// //       const newSession: Session = await response.json();
// //       setSessions(prev => [newSession, ...prev]);
// //       setCurrentSessionId(newSession.id);
// //       return newSession;
// //     } catch (error) {
// //       console.error("Error creating new session:", error);
// //       return undefined;
// //     }
// //   };

// //   const deleteSession = async (sessionIdToDelete: number) => {
// //     if (!SESSION_API_URL) return;
// //     try {
// //       const response = await fetch(`${SESSION_API_URL}/${sessionIdToDelete}`, { method: 'DELETE' });
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

// //   useEffect(() => {
// //     const handleStateChange = (data: { resource?: string }) => {
// //       if (data?.resource === 'sessions') {
// //         fetchSessions();
// //       }
// //     };
// //     appEventBus.on('state_change', handleStateChange);
// //     return () => {
// //       appEventBus.off('state_change', handleStateChange);
// //     };
// //   }, [fetchSessions]);
  
// //   // The value provided to the context contains all the state and functions.
// //   const value = {
// //     userId,
// //     sessions,
// //     isLoading,
// //     currentSessionId,
// //     setCurrentSessionId,
// //     createNewSession,
// //     deleteSession,
// //   };

// //   return (
// //     <SessionContext.Provider value={value}>
// //       {children}
// //     </SessionContext.Provider>
// //   );
// // }

// // // The consumer hook remains the same.
// // export function useSessionContext() {
// //   const context = useContext(SessionContext);
// //   if (context === undefined) {
// //     throw new Error('useSessionContext must be used within a SessionProvider');
// //   }
// //   return context;
// // }
// // // import { createContext, useContext, type ReactNode } from 'react';
// // // import { useSession } from '../hooks/useSession';
// // // import type { Session } from '@/types';

// // // // The context type is now focused only on session data and actions.
// // // interface SessionContextType {
// // //   userId: number;
// // //   sessions: Session[];
// // //   isLoading: boolean;
// // //   currentSessionId: number | null;
// // //   setCurrentSessionId: (id: number | null) => void;
// // //   createNewSession: () => Promise<Session | undefined>;
// // //   deleteSession: (sessionId: number) => Promise<void>; 
// // // }

// // // const SessionContext = createContext<SessionContextType | undefined>(undefined);

// // // export function SessionProvider({ children }: { children: ReactNode }) {
// // //   const sessionData = useSession();
// // //   return (
// // //     <SessionContext.Provider value={sessionData}>
// // //       {children}
// // //     </SessionContext.Provider>
// // //   );
// // // }

// // // export function useSessionContext() {
// // //   const context = useContext(SessionContext);
// // //   if (context === undefined) {
// // //     throw new Error('useSessionContext must be used within a SessionProvider');
// // //   }
// // //   return context;
// // // }
// // // // import { createContext, useContext, type ReactNode } from 'react';
// // // // import { useSession} from '../hooks/useSession';
// // // // import type { Session } from '@/types';

// // // // // Define the shape of the data that our context will provide
// // // // interface SessionContextType {
// // // //   userId: number;
// // // //   sessions: Session[];
// // // //   isLoading: boolean;
// // // //   currentSessionId: number | null;
// // // //   setCurrentSessionId: (id: number | null) => void;
// // // //   // --- THE ONLY CHANGE IS HERE ---
// // // //   // The signature now correctly reflects that createNewSession returns a Promise of a Session.
// // // //   createNewSession: () => Promise<Session | undefined>;
// // // //   deleteSession: (sessionId: number) => Promise<void>; 
// // // //   chatConnectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
// // // //   reconnectChat: () => void;
// // // // }

// // // // // Create the context.
// // // // const SessionContext = createContext<SessionContextType | undefined>(undefined);

// // // // // Create the provider component.
// // // // export function SessionProvider({ children }: { children: ReactNode }) {
// // // //   const sessionData = useSession();

// // // //   return (
// // // //     <SessionContext.Provider value={sessionData}>
// // // //       {children}
// // // //     </SessionContext.Provider>
// // // //   );
// // // // }

// // // // // Create a custom hook for easy consumption of the context.
// // // // export function useSessionContext() {
// // // //   const context = useContext(SessionContext);
// // // //   if (context === undefined) {
// // // //     throw new Error('useSessionContext must be used within a SessionProvider');
// // // //   }
// // // //   return context;
// // // // }

// // // // // import { createContext, useContext, type ReactNode } from 'react';
// // // // // import { useSession, type Session } from '../hooks/useSession';

// // // // // // Define the shape of the data that our context will provide
// // // // // interface SessionContextType {
// // // // //   userId: number;
// // // // //   sessions: Session[];
// // // // //   isLoading: boolean;
// // // // //   currentSessionId: number | null;
// // // // //   setCurrentSessionId: (id: number | null) => void;
// // // // //   createNewSession: () => Promise<void>;
// // // // //   deleteSession: (sessionId: number) => Promise<void>; 
// // // // // }

// // // // // // Create the context. We initialize it as undefined.
// // // // // const SessionContext = createContext<SessionContextType | undefined>(undefined);

// // // // // // Create the provider component. This is the component that will hold the state.
// // // // // export function SessionProvider({ children }: { children: ReactNode }) {
// // // // //   // The useSession hook is now called ONLY ONCE, here in the provider.
// // // // //   const sessionData = useSession();

// // // // //   return (
// // // // //     <SessionContext.Provider value={sessionData}>
// // // // //       {children}
// // // // //     </SessionContext.Provider>
// // // // //   );
// // // // // }

// // // // // // Create a custom hook for easy consumption of the context.
// // // // // // This hook ensures we're always accessing the context from within a provider.
// // // // // export function useSessionContext() {
// // // // //   const context = useContext(SessionContext);
// // // // //   if (context === undefined) {
// // // // //     throw new Error('useSessionContext must be used within a SessionProvider');
// // // // //   }
// // // // //   return context;
// // // // // }