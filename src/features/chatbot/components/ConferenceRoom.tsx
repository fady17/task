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