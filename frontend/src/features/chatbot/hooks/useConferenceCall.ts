import { useState, useRef, useEffect, useCallback } from 'react';
import { PEER_CONNECTION_CONFIG, API_CONFIG } from '@/config';

export type CallStatus = 'disconnected' | 'connecting' | 'connected' | 'failed';
export interface RemoteParticipant {
  id: string;
  stream: MediaStream;
}

// Define the WebSocket URL for conference calls
const CONFERENCE_WEBSOCKET_URL = API_CONFIG.WEBSOCKET_URL.replace('/ai/ws', '/conference/ws');

export const useConferenceCall = () => {
  const [status, setStatus] = useState<CallStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [remoteParticipants, setRemoteParticipants] = useState<RemoteParticipant[]>([]);
  
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const roomDetailsRef = useRef<{ roomId: string, userId: string } | null>(null);

  const cleanup = useCallback(() => {
    console.log('[Conference] Cleanup called.');
    pcRef.current?.close();
    wsRef.current?.close();
    localStreamRef.current?.getTracks().forEach(track => track.stop());
    pcRef.current = null;
    wsRef.current = null;
    localStreamRef.current = null;
    setStatus('disconnected');
    setRemoteParticipants([]);
  }, []);

  const joinRoom = useCallback(async (roomId: string, userId: string) => {
    if (pcRef.current) return;
    
    roomDetailsRef.current = { roomId, userId };
    setStatus('connecting');
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      localStreamRef.current = stream;

      const pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);
      pcRef.current = pc;
      
      pc.onconnectionstatechange = () => {
        console.log(`[Conference] Peer Connection State: ${pc.connectionState}`);
        if (pc.connectionState === 'connected') setStatus('connected');
        if (pc.connectionState === 'failed') { setStatus('failed'); setError('Connection failed.'); }
        if (pc.connectionState === 'disconnected' || pc.connectionState === 'closed') cleanup();
      };
      
      stream.getTracks().forEach(track => pc.addTrack(track, stream));

      pc.ontrack = (event) => {
        console.log('[Conference] Remote track received!');
        const remoteStream = event.streams[0];
        setRemoteParticipants(prev => {
          if (!prev.some(p => p.id === remoteStream.id)) {
            return [...prev, { id: remoteStream.id, stream: remoteStream }];
          }
          return prev;
        });
      };
      
      // Fixed: Use the correct WebSocket URL
      const ws = new WebSocket(`${CONFERENCE_WEBSOCKET_URL}/${roomId}/${userId}`);
      wsRef.current = ws;

      ws.onopen = async () => {
        console.log('[Conference] Signaling WebSocket open.');
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        ws.send(JSON.stringify({ type: 'offer', sdp: pc.localDescription?.sdp }));
      };

      ws.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        const currentPc = pcRef.current;
        if (!currentPc || currentPc.signalingState === 'closed') return;

        if (data.type === 'answer') {
          console.log('[Conference] Received answer.');
          await currentPc.setRemoteDescription(new RTCSessionDescription(data));
        } else if (data.type === 'new-peer') {
          console.log(`[Conference] New peer '${data.peer_id}' joined. Starting renegotiation...`);
          const offer = await currentPc.createOffer({ iceRestart: true });
          await currentPc.setLocalDescription(offer);

          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'offer', sdp: currentPc.localDescription?.sdp }));
          }
        } else if (data.type === 'peer-left') {
            console.log(`[Conference] Peer '${data.peer_id}' left. Refreshing connection.`);
            cleanup();
            setTimeout(() => {
                if(roomDetailsRef.current) {
                    joinRoom(roomDetailsRef.current.roomId, roomDetailsRef.current.userId);
                }
            }, 100);
        }
      };
      
      ws.onerror = () => { setStatus('failed'); setError('WebSocket connection failed.'); };
      ws.onclose = () => { if (status !== 'connected') cleanup(); };

    } catch (err: any) {
      console.error('[Conference] Failed to join room:', err);
      setError(err.message || 'Could not start call.');
      cleanup();
    }
  }, [cleanup, status]);

  useEffect(() => {
    return () => cleanup();
  }, [cleanup]);

  return { status, error, remoteParticipants, joinRoom, leaveRoom: cleanup };
};
// import { useConfig } from '@/context/ConfigContext';
// import { useState, useRef, useEffect, useCallback } from 'react';

// export type CallStatus = 'disconnected' | 'connecting' | 'connected' | 'failed';
// export interface RemoteParticipant {
//   id: string;
//   stream: MediaStream;
// }

// // const WEBSOCKET_URL = 'ws://localhost:8001/ws';
// // const PEER_CONNECTION_CONFIG: RTCConfiguration = {
// //   iceServers: [{ urls: 'turn:127.0.0.1:3478', username: 'demo', credential: 'password' }],
// // };
// // const YOUR_COMPUTER_IP = '192.168.1.3'; // <-- REPLACE THIS WITH YOUR ACTUAL IP

