// import React, { createContext, useContext, useState, useEffect, type ReactNode, useMemo } from 'react';
// import { connectionManager } from '@/lib/connectionManager';
// import type { ConnectionStatus } from '@/types';
// import { useConfig } from '@/context/ConfigContext'; // <-- Import the config hook

// interface ConnectionContextType {
//   connectionStatus: ConnectionStatus;
//   reconnect: () => void;
// }

// const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined);

// export const ConnectionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
//   const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
//   const config = useConfig(); // Get the loaded config from the parent provider

//   useEffect(() => {
//     // This effect now depends on the config object. It will not run until
//     // the ConfigProvider has successfully loaded the configuration.
//     if (config) {
//       console.log("🛠️ Config is ready, initializing connection...");
      
//       connectionManager.onStatusChange = (newStatus) => {
//         setConnectionStatus(newStatus as ConnectionStatus);
//       };
      
//       // Pass the loaded config to the connect method.
//       connectionManager.connect(config);
//     }
//   }, [config]); // The dependency on 'config' is crucial.

//   const value = useMemo(() => ({
//     connectionStatus,
//     reconnect: () => connectionManager.reconnect(),
//   }), [connectionStatus]);

//   return (
//     <ConnectionContext.Provider value={value}>
//       {children}
//     </ConnectionContext.Provider>
//   );
// };

// export const useConnection = () => {
//   const context = useContext(ConnectionContext);
//   if (!context) {
//     throw new Error('useConnection must be used within a ConnectionProvider');
//   }
//   return context;
// };
// // import React, { createContext, useContext, useState, useEffect, type ReactNode, useMemo } from 'react';
// // import { connectionManager } from '@/lib/connectionManager';
// // import type { ConnectionStatus } from '@/types';
// // import { fetchAppConfig } from '@/config'; // <-- Import your promise-based config fetcher

// // // Define the shape of the data and functions our new context will provide.
// // interface ConnectionContextType {
// //   connectionStatus: ConnectionStatus;
// //   reconnect: () => void;
// // }

// // // Create the context.
// // const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined);

// // /**
// //  * This provider's sole responsibility is to manage the lifecycle of the
// //  * global connectionManager and provide its status to the entire app.
// //  */
// // export const ConnectionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
// //   const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');

// //   // This useEffect runs ONLY ONCE when the application mounts.
// //   useEffect(() => {
// //     console.log("🛠️ Initializing ConnectionProvider (should happen only once)");
    
// //     // The provider's state setter is the single, stable callback for the manager.
// //     connectionManager.onStatusChange = (newStatus) => {
// //       console.log(`📡 ConnectionProvider received status update: ${newStatus}`);
// //       setConnectionStatus(newStatus as ConnectionStatus);
// //     };
    
// //     // --- THE FIX IS HERE ---
// //     // We call the async function to fetch the config and then initiate the connection.
// //     const initializeConnection = async () => {
// //       try {
// //         console.log("Fetching app configuration...");
// //         const config = await fetchAppConfig(); // Wait for the config to be loaded
// //         console.log("Configuration loaded, now connecting WebSocket...");
// //         connectionManager.connect(config); // Initiate the connection with the loaded config
// //       } catch (error) {
// //         console.error("Failed to initialize connection due to config error:", error);
// //         // If config fails, we can't connect, so we set an error state.
// //         setConnectionStatus('error');
// //       }
// //     };
    
// //     initializeConnection();
// //     // --- END OF FIX ---

// //   }, []); // The empty dependency array is correct and crucial.

// //   // useMemo ensures that the context value object is stable
// //   const value = useMemo(() => ({
// //     connectionStatus,
// //     reconnect: () => connectionManager.reconnect(),
// //   }), [connectionStatus]);

// //   return (
// //     <ConnectionContext.Provider value={value}>
// //       {children}
// //     </ConnectionContext.Provider>
// //   );
// // };

// // /**
// //  * A custom hook for easy, type-safe access to the connection context.
// //  */
// // export const useConnection = () => {
// //   const context = useContext(ConnectionContext);
// //   if (!context) {
// //     throw new Error('useConnection must be used within a ConnectionProvider');
// //   }
// //   return context;
// // };