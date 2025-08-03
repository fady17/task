// // frontend/src/features/chatbot/components/VoiceConferenceRoom.tsx
// import { useState, useEffect } from 'react';
// import { LiveKitRoom, VideoConference, ControlBar, useConnectionState } from '@livekit/components-react';
// import '@livekit/components-styles';
// import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { Badge } from '@/components/ui/badge';
// import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
// import { ConnectionState } from 'livekit-client';

// // API endpoints
// const TOKEN_ENDPOINT = 'http://localhost:8000/api/livekit/token';
// const VOICE_BOT_ENDPOINT = 'http://localhost:8000/ai/voice';
// const LIVEKIT_URL = 'ws://localhost:7880';

// interface VoiceBotStatus {
//   running: boolean;
//   room_name?: string;
// }

// export const ConferenceRoom = () => {
//   const [token, setToken] = useState<string | null>(null);
//   const [roomName, setRoomName] = useState('ai-voice-chat');
//   const [userName, setUserName] = useState(`user-${Math.round(Math.random() * 1000)}`);
//   const [voiceBotStatus, setVoiceBotStatus] = useState<VoiceBotStatus>({ running: false });
//   const [connecting, setConnecting] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   // Check voice bot status
//   const checkVoiceBotStatus = async () => {
//     try {
//       const response = await fetch(`${VOICE_BOT_ENDPOINT}/status`);
//       if (response.ok) {
//         const status = await response.json();
//         setVoiceBotStatus(status);
//       }
//     } catch (e) {
//       console.error('Failed to check voice bot status:', e);
//     }
//   };

//   // Start voice bot
//   const startVoiceBot = async () => {
//     try {
//       setConnecting(true);
//       const response = await fetch(`${VOICE_BOT_ENDPOINT}/connect`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ 
//           room_name: roomName,
//           session_id: `voice-session-${Date.now()}`
//         }),
//       });
      
//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || 'Failed to start voice bot');
//       }
      
//       await checkVoiceBotStatus();
//       setError(null);
//     } catch (e) {
//       setError(e instanceof Error ? e.message : 'Unknown error starting voice bot');
//       console.error('Failed to start voice bot:', e);
//     } finally {
//       setConnecting(false);
//     }
//   };

//   // Stop voice bot
//   const stopVoiceBot = async () => {
//     try {
//       setConnecting(true);
//       const response = await fetch(`${VOICE_BOT_ENDPOINT}/disconnect`, {
//         method: 'POST',
//       });
      
//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || 'Failed to stop voice bot');
//       }
      
//       await checkVoiceBotStatus();
//       setError(null);
//     } catch (e) {
//       setError(e instanceof Error ? e.message : 'Unknown error stopping voice bot');
//       console.error('Failed to stop voice bot:', e);
//     } finally {
//       setConnecting(false);
//     }
//   };

//   // Join room as user
//   const joinRoom = async () => {
//     try {
//       setConnecting(true);
//       const response = await fetch(TOKEN_ENDPOINT, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ room_name: roomName, identity: userName }),
//       });
      
//       if (!response.ok) {
//         throw new Error('Failed to get room token');
//       }
      
//       const data = await response.json();
//       setToken(data.token);
//       setError(null);
//     } catch (e) {
//       setError(e instanceof Error ? e.message : 'Unknown error joining room');
//       console.error('Failed to join room:', e);
//     } finally {
//       setConnecting(false);
//     }
//   };

//   // Check status on component mount
//   useEffect(() => {
//     checkVoiceBotStatus();
//   }, []);

//   // Connection status component
//   const ConnectionStatus = () => {
//     const connectionState = useConnectionState();
    
//     const getStatusColor = () => {
//       switch (connectionState) {
//         case ConnectionState.Connected: return 'bg-green-500';
//         case ConnectionState.Connecting: return 'bg-yellow-500';
//         case ConnectionState.Disconnected: return 'bg-red-500';
//         default: return 'bg-gray-500';
//       }
//     };

//     return (
//       <Badge className={`${getStatusColor()} text-white`}>
//         {connectionState}
//       </Badge>
//     );
//   };

//   if (!token) {
//     return (
//       <div className="max-w-2xl mx-auto p-6 space-y-6">
//         <Card>
//           <CardHeader>
//             <CardTitle className="flex items-center gap-2">
//               <Volume2 className="h-5 w-5" />
//               Voice AI Assistant
//             </CardTitle>
//           </CardHeader>
//           <CardContent className="space-y-4">
//             {error && (
//               <div className="p-3 bg-red-100 border border-red-300 rounded-md text-red-700">
//                 {error}
//               </div>
//             )}
            
