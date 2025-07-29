// import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
// import { fetchAppConfig, type AppConfig } from '@/config';

// interface ConfigContextType {
//   config: AppConfig;
// }

// const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

// export const ConfigProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
//   const [config, setConfig] = useState<AppConfig | null>(null);
//   const [error, setError] = useState<string | null>(null);

//   useEffect(() => {
//     fetchAppConfig()
//       .then(setConfig)
//       .catch((err) => setError(err.message || 'Unknown error'));
//   }, []);

//   if (error) {
//     return <div className="h-screen w-screen flex items-center justify-center bg-red-900 text-white">Error: {error}</div>;
//   }
//   if (!config) {
//     return <div className="h-screen w-screen flex items-center justify-center bg-black text-white">Loading Configuration...</div>;
//   }

//   return (
//     <ConfigContext.Provider value={{ config }}>
//       {children}
//     </ConfigContext.Provider>
//   );
// };

// export const useConfig = () => {
//   const context = useContext(ConfigContext);
//   if (!context) {
//     throw new Error('useConfig must be used within a ConfigProvider');
//   }
//   return context.config;
// };
// // import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
// // import { fetchAppConfig, type AppConfig } from '@/config';

// // interface ConfigContextType {
// //   config: AppConfig; // The config is guaranteed to exist for all children.
// // }

// // const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

// // export const ConfigProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
// //   const [config, setConfig] = useState<AppConfig | null>(null);
// //   const [error, setError] = useState<string | null>(null);

// //   useEffect(() => {
// //     // This effect runs once on app startup to fetch the config.
// //     fetchAppConfig()
// //       .then(setConfig)
// //       .catch((err) => setError(err.message || 'Unknown error'));
// //   }, []);

// //   if (error) {
// //     return <div className="h-screen w-screen flex items-center justify-center bg-red-900 text-white">Error: {error}</div>;
// //   }
  
// //   if (!config) {
// //     return <div className="h-screen w-screen flex items-center justify-center bg-black text-white">Loading Configuration...</div>;
// //   }

// //   // Only render the app once the config is successfully loaded.
// //   return (
// //     <ConfigContext.Provider value={{ config }}>
// //       {children}
// //     </ConfigContext.Provider>
// //   );
// // };

// // // The custom hook that components will use to access the loaded config.
// // export const useConfig = () => {
// //   const context = useContext(ConfigContext);
// //   if (!context) {
// //     throw new Error('useConfig must be used within a ConfigProvider');
// //   }
// //   return context.config;
// // };
// // import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
// // import type { AppConfig } from '@/config'; // The interface from our config.ts

// // interface ConfigContextType {
// //   config: AppConfig | null;
// //   isLoading: boolean;
// //   error: Error | null;
// // }

// // const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

// // export const ConfigProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
// //   const [config, setConfig] = useState<AppConfig | null>(null);
// //   const [isLoading, setIsLoading] = useState(true);
// //   const [error, setError] = useState<Error | null>(null);

// //   useEffect(() => {
// //     // This effect runs once on app startup to fetch the config.
// //     const loadConfig = async () => {
// //       try {
// //         const response = await fetch('/api/config');
// //         if (!response.ok) throw new Error('Network response was not ok');
// //         const appConfig: AppConfig = await response.json();
// //         setConfig(appConfig);
// //       } catch (err: any) {
// //         setError(err);
// //       } finally {
// //         setIsLoading(false);
// //       }
// //     };
// //     loadConfig();
// //   }, []);

// //   if (isLoading) {
// //     return <div>Loading Configuration...</div>; // Or a nice spinner
// //   }
// //   if (error) {
// //     return <div>Error: Could not load application configuration. Please try again.</div>;
// //   }

// //   // Only render the rest of the app once the config is loaded.
// //   return (
// //     <ConfigContext.Provider value={{ config, isLoading, error }}>
// //       {children}
// //     </ConfigContext.Provider>
// //   );
// // };

// // export const useConfig = () => {
// //   const context = useContext(ConfigContext);
// //   if (!context) throw new Error('useConfig must be used within a ConfigProvider');
// //   return context.config; // Return the config object directly
// // };