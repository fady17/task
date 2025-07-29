import React, { useRef } from 'react';
import { Button } from '@/components/ui/button';
import { useVoiceEcho } from '../hooks/useVoiceEcho'; // Make sure path is correct

export const VoiceEchoTest: React.FC = () => {
  const { status, startCall, stopCall } = useVoiceEcho();
  const audioPlayerRef = useRef<HTMLAudioElement>(null);

  return (
    <div className="p-4 border rounded-lg bg-card text-card-foreground space-y-4">
      <h3 className="text-lg font-semibold">Voice Echo Test</h3>
      <div className="flex items-center space-x-4">
        <Button
          onClick={() => status === 'disconnected' ? startCall(audioPlayerRef.current) : stopCall()}
          disabled={status === 'connecting'}
        >
          {status === 'connected' ? 'Stop Call' : 'Start Call'}
        </Button>
        <div className="flex items-center space-x-2">
          <span className={`h-3 w-3 rounded-full ${
            status === 'connected' ? 'bg-green-500' :
            status === 'connecting' ? 'bg-yellow-500 animate-pulse' :
            'bg-red-500'
          }`}></span>
          <span className="capitalize font-medium">{status}</span>
        </div>
      </div>
      <div>
        <p className="text-sm text-muted-foreground mb-2">
          Click "Start Call" and allow microphone access. You should hear your voice echoed back.
        </p>
        <audio ref={audioPlayerRef} autoPlay controls className="w-full" />
      </div>
    </div>
  );
};
// import React, { useState, useRef, useEffect, useCallback } from 'react';
// import { Button } from '@/components/ui/button';
// import { Alert, AlertDescription } from '@/components/ui/alert';
// import { Badge } from '@/components/ui/badge';

// // Configuration for the voice service
// const VOICE_API_WS_URL = 'ws://localhost:8001/ws';
// const PEER_CONNECTION_CONFIG: RTCConfiguration = {
//   iceServers: [
//     {
//       urls: [
//         'stun:127.0.0.1:3478',
//         'turn:127.0.0.1:3478'
//       ],
//       username: 'demo',
//       credential: 'password'
//     }
//   ],
// };

// type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';
// type WebSocketStatus = 'closed' | 'connecting' | 'open' | 'error';
// type MediaStatus = 'none' | 'requesting' | 'granted' | 'denied';

// interface DebugInfo {
//   timestamp: string;
//   level: 'info' | 'warn' | 'error';
//   message: string;
//   data?: any;
// }

// export const VoiceEchoTest: React.FC = () => {
//   const [status, setStatus] = useState<ConnectionStatus>('disconnected');
//   const [wsStatus, setWsStatus] = useState<WebSocketStatus>('closed');
//   const [mediaStatus, setMediaStatus] = useState<MediaStatus>('none');
//   const [iceConnectionState, setIceConnectionState] = useState<RTCIceConnectionState>('new');
//   const [debugLogs, setDebugLogs] = useState<DebugInfo[]>([]);
//   const [showDebugLogs, setShowDebugLogs] = useState(false);
//   const [error, setError] = useState<string | null>(null);
//   const [audioLevel, setAudioLevel] = useState<number>(0);
//   const [reconnectAttempts, setReconnectAttempts] = useState(0);

//   const pcRef = useRef<RTCPeerConnection | null>(null);
//   const wsRef = useRef<WebSocket | null>(null);
//   const audioPlayerRef = useRef<HTMLAudioElement>(null);
//   const localStreamRef = useRef<MediaStream | null>(null);
//   const audioContextRef = useRef<AudioContext | null>(null);
//   const analyserRef = useRef<AnalyserNode | null>(null);
//   const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

//   const addDebugLog = useCallback((level: 'info' | 'warn' | 'error', message: string, data?: any) => {
//     const log: DebugInfo = {
//       timestamp: new Date().toISOString().split('T')[1].split('.')[0],
//       level,
//       message,
//       data
//     };
    
