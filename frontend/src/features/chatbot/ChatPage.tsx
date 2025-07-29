import { memo } from 'react';
import { Button } from '@/components/ui/button';
import { ChatInput } from './components/ChatInput';
import { ChatWindow } from './components/ChatWindow';
import { ConferenceRoom } from './components/ConferenceRoom';
import { useChat } from './hooks/useChat';

export const ChatPage = memo(function ChatPage() {
  const { 
    messages, 
    input, 
    status, 
    isLoading, 
    connectionError,
    handleInputChange, 
    handleSubmit, 
    reconnect 
  } = useChat();

  return (
    <div className="flex h-full flex-col">
      {/* The ChatWindow grows to fill available space and is scrollable. */}
      <div className="flex-1 overflow-y-auto">
        <ChatWindow messages={messages} isLoading={isLoading} />
      </div>

      {/* The footer area is a fixed height and never shrinks. */}
      <div className="shrink-0 border-t border-neutral-800">
        {/* Connection Status Indicator */}
        {status !== 'connected' && (
          <div className={`p-3 text-center text-sm ${
            status === 'error' 
              ? 'bg-red-900/50 text-red-300' 
              : 'bg-yellow-900/50 text-yellow-300'
          }`}>
            <div className="font-medium">
              {status === 'connecting' && 'Connecting to assistant...'}
              {status === 'error' && 'Connection Failed'}
              {status === 'disconnected' && 'Disconnected from assistant'}
            </div>
            {connectionError && (
              <div className="mt-1 text-xs opacity-90">
                {connectionError}
              </div>
            )}
            {status === 'error' && (
              <Button 
                onClick={reconnect} 
                variant="outline" 
                size="sm" 
                className="mt-2 h-8 border-red-400 text-red-300 hover:bg-red-900/30 hover:text-red-200"
              >
                Try Again
              </Button>
            )}
            {status === 'connecting' && (
              <div className="mt-2 text-xs opacity-75">
                This may take a few moments on mobile networks
              </div>
            )}
          </div>
        )}
        <ChatInput
          key={`chat-input-${status}-${isLoading}`} // Force re-render when status changes
          input={input}
          handleInputChange={handleInputChange}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
          disabled={status !== 'connected'}
        />
        <div className="p-4 border-t border-neutral-800">
          <ConferenceRoom />
        </div>
      </div>
    </div>
  );
});
// import { memo } from 'react';
// import { Button } from '@/components/ui/button';
// import { ChatInput } from './components/ChatInput';
// import { ChatWindow } from './components/ChatWindow';
// import { ConferenceRoom } from './components/ConferenceRoom';
// import { useChat } from './hooks/useChat';

// export const ChatPage = memo(function ChatPage() {
//   const { 
//     messages, 
//     input, 
//     status, 
//     isLoading, 
//     handleInputChange, 
//     handleSubmit, 
//     reconnect 
//   } = useChat();

//   return (
//     <div className="flex h-full flex-col">
//       {/* The ChatWindow grows to fill available space and is scrollable. */}
//       <div className="flex-1 overflow-y-auto">
//         <ChatWindow messages={messages} isLoading={isLoading} />
//       </div>

//       {/* The footer area is a fixed height and never shrinks. */}
//       <div className="shrink-0 border-t border-neutral-800">
//         {/* Connection Status Indicator */}
//         {status !== 'connected' && (
//           <div className={`p-2 text-center text-xs ${
//             status === 'error' 
//               ? 'bg-red-900/50 text-red-300' 
//               : 'bg-yellow-900/50 text-yellow-300'
//           }`}>
//             {status === 'connecting' ? 'Connecting to assistant...' : 'Connection failed.'}
//             {status === 'error' && (
//               <Button 
//                 onClick={reconnect} 
//                 variant="link" 
//                 size="sm" 
//                 className="ml-2 h-auto p-0 text-white underline"
//               >
//                 Retry
//               </Button>
//             )}
//           </div>
//         )}
//         <ChatInput
//           input={input}
//           handleInputChange={handleInputChange}
//           handleSubmit={handleSubmit}
//           isLoading={isLoading}
//           disabled={status !== 'connected'}
//         />
//         <div className="p-4 border-t border-neutral-800">
//           <ConferenceRoom />
//         </div>
//       </div>
//     </div>
//   );
// });
// // import { Button } from '@/components/ui/button';
// // import { ChatInput } from './components/ChatInput';
// // import { ChatWindow } from './components/ChatWindow';
// // import { ConferenceRoom } from './components/ConferenceRoom';
// // import { useChat } from './hooks/useChat';

// // export function ChatPage() {
// //   const { messages, input, status, isLoading, handleInputChange, handleSubmit, reconnect } = useChat();

// //   return (
// //     // This structure is CRITICAL for the mobile keyboard to work.
// //     // <div className="flex h-full flex-col bg-neutral-900">
// //     <div className="flex h-full flex-col">
// //       {/* The ChatWindow grows to fill available space and is scrollable. */}
// //       <div className="flex-1 overflow-y-auto">
// //         <ChatWindow messages={messages} isLoading={isLoading} />
// //       </div>

