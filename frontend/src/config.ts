// todo-ui/src/config.ts

// The single, unchanging location of our backend API server during local development.
const API_ORIGIN = 'http://localhost:8000';

// This config now builds all URLs from a single, reliable source.
export const API_CONFIG = {
  // All standard API calls are made to the root of the backend server.
  HTTP_ROOT: API_ORIGIN, // e.g., http://localhost:8000/lists
  // The AI WebSocket connects to the backend server.
  // WEBSOCKET_URL: `ws://localhost:8000/ai/ws`,
};

export const LIVEKIT_CONFIG = {
  // The LiveKit server is a separate process on a different port.
  SERVER_URL: 'ws://localhost:7880',
  // The token endpoint is a special route on our backend.
  TOKEN_ENDPOINT: `${API_ORIGIN}/api/livekit/token`,
};

// The TURN server is a separate Docker container on a different port.
export const PEER_CONNECTION_CONFIG: RTCConfiguration = {
  iceServers: [{
    urls: 'turn:localhost:3478',
    username: 'demo',
    credential: 'password'
  }],
};
// This is also now obsolete.
// export const PEER_CONNECTION_CONFIG = { ... };
// const host = window.location.hostname;
// const port = window.location.port ? `:${window.location.port}` : '';
// const origin = `${window.location.protocol}//${host}${port}`;
// // const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
// // const wsOrigin = `${wsProtocol}//${host}${port}`;

// // export const API_CONFIG = {
// //   HTTP_ROOT: origin,
// //   // The old WEBSOCKET_URL is now obsolete.
// // };

// // --- THIS IS THE KEY ADDITION ---
// export const LIVEKIT_CONFIG = {
//   SERVER_URL: `ws://${host}:7880`,
//   // This must match the special /api prefix in your app/main.py
//   TOKEN_ENDPOINT: `${origin}/api/livekit/token`,
// };
// export const API_CONFIG = {
//   HTTP_ROOT: import.meta.env.VITE_API_URL || 'http://localhost:8000',
//   LIVEKIT_URL: import.meta.env.VITE_LIVEKIT_URL || 'ws://localhost:7880',
// };
// // This is also now obsolete.
// // export const PEER_CONNECTION_CONFIG = { ... };