//     setDebugLogs(prev => [...prev.slice(-49), log]); // Keep last 50 logs
    
//     if (level === 'error') {
//       console.error(`[Voice Error] ${message}`, data);
//     } else if (level === 'warn') {
//       console.warn(`[Voice Warn] ${message}`, data);
//     } else {
//       console.log(`[Voice Info] ${message}`, data);
//     }
//   }, []);

//   const clearError = useCallback(() => {
//     setError(null);
//   }, []);

//   const setupAudioAnalyzer = useCallback((stream: MediaStream) => {
//     try {
//       audioContextRef.current = new AudioContext();
//       analyserRef.current = audioContextRef.current.createAnalyser();
//       const source = audioContextRef.current.createMediaStreamSource(stream);
//       source.connect(analyserRef.current);
      
//       analyserRef.current.fftSize = 256;
//       const bufferLength = analyserRef.current.frequencyBinCount;
//       const dataArray = new Uint8Array(bufferLength);

//       const updateAudioLevel = () => {
//         if (analyserRef.current) {
//           analyserRef.current.getByteFrequencyData(dataArray);
//           const average = dataArray.reduce((a, b) => a + b) / bufferLength;
//           setAudioLevel(average / 255);
//           requestAnimationFrame(updateAudioLevel);
//         }
//       };
//       updateAudioLevel();
      
//       addDebugLog('info', 'Audio analyzer setup complete');
//     } catch (err) {
//       addDebugLog('error', 'Failed to setup audio analyzer', err);
//     }
//   }, [addDebugLog]);

//   const cleanup = useCallback(() => {
//     addDebugLog('info', 'Starting cleanup...');
    
//     // Clear reconnect timeout
//     if (reconnectTimeoutRef.current) {
//       clearTimeout(reconnectTimeoutRef.current);
//       reconnectTimeoutRef.current = null;
//     }

//     // Close peer connection
//     if (pcRef.current) {
//       pcRef.current.close();
//       pcRef.current = null;
//       addDebugLog('info', 'Peer connection closed');
//     }

//     // Close WebSocket
//     if (wsRef.current) {
//       wsRef.current.close();
//       wsRef.current = null;
//       addDebugLog('info', 'WebSocket closed');
//     }

//     // Stop media streams
//     if (localStreamRef.current) {
//       localStreamRef.current.getTracks().forEach(track => {
//         track.stop();
//         addDebugLog('info', `Stopped ${track.kind} track`);
//       });
//       localStreamRef.current = null;
//     }

//     // Clean up audio player
//     if (audioPlayerRef.current && audioPlayerRef.current.srcObject) {
//       const stream = audioPlayerRef.current.srcObject as MediaStream;
//       stream.getTracks().forEach(track => track.stop());
//       audioPlayerRef.current.srcObject = null;
//     }

//     // Clean up audio context
//     if (audioContextRef.current) {
//       audioContextRef.current.close();
//       audioContextRef.current = null;
//       analyserRef.current = null;
//     }

//     // Reset states
//     setStatus('disconnected');
//     setWsStatus('closed');
//     setMediaStatus('none');
//     setIceConnectionState('new');
//     setAudioLevel(0);
    
//     addDebugLog('info', 'Cleanup complete');
//   }, [addDebugLog]);

//   const startCall = async () => {
//     if (pcRef.current) {
//       addDebugLog('warn', 'Call already in progress');
//       return;
//     }

//     setStatus('connecting');
//     setError(null);
//     clearError();
//     addDebugLog('info', 'Starting call...');

//     try {
//       // 1. Get microphone access
//       setMediaStatus('requesting');
//       addDebugLog('info', 'Requesting microphone access...');
      
//       const localStream = await navigator.mediaDevices.getUserMedia({ 
//         audio: {
//           echoCancellation: true,
//           noiseSuppression: true,
//           autoGainControl: true
//         } 
//       });
      
