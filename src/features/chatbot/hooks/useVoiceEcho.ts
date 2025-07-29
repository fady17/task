import { useState, useRef, useEffect, useCallback } from 'react';

// --- Type Definitions (Simplified) ---
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'failed';

// --- Configuration ---
const VOICE_API_WS_URL = 'ws://localhost:8001/ws';
const PEER_CONNECTION_CONFIG: RTCConfiguration = {
  iceServers: [{
    urls: 'turn:127.0.0.1:3478', // Using just TURN is the most robust for this setup
    username: 'demo',
    credential: 'password'
  }],
};

// --- The Custom Hook ---
export const useVoiceEcho = () => {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);

  // Use useCallback to ensure the cleanup function has a stable identity
  const cleanup = useCallback(() => {
    if (pcRef.current) {
      console.log('[Voice] Closing PeerConnection...');
      pcRef.current.close();
      pcRef.current = null;
    }
    if (localStreamRef.current) {
      console.log('[Voice] Stopping media tracks...');
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }
    setStatus('disconnected');
  }, []);
  
  const startCall = useCallback(async (audioPlayer: HTMLAudioElement | null) => {
    if (pcRef.current) {
      console.warn('[Voice] Call already in progress.');
      return;
    }

    console.log('[Voice] --- STARTING NEW CALL ---');
    setStatus('connecting');

    try {
      // 1. Get Microphone Stream
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      localStreamRef.current = stream;
      console.log('[Voice] Microphone access granted and stream captured.');

      // 2. Create and Configure PeerConnection
      const pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);
      pcRef.current = pc;

      // Add event listeners BEFORE doing anything else
      pc.onconnectionstatechange = () => {
        console.log(`[Voice] Peer Connection State: ${pc.connectionState}`);
        if (pc.connectionState === 'connected') {
          setStatus('connected');
        } else if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected' || pc.connectionState === 'closed') {
          cleanup();
        }
      };

      pc.oniceconnectionstatechange = () => {
        console.log(`[Voice] ICE Connection State: ${pc.iceConnectionState}`);
      };

      // 3. Add Local Tracks to the Connection
      // This is the CRITICAL step that sends the audio
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream);
        console.log(`[Voice] Added local audio track to be sent.`);
      });
      
      // 4. Handle Incoming (Echoed) Tracks
      pc.ontrack = (event) => {
        console.log('[Voice] SUCCESS: Remote (echoed) track received from server!');
        if (audioPlayer && event.streams[0]) {
          audioPlayer.srcObject = event.streams[0];
          audioPlayer.play().catch(e => console.warn('[Voice] Autoplay was blocked by browser.', e));
        }
      };
      
      // 5. Connect WebSocket for Signaling
      const ws = new WebSocket(VOICE_API_WS_URL);

      ws.onopen = async () => {
        console.log('[Voice] Signaling WebSocket open.');
        
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        
        console.log('[Voice] Sending offer to server...');
        ws.send(JSON.stringify({ type: 'offer', sdp: pc.localDescription?.sdp }));
      };

      ws.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'answer') {
          console.log('[Voice] Received answer from server.');
          if (pc.signalingState !== 'closed') {
            await pc.setRemoteDescription(new RTCSessionDescription(data));
          }
        }
      };

      ws.onerror = () => {
        console.error('[Voice] WebSocket error occurred.');
        setStatus('failed');
      };
      
      ws.onclose = () => {
        console.log('[Voice] WebSocket closed.');
      };

      // Link the PC cleanup to the WebSocket
      pc.oniceconnectionstatechange = () => {
        if(pc.iceConnectionState === 'disconnected' || pc.iceConnectionState === 'failed') {
            ws.close();
        }
      }

    } catch (err: any) {
      console.error('[Voice] Failed to start call:', err);
      setStatus('failed');
      cleanup();
    }
  }, [cleanup]);

  useEffect(() => {
    // This effect ensures cleanup is called when the component unmounts
    return () => cleanup();
  }, [cleanup]);

  return {
    status,
    startCall,
    stopCall: cleanup,
  };
};