//             <div className="flex items-center gap-2">
//               <span>Voice Bot Status:</span>
//               <Badge className={voiceBotStatus.running ? 'bg-green-500' : 'bg-gray-500'}>
//                 {voiceBotStatus.running ? 'Running' : 'Stopped'}
//               </Badge>
//               {voiceBotStatus.room_name && (
//                 <span className="text-sm text-gray-600">
//                   in {voiceBotStatus.room_name}
//                 </span>
//               )}
//             </div>

//             <div className="space-y-3">
//               <Input 
//                 value={roomName} 
//                 onChange={(e) => setRoomName(e.target.value)} 
//                 placeholder="Room Name" 
//                 disabled={connecting}
//               />
//               <Input 
//                 value={userName} 
//                 onChange={(e) => setUserName(e.target.value)} 
//                 placeholder="Your Name" 
//                 disabled={connecting}
//               />
//             </div>

//             <div className="flex gap-2">
//               <Button 
//                 onClick={startVoiceBot} 
//                 disabled={connecting || voiceBotStatus.running}
//                 className="flex-1"
//               >
//                 {connecting ? 'Starting...' : 'Start Voice Bot'}
//               </Button>
              
//               <Button 
//                 onClick={stopVoiceBot} 
//                 disabled={connecting || !voiceBotStatus.running}
//                 variant="outline"
//                 className="flex-1"
//               >
//                 {connecting ? 'Stopping...' : 'Stop Voice Bot'}
//               </Button>
//             </div>

//             <Button 
//               onClick={joinRoom} 
//               disabled={connecting || !voiceBotStatus.running}
//               className="w-full"
//               size="lg"
//             >
//               <Mic className="mr-2 h-4 w-4" />
//               {connecting ? 'Joining...' : 'Join Voice Chat'}
//             </Button>

//             <div className="text-sm text-gray-600 space-y-1">
//               <p><strong>Instructions:</strong></p>
//               <ol className="list-decimal list-inside space-y-1 ml-2">
//                 <li>First, start the voice bot</li>
//                 <li>Then join the voice chat</li>
//                 <li>Speak naturally - the AI will respond with voice</li>
//                 <li>You can manage your todos through voice commands</li>
//               </ol>
//             </div>
//           </CardContent>
//         </Card>
//       </div>
//     );
//   }

//   return (
//     <div className="h-screen flex flex-col">
//       <div className="p-4 bg-gray-100 border-b flex justify-between items-center">
//         <div className="flex items-center gap-4">
//           <h2 className="text-lg font-semibold">Voice AI Chat - {roomName}</h2>
//           <ConnectionStatus />
//         </div>
//         <div className="flex gap-2">
//           <Button 
//             onClick={() => checkVoiceBotStatus()} 
//             variant="outline" 
//             size="sm"
//           >
//             Refresh Status
//           </Button>
//           <Button 
//             onClick={() => setToken(null)} 
//             variant="outline" 
//             size="sm"
//           >
//             Leave Room
//           </Button>
//         </div>
//       </div>

//       <div className="flex-1">
//         <LiveKitRoom
//           serverUrl={LIVEKIT_URL}
//           token={token}
//           connect={true}
//           video={false} // Voice-only interaction
//           audio={true}
//           onDisconnected={() => setToken(null)}
//         >
//           <VideoConference />
//           <ControlBar />
//         </LiveKitRoom>
//       </div>
//     </div>
//   );
// };

import { useState } from 'react';
import { LiveKitRoom, VideoConference, ControlBar } from '@livekit/components-react';
import '@livekit/components-styles';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

// The endpoint on our OWN API that generates the token
const TOKEN_ENDPOINT = 'http://localhost:8000/api/livekit/token';
// The URL of the LiveKit server itself
const LIVEKIT_URL = 'ws://localhost:7880';

