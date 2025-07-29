// todo-ui/src/config.ts

// These variables are determined dynamically from the browser's current URL
const httpProtocol = window.location.protocol;
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = window.location.hostname;
const port = window.location.port ? `:${window.location.port}` : '';

// The base origin for all API calls (e.g., "https://192.168.1.10")
const httpOrigin = `${httpProtocol}//${host}${port}`;
// The base origin for all WebSocket calls (e.g., "wss://192.168.1.10")
const wsOrigin = `${wsProtocol}//${host}${port}`;

export const API_CONFIG = {
  // All HTTP requests are built from this root
  HTTP_ROOT: `${httpOrigin}/api`,
  // The AI WebSocket connects to this URL
  WEBSOCKET_URL: `${wsOrigin}/api/ai/ws`,
};

export const LIVEKIT_CONFIG = {
  // The LiveKit server connects via WebSocket to the same host, but on port 7880
  SERVER_URL: `ws://${host}:7880`,
};

// You can also make the TURN server dynamic
export const PEER_CONNECTION_CONFIG: RTCConfiguration = {
  iceServers: [{
    urls: `turn:${host}:3478`,
    username: 'demo',
    credential: 'password'
  }],
};
// // Check if we're in development mode
// const isDevelopment = import.meta.env.DEV || window.location.hostname === 'localhost';

// // In development, use the backend server directly
// // In production, use the same origin (assuming backend and frontend are served from same domain)
// const backendHost = isDevelopment ? 'localhost:8000' : window.location.host;
// const backendProtocol = isDevelopment ? 'http:' : window.location.protocol;
// // const wsProtocol = backendProtocol === 'https:' ? 'wss:' : 'ws:';
// const API_ORIGIN = 'http://localhost:8000';
// const WS_ORIGIN = 'ws://localhost:8000';

// // export const API_CONFIG = {
// //   // HTTP_ROOT: `${backendProtocol}//${backendHost}`,
// //   // WEBSOCKET_URL: `${wsProtocol}//${backendHost}/ai/ws`,
// //   HTTP_ROOT: `${API_ORIGIN}/api`,
// //   WEBSOCKET_URL: `${WS_ORIGIN}/api/ws`,
// // };
// export const API_CONFIG = {
//   // All HTTP requests are based from this root.
//   HTTP_ROOT: `${API_ORIGIN}/api`,
//   // The WebSocket URL needs the /ai prefix.
//   WEBSOCKET_URL: `${WS_ORIGIN}/api/ai/ws`, // <-- Corrected path
// };


// export const LIVEKIT_CONFIG = {
//   // The full URL for the LiveKit server
//   URL: `ws://localhost:7880`,
//   // The full URL for our API's token endpoint
//   TOKEN_ENDPOINT: `${backendProtocol}//${backendHost}/api/livekit/token`,
// };

// export const PEER_CONNECTION_CONFIG: RTCConfiguration = {
//   iceServers: [{
//     urls: `turn:localhost:3478`, // Use localhost for TURN server
//     username: 'demo',
//     credential: 'password'
//   }],
// };

// // const host = window.location.hostname;
// // const port = window.location.port ? `:${window.location.port}` : '';
// // const origin = `${window.location.protocol}//${host}${port}`;
// // const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
// // const wsOrigin = `${wsProtocol}//${host}${port}`;

// // export const API_CONFIG = {
// //   HTTP_ROOT: `${origin}`,
// //   WEBSOCKET_URL: `${wsOrigin}/ai/ws`,
// // };

// // // export const VOICE_CONFIG = {
// // //   WEBSOCKET_URL: `${wsOrigin}/ws`,
// // // };
// // export const LIVEKIT_CONFIG = {
// //     // The full URL for the LiveKit server
// //     URL: `ws://localhost:7880`,
// //     // The full URL for our API's token endpoint
// //     TOKEN_ENDPOINT: `http://localhost:8000/api/livekit/token`,
// // }

// // export const PEER_CONNECTION_CONFIG: RTCConfiguration = {
// //   iceServers: [{
// //     urls: `turn:${host}:3478`,
// //     username: 'demo',
// //     credential: 'password'
// //   }],
// // };


// // // // This file is the single source of truth for all network configuration.
// // // // It dynamically builds URLs based on how the user accessed the page.

// // // const host = window.location.hostname;
// // // const port = window.location.port ? `:${window.location.port}` : '';
// // // const origin = `${window.location.protocol}//${host}${port}`;
// // // const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
// // // const wsOrigin = `${wsProtocol}//${host}${port}`;