//       localStreamRef.current = localStream;
//       setMediaStatus('granted');
//       addDebugLog('info', 'Microphone access granted', {
//         tracks: localStream.getTracks().map(track => ({
//           kind: track.kind,
//           label: track.label,
//           enabled: track.enabled
//         }))
//       });

//       // Setup audio analyzer
//       setupAudioAnalyzer(localStream);

//       // 2. Setup PeerConnection
//       const pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);
//       pcRef.current = pc;
//       addDebugLog('info', 'Peer connection created');

//       // Connection state monitoring
//       pc.onconnectionstatechange = () => {
//         addDebugLog('info', `Connection state: ${pc.connectionState}`);
//         if (pc.connectionState === 'connected') {
//           setStatus('connected');
//           setReconnectAttempts(0);
//         } else if (pc.connectionState === 'failed') {
//           setStatus('error');
//           setError('Peer connection failed');
//           addDebugLog('error', 'Peer connection failed');
//         } else if (pc.connectionState === 'disconnected') {
//           setStatus('disconnected');
//           addDebugLog('warn', 'Peer connection disconnected');
//         }
//       };

//       // ICE connection state monitoring
//       pc.oniceconnectionstatechange = () => {
//         setIceConnectionState(pc.iceConnectionState);
//         addDebugLog('info', `ICE connection state: ${pc.iceConnectionState}`);
        
//         if (pc.iceConnectionState === 'failed') {
//           addDebugLog('error', 'ICE connection failed - check STUN/TURN configuration');
//           setError('ICE connection failed. Check network connectivity.');
//         }
//       };
      
//       // ICE candidate handling
//       pc.onicecandidate = (event) => {
//         if (event.candidate) {
//           addDebugLog('info', `ICE candidate found: ${event.candidate.type}`, {
//             candidate: event.candidate.candidate,
//             sdpMid: event.candidate.sdpMid
//           });
//         } else {
//           addDebugLog('info', 'ICE candidate gathering complete');
//         }
//       };

//       // Add local tracks
//       localStream.getTracks().forEach(track => {
//         pc.addTrack(track, localStream);
//         addDebugLog('info', `Added ${track.kind} track to peer connection`);
//       });
      
//       // Handle incoming tracks
//       pc.ontrack = (event) => {
//         addDebugLog('info', 'Received remote track', {
//           kind: event.track.kind,
//           streams: event.streams.length
//         });
        
//         if (audioPlayerRef.current && event.streams[0]) {
//           audioPlayerRef.current.srcObject = event.streams[0];
//           addDebugLog('info', 'Set remote stream to audio player');
//         }
//       };

//       // 3. Setup WebSocket
//       setWsStatus('connecting');
//       const ws = new WebSocket(VOICE_API_WS_URL);
//       wsRef.current = ws;
      
//       const wsOpenTimeout = setTimeout(() => {
//         if (ws.readyState === WebSocket.CONNECTING) {
//           addDebugLog('error', 'WebSocket connection timeout');
//           setError('Connection timeout - server may be unavailable');
//           cleanup();
//         }
//       }, 10000);

//       ws.onopen = async () => {
//         clearTimeout(wsOpenTimeout);
//         setWsStatus('open');
//         addDebugLog('info', 'WebSocket connection established');
        
//         try {
//           const offer = await pc.createOffer();
//           await pc.setLocalDescription(offer);
          
//           ws.send(JSON.stringify({ 
//             type: 'offer', 
//             sdp: pc.localDescription?.sdp 
//           }));
          
//           addDebugLog('info', 'Offer sent to server', {
//             sdpSize: pc.localDescription?.sdp?.length
//           });
//         } catch (err) {
//           addDebugLog('error', 'Failed to create or send offer', err);
//           setError('Failed to create connection offer');
//         }
//       };
      
//       ws.onmessage = async (event) => {
//         try {
//           const data = JSON.parse(event.data);
//           addDebugLog('info', `Received ${data.type} from server`);
          
