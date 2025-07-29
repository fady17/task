// import React, { createContext, useContext, useState, useEffect, type ReactNode, useMemo } from 'react';
// import { fetchAppConfig, type AppConfig } from '@/config';
// import { useSession } from '@/features/chatbot/hooks/useSession';
// import { connectionManager } from '@/lib/connectionManager';
// import type { ConnectionStatus } from '@/types';

// // Define the shape of all our global contexts combined
// interface AppContextType {
//   config: AppConfig;
//   sessionData: ReturnType<typeof useSession>;
//   connectionStatus: ConnectionStatus;
//   reconnect: () => void;
// }

// // Create the single context
// const AppContext = createContext<AppContextType | undefined>(undefined);

// export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
//   // --- Stage 1: Load Configuration ---
//   const [config, setConfig] = useState<AppConfig | null>(null);
//   const [error, setError] = useState<string | null>(null);

//   useEffect(() => {
//     fetchAppConfig()
//       .then(setConfig)
//       .catch((err) => setError(err.message || 'Unknown error'));
//   }, []);

//   // --- Stage 2: Manage Connection (depends on config) ---
//   const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  
//   useEffect(() => {
//     if (config) {
//       connectionManager.onStatusChange = (newStatus) => {
//         setConnectionStatus(newStatus as ConnectionStatus);
//       };
//       connectionManager.connect(config);
//     }
//   }, [config]); // This effect runs only after config is loaded

//   // --- Stage 3: Manage Session Data (depends on config) ---
//   // We can't use the useSession hook directly here because it also needs the config.
//   // We will pass the config to it. Let's modify useSession slightly.
  
//   const sessionData = useSession(config); // Pass config to the hook

//   // Memoize the context value to prevent unnecessary re-renders
//   const value = useMemo(() => {
//     if (!config) return undefined;
//     return {
//       config,
//       sessionData,
//       connectionStatus,
//       reconnect: () => connectionManager.reconnect(),
//     };
//   }, [config, sessionData, connectionStatus]);

//   // --- Render Logic ---
//   if (error) {
//     return <div>Error loading application: {error}</div>;
//   }
//   if (!value) {
//     return <div>Loading Application...</div>; // Show loading until config and session data are ready
//   }

//   return (
//     <AppContext.Provider value={value}>
//       {children}
//     </AppContext.Provider>
//   );
// };

// // A single hook to rule them all
// export const useAppContext = () => {
//   const context = useContext(AppContext);
//   if (!context) {
//     throw new Error('useAppContext must be used within an AppProvider');
//   }
//   return context;
// };