// // const WEBSOCKET_URL = `ws://${YOUR_COMPUTER_IP}:8001/ws`;

// // const PEER_CONNECTION_CONFIG: RTCConfiguration = {
// //   iceServers: [{
// //     // The browser on another device needs to reach the TURN server at your computer's IP
// //     urls: `turn:${YOUR_COMPUTER_IP}:3478`,
// //     username: 'demo',
// //     credential: 'password'
// //   }],
// // };


// export const useConferenceCall = () => {
//   const config = useConfig();
//    const WEBSOCKET_URL = `ws://${config.api_host}:${config.voice_api_port}/ws`;
//   const PEER_CONNECTION_CONFIG: RTCConfiguration = {
//     iceServers: [config.turn_server],
//   };
//   const [status, setStatus] = useState<CallStatus>('disconnected');
//   const [error, setError] = useState<string | null>(null);
//   const [remoteParticipants, setRemoteParticipants] = useState<RemoteParticipant[]>([]);
  
//   const pcRef = useRef<RTCPeerConnection | null>(null);
//   const localStreamRef = useRef<MediaStream | null>(null);
//   const wsRef = useRef<WebSocket | null>(null);

//   const cleanup = useCallback(() => {
//     console.log('[Conference] Cleanup called.');
//     pcRef.current?.close();
//     wsRef.current?.close();
//     localStreamRef.current?.getTracks().forEach(track => track.stop());
//     pcRef.current = null;
//     wsRef.current = null;
//     localStreamRef.current = null;
//     setStatus('disconnected');
//     setRemoteParticipants([]);
//   }, []);

//   const joinRoom = useCallback(async (roomId: string, userId: string) => {
//     if (pcRef.current) return;
    
//     console.log(`[Conference] Joining room '${roomId}' as '${userId}'`);
//     setStatus('connecting');
//     setError(null);

//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       localStreamRef.current = stream;

//       // const pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);
//       const pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);
//       pcRef.current = pc;
      
//       pc.onconnectionstatechange = () => {
//         console.log(`[Conference] Peer Connection State: ${pc.connectionState}`);
//         if (pc.connectionState === 'connected') setStatus('connected');
//         if (pc.connectionState === 'failed') { setStatus('failed'); setError('Connection failed.'); }
//         if (pc.connectionState === 'disconnected' || pc.connectionState === 'closed') cleanup();
//       };
      
//       stream.getTracks().forEach(track => pc.addTrack(track, stream));

//       pc.ontrack = (event) => {
//         console.log('[Conference] Remote track received!');
//         const remoteStream = event.streams[0];
//         setRemoteParticipants(prev => {
//           if (!prev.some(p => p.id === remoteStream.id)) {
//             return [...prev, { id: remoteStream.id, stream: remoteStream }];
//           }
//           return prev;
//         });
//       };
      
//       const ws = new WebSocket(`${WEBSOCKET_URL}/${roomId}/${userId}`);
//       // const ws = new WebSocket(`${VOICE_CONFIG.WEBSOCKET_URL}/${roomId}/${userId}`);
//       wsRef.current = ws;

//       ws.onopen = async () => {
//         console.log('[Conference] Signaling WebSocket open.');
//         const offer = await pc.createOffer();
//         await pc.setLocalDescription(offer);
//         ws.send(JSON.stringify({ type: 'offer', sdp: pc.localDescription?.sdp }));
//       };

//       // --- SIMPLIFIED onmessage HANDLER ---
//       ws.onmessage = async (event) => {
//         const data = JSON.parse(event.data);
//         const currentPc = pcRef.current;
//         if (!currentPc || currentPc.signalingState === 'closed') return;

//         if (data.type === 'answer') {
//           console.log('[Conference] Received answer.');
//           await currentPc.setRemoteDescription(new RTCSessionDescription(data));
//         } else if (data.type === 'new-peer') {
//           console.log(`[Conference] New peer '${data.peer_id}' joined. Renegotiating...`);
//           // A new user joined. We need to create a new offer to receive their track.
//           const offer = await currentPc.createOffer({ iceRestart: true });
//           await currentPc.setLocalDescription(offer);
//           ws.send(JSON.stringify({ type: 'offer', sdp: currentPc.localDescription?.sdp }));
//         }
//       };
      
//       ws.onerror = () => { setStatus('failed'); setError('WebSocket connection failed.'); };
//       ws.onclose = () => { if (status !== 'connected') cleanup(); };

//     } catch (err: any) {
//       console.error('[Conference] Failed to join room:', err);
//       setError(err.message || 'Could not start call.');
//       cleanup();
//     }
//   }, [cleanup, status]);

//   useEffect(() => {
//     return () => cleanup();
//   }, [cleanup]);

//   return { status, error, remoteParticipants, joinRoom, leaveRoom: cleanup };
// };