//           if (data.type === 'answer') {
//             await pc.setRemoteDescription(new RTCSessionDescription(data));
//             addDebugLog('info', 'Remote description set successfully');
//           }
//         } catch (err) {
//           addDebugLog('error', 'Failed to handle server message', err);
//         }
//       };

//       ws.onerror = (event) => {
//         setWsStatus('error');
//         addDebugLog('error', 'WebSocket error', event);
//         setError('WebSocket connection error');
//       };
      
//       ws.onclose = (event) => {
//         clearTimeout(wsOpenTimeout);
//         setWsStatus('closed');
//         addDebugLog('warn', 'WebSocket closed', {
//           code: event.code,
//           reason: event.reason,
//           wasClean: event.wasClean
//         });
        
//         if (status === 'connected' && reconnectAttempts < 3) {
//           // Auto-reconnect on unexpected close
//           setReconnectAttempts(prev => prev + 1);
//           addDebugLog('info', `Attempting reconnect ${reconnectAttempts + 1}/3`);
//           reconnectTimeoutRef.current = setTimeout(() => {
//             startCall();
//           }, 2000 * (reconnectAttempts + 1)); // Exponential backoff
//         }
//       };

//     } catch (err: any) {
//       addDebugLog('error', 'Failed to start call', err);
//       setMediaStatus('denied');
//       setStatus('error');
//       setError(err?.message || 'Failed to start call');
//       cleanup();
//     }
//   };

//   const stopCall = useCallback(() => {
//     addDebugLog('info', 'Stopping call...');
//     cleanup();
//   }, [cleanup, addDebugLog]);

//   // Cleanup on unmount
//   useEffect(() => {
//     return () => {
//       cleanup();
//     };
//   }, [cleanup]);

//   const getStatusColor = (currentStatus: ConnectionStatus) => {
//     switch (currentStatus) {
//       case 'connected': return 'bg-green-500';
//       case 'connecting': return 'bg-yellow-500 animate-pulse';
//       case 'error': return 'bg-red-500';
//       default: return 'bg-gray-500';
//     }
//   };

//   return (
//     <div className="p-4 border rounded-lg bg-card text-card-foreground space-y-4">
//       <div className="flex justify-between items-center">
//         <h3 className="text-lg font-semibold">Voice Echo Test</h3>
//         <Button
//           variant="outline"
//           size="sm"
//           onClick={() => setShowDebugLogs(!showDebugLogs)}
//         >
//           {showDebugLogs ? 'Hide' : 'Show'} Debug
//         </Button>
//       </div>

//       {error && (
//         <Alert variant="destructive">
//           <AlertDescription className="flex justify-between items-center">
//             <span>{error}</span>
//             <Button variant="ghost" size="sm" onClick={clearError}>×</Button>
//           </AlertDescription>
//         </Alert>
//       )}

//       <div className="flex items-center justify-between">
//         <div className="flex items-center space-x-4">
//           <Button
//             onClick={status === 'disconnected' ? startCall : stopCall}
//             disabled={status === 'connecting'}
//           >
//             {status === 'disconnected' && 'Start Call'}
//             {status === 'connecting' && 'Connecting...'}
//             {status === 'connected' && 'Stop Call'}
//             {status === 'error' && 'Retry Call'}
//           </Button>
          
//           <div className="flex items-center space-x-2">
//             <span className={`h-3 w-3 rounded-full ${getStatusColor(status)}`}></span>
//             <span className="capitalize font-medium">{status}</span>
//           </div>
//         </div>

//         {reconnectAttempts > 0 && (
//           <Badge variant="secondary">
//             Reconnect {reconnectAttempts}/3
//           </Badge>
//         )}
//       </div>