// //       {/* The footer area is a fixed height and never shrinks. */}
// //       <div className="shrink-0 border-t border-neutral-800">
// //         {/* Connection Status Indicator */}
// //         {status !== 'connected' && (
// //           <div className={`p-2 text-center text-xs ${status === 'error' ? 'bg-red-900/50 text-red-300' : 'bg-yellow-900/50 text-yellow-300'}`}>
// //             {status === 'connecting' ? 'Connecting to assistant...' : 'Connection failed.'}
// //             {status === 'error' && (
// //               <Button onClick={reconnect} variant="link" size="sm" className="ml-2 h-auto p-0 text-white underline">Retry</Button>
// //             )}
// //           </div>
// //         )}
// //         <ChatInput
// //           input={input}
// //           handleInputChange={handleInputChange}
// //           handleSubmit={handleSubmit}
// //           isLoading={isLoading}
// //           disabled={status !== 'connected'}
// //         />
// //         <div className="p-4 border-t border-neutral-800">
// //           <ConferenceRoom />
// //         </div>
// //       </div>
// //     </div>
// //   );
// // }
// // // import { Button } from '@/components/ui/button';
// // // import { ChatInput } from './components/ChatInput';
// // // import { ChatWindow } from './components/ChatWindow';
// // // import { ConferenceRoom } from './components/ConferenceRoom';
// // // import { useChat } from './hooks/useChat';

// // // export function ChatPage() {
// // //   const { messages, input, status, isLoading, handleInputChange, handleSubmit, reconnect } = useChat();

// // //   return (
// // //     // This component MUST be a flex container that fills the height provided by its parent (App.tsx)
// // //     <div className="flex h-full flex-col">
// // //       {/* The ChatWindow takes up all available space and becomes scrollable */}
// // //       <div className="flex-1 overflow-y-auto">
// // //         <ChatWindow messages={messages} isLoading={isLoading} />
// // //       </div>

      
// // //       {/* This container will not grow or shrink, staying at the bottom */}
// // //       <div className="shrink-0 border-t border-neutral-800">
// // //         {/* Connection Status Indicator */}
// // //         {status !== 'connected' && (
// // //           <div className={`p-2 text-center text-xs ${status === 'error' ? 'bg-red-900/50 text-red-300' : 'bg-yellow-900/50 text-yellow-300'}`}>
// // //             {status === 'connecting' ? 'Connecting to assistant...' : 'Connection failed.'}
// // //             {status === 'error' && (
// // //               <Button onClick={reconnect} variant="link" size="sm" className="ml-2 h-auto p-0 text-white underline">Retry</Button>
// // //             )}
// // //           </div>
// // //         )}
// // //          <ChatInput
// // //           input={input}
// // //           handleInputChange={handleInputChange}
// // //           handleSubmit={handleSubmit}
// // //           isLoading={isLoading}
// // //           disabled={status !== 'connected'}
// // //         />
// // //         <div className="p-4 border-t border-neutral-800">
// // //           <ConferenceRoom />
// // //         </div>
// // //       </div>
// // //     </div>
// // //   );
// // // }
// // // import { ChatInput } from './components/ChatInput';
// // // import { ChatWindow } from './components/ChatWindow';
// // // import { ConferenceRoom } from './components/ConferenceRoom';
// // // // import { VoiceEchoTest } from './components/VoiceEchoTest';

// // // import { useChat } from './hooks/useChat';

// // // export function ChatPage() {
// // //   const { 
// // //     messages, 
// // //     input, 
// // //     status,
// // //     isLoading, 
// // //     handleInputChange, 
// // //     handleSubmit,
// // //     reconnect 
// // //   } = useChat();

// // //   return (
// // //     <div className="flex h-full flex-col">
// // //       <ChatWindow messages={messages} isLoading={isLoading} />
      
// // //       {/* Connection status indicator */}
// // //       {status === 'error' && (
// // //         <div className="p-4 text-center bg-red-50 border-t border-red-200">
// // //           <p className="text-sm text-red-600 mb-2">
// // //             Connection failed. Unable to connect to the chat server.
// // //           </p>
// // //           <button 
// // //             onClick={reconnect}
// // //             className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
// // //           >
// // //             Retry Connection
// // //           </button>
// // //         </div>
// // //       )}
      
// // //       {status === 'connecting' && (
// // //         <div className="p-4 text-center bg-yellow-50 border-t border-yellow-200">
// // //           <p className="text-sm text-yellow-600">
// // //             Connecting to chat server...
// // //           </p>
// // //         </div>
// // //       )}
      
// // //       <div className="border-t">
// // //         <ChatInput
// // //           input={input}
// // //           handleInputChange={handleInputChange}
// // //           handleSubmit={handleSubmit}
// // //           isLoading={isLoading}
// // //           disabled={status !== 'connected'}
// // //         />
// // //       </div>
// // //       <div className="p-4 border-t bg-background">
// // //     <ConferenceRoom />
// // //       </div>

// // //        {/* <div className="p-4 border-t bg-background">
// // //             <VoiceEchoTest />
// // //         </div> */}
// // //     </div>
// // //   );
// // // }
// // // // import { ChatInput } from './components/ChatInput';
// // // // import { ChatWindow } from './components/ChatWindow';
// // // // import { useChat } from './hooks/useChat';

// // // // export function ChatPage() {
// // // //   const { messages, input, isLoading, handleInputChange, handleSubmit, error } = useChat();

// // // //   return (
// // // //     <div className="flex h-full flex-col">
// // // //       <ChatWindow messages={messages} isLoading={isLoading} />
// // // //       {error && <p className="p-4 text-center text-sm text-red-500">{error}</p>}
// // // //       <div className="border-t">
// // // //         <ChatInput
// // // //           input={input}
// // // //           handleInputChange={handleInputChange}
// // // //           handleSubmit={handleSubmit}
// // // //           isLoading={isLoading}
// // // //         />
// // // //       </div>
// // // //     </div>
// // // //   );
// // // // }