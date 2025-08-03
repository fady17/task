import { useState } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useRoomContext,
  useConnectionState,
} from '@livekit/components-react';
import { ConnectionState } from 'livekit-client';
import { Button } from '@/components/ui/button';
import { LIVEKIT_CONFIG } from '@/config';
import { Mic, PhoneOff, Loader2 } from 'lucide-react'; // Using lucide-react for icons

// These constants must be consistent with the Pipecat agent's configuration.
const AI_VOICE_ROOM_NAME = "ai-voice-room";
// In a real application, the user identity would come from an authentication context.
const USER_IDENTITY = `user-voice-${Math.round(Math.random() * 1000)}`;

export const AIVoiceCall = () => {
  const [token, setToken] = useState<string | null>(null);
  const [inCall, setInCall] = useState(false);

  // This function is called when the user clicks the "Call" button.
  const joinCall = async () => {
    try {
      const response = await fetch(LIVEKIT_CONFIG.TOKEN_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: AI_VOICE_ROOM_NAME,
          identity: USER_IDENTITY,
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to fetch LiveKit token for voice call');
      }
      const data = await response.json();
      setToken(data.token);
      setInCall(true); // This will trigger the UI to render the <LiveKitRoom>
    } catch (error) {
      console.error("Error joining AI voice call:", error);
    }
  };

  // This function is called by LiveKitRoom's onDisconnected prop to reset the UI.
  const leaveCall = () => {
    setInCall(false);
    setToken(null);
  };

  // If we are not in a call, show the "Call AI" button.
  if (!inCall || !token) {
    return (
      <Button onClick={joinCall} className="w-full">
        <Mic className="mr-2 h-4 w-4" />
        Call AI Assistant
      </Button>
    );
  }

  // If we are in a call, render the LiveKitRoom provider.
  // This component handles the entire connection lifecycle for the voice call.
  return (
    <LiveKitRoom
      serverUrl={LIVEKIT_CONFIG.SERVER_URL}
      token={token}
      connect={true}
      audio={true} // We must enable audio to send the user's voice to the bot.
      video={false}
      onDisconnected={leaveCall} // When the call ends, reset our state.
    >
      {/* This component is essential: it finds and plays all incoming audio tracks (i.e., the bot's voice). */}
      <RoomAudioRenderer />
      {/* This child component displays the call status and hang-up button. */}
      <InCallUI />
    </LiveKitRoom>
  );
};

// A small UI component that can access the LiveKit context provided by <LiveKitRoom>.
const InCallUI = () => {
  const room = useRoomContext();
  const connectionState = useConnectionState(room);

  const getStatusMessage = () => {
    switch (connectionState) {
      case ConnectionState.Connecting: return 'Connecting...';
      case ConnectionState.Connected: return 'Connected to AI Assistant';
      case ConnectionState.Reconnecting: return 'Reconnecting...';
      case ConnectionState.Disconnected: return 'Disconnected';
      default: return 'Call Active';
    }
  };

  return (
    <div className="flex items-center justify-between w-full">
      <div className="flex items-center text-sm text-gray-400">
        {connectionState === ConnectionState.Connecting && (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        )}
        {getStatusMessage()}
      </div>
      <Button
        onClick={() => room.disconnect()}
        variant="destructive"
        size="sm"
      >
        <PhoneOff className="mr-2 h-4 w-4" />
        Hang Up
      </Button>
    </div>
  );
};
// import { useState } from 'react';
// // --- CORRECTED IMPORTS ---
// import { LiveKitRoom, RoomAudioRenderer } from '@livekit/components-react';
// import { useRoomContext, useConnectionState } from '@livekit/components-react';
// import { ConnectionState } from 'livekit-client'; // The actual enum is here
// // --- END OF CORRECTIONS ---

// import { Button } from '@/components/ui/button';
// import { LIVEKIT_CONFIG } from '@/config';
// import { Mic, PhoneOff, Loader2 } from 'lucide-react';

// const AI_VOICE_ROOM_NAME = "ai-voice-room";
// // In a real app, this would come from an authentication context
// const USER_IDENTITY = `user-${Math.round(Math.random() * 1000)}`;

// export const AIVoiceCall = () => {
//   const [token, setToken] = useState<string | null>(null);
//   const [inCall, setInCall] = useState(false);

//   const joinCall = async () => {
//     try {
//       const response = await fetch(LIVEKIT_CONFIG.TOKEN_ENDPOINT, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           room_name: AI_VOICE_ROOM_NAME,
//           identity: USER_IDENTITY,
//         }),
//       });
//       if (!response.ok) throw new Error('Failed to fetch LiveKit token');
//       const data = await response.json();
//       setToken(data.token);
//       setInCall(true);
//     } catch (error) {
//       console.error("Error joining AI call:", error);
//     }
//   };

//   const leaveCall = () => {
//     setInCall(false);
//     setToken(null);
//   };

//   if (!inCall || !token) {
//     return (
//       <Button onClick={joinCall} className="w-full">
//         <Mic className="mr-2 h-4 w-4" />
//         Call AI Assistant
//       </Button>
//     );
//   }

//   return (
//     <LiveKitRoom
//       serverUrl={LIVEKIT_CONFIG.SERVER_URL}
//       token={token}
//       connect={true}
//       audio={true}
//       video={false}
//       onDisconnected={leaveCall}
//       onError={(e) => console.error("LiveKit Room Error:", e)}
//     >
//       <RoomAudioRenderer />
//       <InCallUI />
//     </LiveKitRoom>
//   );
// };

// const InCallUI = () => {
//   // --- CORRECTED HOOK USAGE ---
//   // useRoomContext() returns the room object directly.
//   const room = useRoomContext();
//   // We pass the room object to useConnectionState.
//   const connectionState = useConnectionState(room);
//   // --- END OF CORRECTION ---

//   const getStatusMessage = () => {
//     // --- CORRECTED ENUM USAGE ---
//     // We now use the imported ConnectionState enum.
//     switch (connectionState) {
//       case ConnectionState.Connecting:
//         return 'Connecting...';
//       case ConnectionState.Connected:
//         return 'Connected to AI Assistant';
//       case ConnectionState.Reconnecting:
//         return 'Reconnecting...';
//       case ConnectionState.Disconnected:
//         return 'Disconnected';
//       default:
//         return 'Call Active';
//     }
//     // --- END OF CORRECTION ---
//   };

//   return (
//     <div className="flex items-center justify-between w-full">
//       <div className="flex items-center text-sm text-gray-400">
//         {connectionState === ConnectionState.Connecting && (
//           <Loader2 className="mr-2 h-4 w-4 animate-spin" />
//         )}
//         {getStatusMessage()}
//       </div>
//       <Button
//         onClick={() => room.disconnect()}
//         variant="destructive"
//         size="sm"
//       >
//         <PhoneOff className="mr-2 h-4 w-4" />
//         Hang Up
//       </Button>
//     </div>
//   );
// };