export const ConferenceRoom = () => {
  const [token, setToken] = useState<string | null>(null);
  const [roomName, setRoomName] = useState('test-room');
  const [userName, setUserName] = useState(`user-${Math.round(Math.random() * 1000)}`);

  const joinRoom = async () => {
    try {
      const response = await fetch(TOKEN_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_name: roomName, identity: userName }),
      });
      const data = await response.json();
      setToken(data.token);
    } catch (e) {
      console.error(e);
    }
  };

  if (!token) {
    return (
      <div className="flex items-center space-x-2 p-4">
        <Input value={roomName} onChange={(e) => setRoomName(e.target.value)} placeholder="Room Name" />
        <Input value={userName} onChange={(e) => setUserName(e.target.value)} placeholder="Your Name" />
        <Button onClick={joinRoom}>Join Room</Button>
      </div>
    );
  }

  return (
    <LiveKitRoom
      serverUrl={LIVEKIT_URL}
      token={token}
      connect={true}
      video={false} // We are only doing audio for now
      audio={true}
      onDisconnected={() => setToken(null)}
    >
      {/* This component provides a pre-built grid of participants */}
      <VideoConference />
      {/* This component provides mute/unmute, etc. controls */}
      <ControlBar />
    </LiveKitRoom>
  );
};
// import React, { useState, useCallback } from 'react';
// import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { useConferenceCall, type RemoteParticipant } from '../hooks/useConferenceCall';

// // A sub-component to handle playing a remote participant's audio
// const RemoteAudioPlayer: React.FC<{ participant: RemoteParticipant }> = ({ participant }) => {
//   // A callback ref is a reliable way to get access to the DOM node.
//   const audioRef = useCallback((audioElement: HTMLAudioElement | null) => {
//     if (audioElement) {
//       console.log(`[RemoteAudio] Audio element for participant ${participant.id} is ready.`);
//       if (participant.stream) {
//         console.log(`[RemoteAudio] Attaching stream ${participant.stream.id} to audio element.`);
//         audioElement.srcObject = participant.stream;
//         audioElement.play().catch(error => {
//           console.warn(`[RemoteAudio] Autoplay for stream ${participant.stream.id} was blocked.`, error);
//         });
//       } else {
//         console.warn(`[RemoteAudio] Audio element is ready, but participant ${participant.id} has no stream.`);
//       }
//     }
//   }, [participant]); // The ref callback will re-run if the participant object changes.

//   return (
//     <div className="p-2 border rounded-md bg-muted">
//       {/* --- FIX: Use participant.id instead of participant.userId --- */}
//       <p className="text-xs font-medium text-muted-foreground">Participant: {participant.id}</p>
//       <audio ref={audioRef} autoPlay controls className="w-full mt-1" />
//     </div>
//   );
// };


// export const ConferenceRoom: React.FC = () => {
//   // We use a default room name for simplicity in this demo.
//   const [roomId, setRoomId] = useState('general-conference');
//   // Generate a random, unique user ID for this browser session.
//   const [userId] = useState(`user-${Math.random().toString(36).substring(7)}`);
  
//   const { status, error, remoteParticipants, joinRoom, leaveRoom } = useConferenceCall();

//   const handleJoin = () => {
//     // We pass the static roomId and userId to the hook to initiate the call.
//     if (roomId && userId) {
//       joinRoom(roomId, userId);
//     }
//   };
  
//   // A boolean to easily check if we are in any active call state.
//   const inCall = status === 'connecting' || status === 'connected';

//   return (
//     <Card className="mt-4">
//       <CardHeader>
//         <CardTitle>Voice Conference Room</CardTitle>
//       </CardHeader>
//       <CardContent className="space-y-4">
//         {/* Conditional rendering: show the join form OR the in-call controls */}
//         {!inCall ? (
//           <div className="flex items-center space-x-2">
//             <Input 
//               placeholder="Room Name" 
//               value={roomId} 
//               onChange={(e) => setRoomId(e.target.value)} 
//             />
//             <Input 
//               placeholder="Your Name" 
//               value={userId} 
//               readOnly // The user ID is generated once and should not be changed.
//             />
//             <Button onClick={handleJoin}>Join Room</Button>
//           </div>
//         ) : (
//           <div className="flex items-center space-x-4">
//             <Button onClick={leaveRoom} variant="destructive">Leave Room</Button>
//             <div className="text-sm">
//               <p>Room: <span className="font-semibold">{roomId}</span></p>
//               <p>Status: <span className="font-semibold capitalize">{status}</span></p>
//             </div>
//           </div>
//         )}
        
//         {/* Display an error message if one exists */}
//         {error && <p className="text-red-500 text-sm font-medium">{error}</p>}
        