// // // /**
// // //  * Configuration for the main AI Chat and To-Do List API.
// // //  * The NGINX reverse proxy will route requests starting with /api to the correct backend.
// // //  */
// // // export const API_CONFIG = {
// // //   // Base URL for all HTTP calls (e.g., https://192.168.1.3/api)
// // //   HTTP_ROOT: `${origin}/api`,
// // //   // WebSocket URL for the AI chat
// // //   WEBSOCKET_URL: `${wsOrigin}/api/ai/ws`,
// // // };

// // // /**
// // //  * Configuration for the Voice Conference Service.
// // //  */
// // // export const VOICE_CONFIG = {
// // //   // The NGINX proxy will route /voice-api to the voice service.
// // //   WEBSOCKET_URL: `${wsOrigin}/voice-api/ws`,
// // // };

// // // /**
// // //  * WebRTC configuration. The browser connects directly to the host's TURN port.
// // //  */
// // // export const PEER_CONNECTION_CONFIG: RTCConfiguration = {
// // //   iceServers: [{
// // //     urls: `turn:${host}:3478`,
// // //     username: 'demo',
// // //     credential: 'password'
// // //   }],
// // // };
// // // // // This file will now hold the fetched configuration.

// // // // export interface AppConfig {
// // // //   api_host: string;
// // // //   api_port: number;
// // // //   voice_api_port: number;
// // // //   turn_server: RTCIceServer;
// // // // }

// // // // // A singleton promise to fetch the config only once.
// // // // let configPromise: Promise<AppConfig> | null = null;

// // // // export const fetchAppConfig = (): Promise<AppConfig> => {
// // // //   if (configPromise) {
// // // //     return configPromise;
// // // //   }

// // // //   // The '/api' prefix is handled by NGINX in Docker, or Vite proxy in local dev.
// // // //   // We fetch from a relative path, making it portable.
// // // //   configPromise = fetch('/api/config')
// // // //     .then(response => {
// // // //       if (!response.ok) {
// // // //         throw new Error('Failed to fetch server configuration');
// // // //       }
// // // //       return response.json();
// // // //     })
// // // //     .then((config: AppConfig) => {
// // // //       console.log('App configuration loaded from server:', config);
// // // //       return config;
// // // //     })
// // // //     .catch(error => {
// // // //       console.error("CRITICAL: Could not load app configuration. Falling back to localhost.", error);
// // // //       // Fallback for local development if the API isn't running
// // // //       return {
// // // //         api_host: 'localhost',
// // // //         api_port: 8000,
// // // //         voice_api_port: 8001,
// // // //         turn_server: {
// // // //           urls: 'turn:127.0.0.1:3478',
// // // //           username: 'demo',
// // // //           credential: 'password',
// // // //         },
// // // //       };
// // // //     });

// // // //   return configPromise;
// // // // };
// // // // // // This file is the single source of truth for all network configuration.
// // // // // const host = window.location.hostname;
// // // // // const port = window.location.port ? `:${window.location.port}` : '';
// // // // // const origin = `${window.location.protocol}//${host}${port}`;
// // // // // const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
// // // // // const wsOrigin = `${wsProtocol}//${host}${port}`;

// // // // // // --- API CONFIG FOR AI CHAT & TO-DO LIST ---
// // // // // export const API_CONFIG = {
// // // // //   // Base URL for all HTTP calls to the main backend
// // // // //   HTTP_ROOT: origin,
// // // // //   // Full URL for the AI chat session API
// // // // //   SESSION_API_URL: `${origin}/ai/sessions`,
// // // // //   // --- FIX: Renamed from CHAT_WEBSOCKET_URL to WEBSOCKET_URL for consistency ---
// // // // //   WEBSOCKET_URL: `${wsOrigin}/ai/ws`, 
// // // // // };

// // // // // // --- VOICE SERVICE CONFIG ---
// // // // // export const VOICE_CONFIG = {
// // // // //   WEBSOCKET_URL: `${wsOrigin}/ws`,
// // // // // };

// // // // // // --- WEBRTC CONFIG ---
// // // // // export const PEER_CONNECTION_CONFIG: RTCConfiguration = {
// // // // //   iceServers: [{
// // // // //     // The browser connects to the TURN server via the host machine's port mapping
// // // // //     urls: `turn:${host}:3478`,
// // // // //     username: 'demo',
// // // // //     credential: 'password'
// // // // //   }],
// // // // // };