//       {/* Status indicators */}
//       <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
//         <div className="flex items-center space-x-2">
//           <span className="font-medium">Media:</span>
//           <Badge variant={mediaStatus === 'granted' ? 'default' : 'secondary'}>
//             {mediaStatus}
//           </Badge>
//         </div>
//         <div className="flex items-center space-x-2">
//           <span className="font-medium">WebSocket:</span>
//           <Badge variant={wsStatus === 'open' ? 'default' : 'secondary'}>
//             {wsStatus}
//           </Badge>
//         </div>
//         <div className="flex items-center space-x-2">
//           <span className="font-medium">ICE:</span>
//           <Badge variant={iceConnectionState === 'connected' ? 'default' : 'secondary'}>
//             {iceConnectionState}
//           </Badge>
//         </div>
//         <div className="flex items-center space-x-2">
//           <span className="font-medium">Audio:</span>
//           <div className="w-12 h-2 bg-gray-200 rounded-full overflow-hidden">
//             <div 
//               className="h-full bg-green-500 transition-all duration-100"
//               style={{ width: `${audioLevel * 100}%` }}
//             />
//           </div>
//         </div>
//       </div>

//       <div>
//         <p className="text-sm text-muted-foreground mb-2">
//           Click "Start Call" and allow microphone access. You should hear your voice echoed back.
//         </p>
//         <audio ref={audioPlayerRef} autoPlay controls className="w-full" />
//       </div>

//       {showDebugLogs && (
//         <div className="mt-4 p-3 bg-muted rounded-lg max-h-64 overflow-y-auto">
//           <div className="flex justify-between items-center mb-2">
//             <h4 className="font-medium">Debug Logs</h4>
//             <Button 
//               variant="ghost" 
//               size="sm" 
//               onClick={() => setDebugLogs([])}
//             >
//               Clear
//             </Button>
//           </div>
//           <div className="space-y-1 font-mono text-xs">
//             {debugLogs.map((log, index) => (
//               <div key={index} className={`
//                 ${log.level === 'error' ? 'text-red-600' : 
//                   log.level === 'warn' ? 'text-yellow-600' : 
//                   'text-foreground'}
//               `}>
//                 <span className="text-muted-foreground">[{log.timestamp}]</span>{' '}
//                 <span className="font-semibold">{log.level.toUpperCase()}</span>{' '}
//                 {log.message}
//                 {log.data && (
//                   <details className="mt-1 ml-4">
//                     <summary className="cursor-pointer text-muted-foreground">
//                       Show data
//                     </summary>
//                     <pre className="mt-1 p-2 bg-background rounded text-xs overflow-x-auto">
//                       {JSON.stringify(log.data, null, 2)}
//                     </pre>
//                   </details>
//                 )}
//               </div>
//             ))}
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };
// // import React, { useState, useRef, useEffect } from 'react';
// // import { Button } from '@/components/ui/button'; // Assuming you use ShadCN UI

// // // Configuration for the voice service
// // const VOICE_API_WS_URL = 'ws://localhost:8001/ws';
// // const PEER_CONNECTION_CONFIG: RTCConfiguration = {
// //   iceServers: [
// //     {
// //       urls: [
// //         'stun:127.0.0.1:3478',
// //         'turn:127.0.0.1:3478'
// //       ],
// //       username: 'demo',
// //       credential: 'password'
// //     }
// //   ],
// // };

// // type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

// // export const VoiceEchoTest: React.FC = () => {
// //   const [status, setStatus] = useState<ConnectionStatus>('disconnected');
// //   const pcRef = useRef<RTCPeerConnection | null>(null);
// //   const wsRef = useRef<WebSocket | null>(null);
// //   const audioPlayerRef = useRef<HTMLAudioElement>(null);

// //   const startCall = async () => {
// //     if (pcRef.current) return; // Already in a call

// //     setStatus('connecting');
// //     console.log('[Voice] Starting call...');

// //     try {
// //       // 1. Get microphone audio stream
// //       const localStream = await navigator.mediaDevices.getUserMedia({ audio: true });

// //       // 2. Setup PeerConnection
// //       const pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);
// //       pcRef.current = pc;