//         <div className="space-y-2">
//           <h4 className="font-semibold">Other Participants ({remoteParticipants.length})</h4>
//           {remoteParticipants.length === 0 && inCall && (
//             <p className="text-sm text-muted-foreground">Waiting for others to join...</p>
//           )}
//           {/* Dynamically render an audio player for each remote participant */}
//           {remoteParticipants.map(participant => (
//             <RemoteAudioPlayer key={participant.id} participant={participant} />
//           ))}
//         </div>
//       </CardContent>
//     </Card>
//   );
// };
// // import React, { useState, useCallback } from 'react';
// // import { Button } from '@/components/ui/button';
// // import { Input } from '@/components/ui/input';
// // import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// // import { useConferenceCall, type RemoteParticipant } from '../hooks/useConferenceCall';

// // // A sub-component to handle playing a remote participant's audio
// // const RemoteAudioPlayer: React.FC<{ participant: RemoteParticipant }> = ({ participant }) => {
// //    const audioRef = useCallback((audioElement: HTMLAudioElement | null) => {
// //     if (audioElement) {
// //       console.log(`[RemoteAudio] Audio element for participant ${participant.userId} is ready.`);
// //       if (participant.stream) {
// //         console.log(`[RemoteAudio] Attaching stream ${participant.stream.id} to audio element.`);
// //         audioElement.srcObject = participant.stream;

// //         // Attempt to play. This is crucial.
// //         audioElement.play().catch(error => {
// //           console.error(`[RemoteAudio] Autoplay was blocked for stream ${participant.stream.id}. User interaction may be required.`, error);
// //         });
// //       } else {
// //         console.warn(`[RemoteAudio] Audio element is ready, but participant ${participant.userId} has no stream.`);
// //       }
// //     }
// //   }, [participant]); // The ref callback will re-run if the participant object changes.

// //   return (
// //      <div className="p-2 border rounded-md">
// //       <p className="text-xs font-medium text-muted-foreground">Participant ID: {participant.userId}</p>
// //       {/* We add a unique key to the audio element to force React to re-mount it if the stream ID changes */}
// //       <audio key={participant.stream.id} ref={audioRef} autoPlay controls className="w-full" />
// //     </div>
// //   );
// // };

// // export const ConferenceRoom: React.FC = () => {
// //   const [roomId, setRoomId] = useState('general');
// //   const [userId, setUserId] = useState(`user-${Math.random().toString(36).substring(7)}`);
  
// //   const { status, error, remoteParticipants, joinRoom, leaveRoom } = useConferenceCall();

// //   const handleJoin = () => {
// //     if (roomId && userId) {
// //       joinRoom(roomId, userId);
// //     }
// //   };
  
// //   const inCall = status === 'connecting' || status === 'connected';

// //   return (
// //     <Card className="mt-4">
// //       <CardHeader>
// //         <CardTitle>Voice Conference Room</CardTitle>
// //       </CardHeader>
// //       <CardContent className="space-y-4">
// //         {!inCall ? (
// //           <div className="flex items-center space-x-2">
// //             <Input 
// //               placeholder="Room Name" 
// //               value={roomId} 
// //               onChange={(e) => setRoomId(e.target.value)} 
// //             />
// //             <Input 
// //               placeholder="Your Name" 
// //               value={userId} 
// //               onChange={(e) => setUserId(e.target.value)} 
// //             />
// //             <Button onClick={handleJoin}>Join Room</Button>
// //           </div>
// //         ) : (
// //           <div className="flex items-center space-x-4">
// //             <Button onClick={leaveRoom} variant="destructive">Leave Room</Button>
// //             <div className="text-sm">
// //               <p>Room: <span className="font-semibold">{roomId}</span></p>
// //               <p>Status: <span className="font-semibold">{status}</span></p>
// //             </div>
// //           </div>
// //         )}
        
// //         {error && <p className="text-red-500 text-sm">{error}</p>}
        
// //          <div className="space-y-2">
// //           <h4 className="font-semibold">Other Participants ({remoteParticipants.length})</h4>
// //           {remoteParticipants.length === 0 && inCall && (
// //             <p className="text-sm text-muted-foreground">Waiting for others to join...</p>
// //           )}
// //           {/* Change to map over the array */}
// //           {remoteParticipants.map(participant => (
// //             <RemoteAudioPlayer key={participant.stream.id} participant={participant} />
// //           ))}
// //         </div>
// //       </CardContent>
// //     </Card>
// //   );
// // };