// //       pc.onconnectionstatechange = () => {
// //         console.log(`[Voice] Connection state: ${pc.connectionState}`);
// //         if (pc.connectionState === 'connected') {
// //           setStatus('connected');
// //         } else if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
// //           stopCall();
// //         }
// //       };
      
// //       pc.onicecandidate = (event) => {
// //         if (event.candidate) {
// //           console.log(`[Voice] Found ICE candidate: ${event.candidate.type}`);
// //         }
// //       };

// //       // Add local microphone track to the connection to send to the server
// //       localStream.getTracks().forEach(track => {
// //         pc.addTrack(track, localStream);
// //       });
      
// //       // 3. Handle incoming audio track from the server (the echo)
// //       pc.ontrack = (event) => {
// //         console.log('[Voice] Received remote audio track from server.');
// //         if (audioPlayerRef.current && event.streams[0]) {
// //           audioPlayerRef.current.srcObject = event.streams[0];
// //         }
// //       };

// //       // 4. Setup WebSocket for signaling
// //       const ws = new WebSocket(VOICE_API_WS_URL);
// //       wsRef.current = ws;

// //       ws.onopen = async () => {
// //         console.log('[Voice] Signaling WebSocket open.');
// //         // Create and send the offer
// //         const offer = await pc.createOffer();
// //         await pc.setLocalDescription(offer);
// //         ws.send(JSON.stringify({ type: 'offer', sdp: pc.localDescription?.sdp }));
// //       };
      
// //       ws.onmessage = async (event) => {
// //         const data = JSON.parse(event.data);
// //         if (data.type === 'answer') {
// //           console.log('[Voice] Received answer from server.');
// //           await pc.setRemoteDescription(new RTCSessionDescription(data));
// //         }
// //       };

// //       ws.onerror = () => setStatus('error');
// //       ws.onclose = () => stopCall();

// //     } catch (err) {
// //       console.error('Failed to start call:', err);
// //       setStatus('error');
// //     }
// //   };

// //   const stopCall = () => {
// //     console.log('[Voice] Stopping call...');
// //     pcRef.current?.close();
// //     wsRef.current?.close();
// //     pcRef.current = null;
// //     wsRef.current = null;
// //     setStatus('disconnected');
// //     // Stop microphone track
// //     if (audioPlayerRef.current && audioPlayerRef.current.srcObject) {
// //       const stream = audioPlayerRef.current.srcObject as MediaStream;
// //       stream.getTracks().forEach(track => track.stop());
// //       audioPlayerRef.current.srcObject = null;
// //     }
// //   };

// //   // Cleanup on component unmount
// //   useEffect(() => {
// //     return () => {
// //       stopCall();
// //     };
// //   }, []);

// //   return (
// //     <div className="p-4 border rounded-lg bg-card text-card-foreground">
// //       <h3 className="text-lg font-semibold mb-2">Voice Echo Test</h3>
// //       <div className="flex items-center space-x-4">
// //         <Button
// //           onClick={status === 'disconnected' ? startCall : stopCall}
// //           disabled={status === 'connecting'}
// //         >
// //           {status === 'disconnected' && 'Start Call'}
// //           {status === 'connecting' && 'Connecting...'}
// //           {status === 'connected' && 'Stop Call'}
// //           {status === 'error' && 'Start Call'}
// //         </Button>
// //         <div className="flex items-center space-x-2">
// //           <span className={`h-3 w-3 rounded-full ${
// //             status === 'connected' ? 'bg-green-500' :
// //             status === 'connecting' ? 'bg-yellow-500 animate-pulse' :
// //             'bg-red-500'
// //           }`}></span>
// //           <span className="capitalize">{status}</span>
// //         </div>
// //       </div>
// //       <div className="mt-4">
// //         <p className="text-sm text-muted-foreground">
// //           Click "Start Call" and allow microphone access. You should hear your own voice echoed back to you.
// //         </p>
// //         <audio ref={audioPlayerRef} autoPlay controls className="w-full mt-2" />
// //       </div>
// //     </div>
// //   );
// // };