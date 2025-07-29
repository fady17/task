import { MessageSquare, Plus, Trash2, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
// import { useSessionContext } from '@/context/SessionContext'; // <-- Reverted to useSessionContext
import type { Session } from '@/types';
// import { useSession } from '../hooks/useSession';
import { useSessionContext } from '@/context/SessionContext';

interface SessionSidebarProps {
  onItemClick?: () => void; // For mobile - close sidebar when an action is taken
}

export function SessionSidebar({ onItemClick }: SessionSidebarProps) {
  // --- This now correctly gets its data from the SessionContext ---
  const {
    sessions,
    isLoading,
    currentSessionId,
    setCurrentSessionId,
    createNewSession,
    deleteSession,
  } = useSessionContext();

  const handleSessionClick = (sessionId: number) => {
    setCurrentSessionId(sessionId);
    onItemClick?.();
  };

  // The improved "New Chat" handler.
  // It now immediately creates a session, which is a good user experience.
  const handleNewChat = async () => {
    try {
      await createNewSession();
      onItemClick?.();
    } catch (error) {
      console.error('Failed to create new session from sidebar:', error);
    }
  };

  const truncateTitle = (title: string, maxLength: number = 25) => {
    return title.length > maxLength ? `${title.substring(0, maxLength)}...` : title;
  };

  const getRelativeTime = (timestamp: string) => {
    if (!timestamp) return 'Just now';
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.round((now.getTime() - date.getTime()) / 1000);
    const diffInMinutes = Math.round(diffInSeconds / 60);
    const diffInHours = Math.round(diffInMinutes / 60);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="flex h-full flex-col bg-black">
      <div className="p-4 border-b border-neutral-800">
        <Button 
          onClick={handleNewChat} 
          variant="outline"
          className="w-full h-10 border-neutral-700 text-white hover:bg-neutral-800 hover:text-white"
        >
          <Plus className="mr-2 h-4 w-4" /> 
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {isLoading && (
          <div className="space-y-2 px-2">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-[60px] w-full bg-neutral-800 rounded-lg" />)}
          </div>
        )}
        
        {!isLoading && sessions.length > 0 && (
          <div className="space-y-1">
            {sessions.map((session: Session) => (
              <div key={session.id} className="group relative">
                <Button
                  variant="ghost"
                  className={`w-full h-auto p-3 justify-start text-left rounded-lg transition-colors ${
                    currentSessionId === session.id 
                      ? 'bg-white text-black hover:bg-neutral-200' 
                      : 'text-white hover:bg-neutral-900'
                  }`}
                  onClick={() => handleSessionClick(session.id)}
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm truncate">{truncateTitle(session.title)}</p>
                    <div className={`flex items-center gap-1.5 text-xs mt-1 ${currentSessionId === session.id ? 'text-neutral-600' : 'text-neutral-500'}`}>
                      <Clock className="w-3 h-3" />
                      <span>{getRelativeTime(session.updated_at || session.created_at)}</span>
                    </div>
                  </div>
                </Button>
                
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className={`absolute top-1 right-1 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity ${
                        currentSessionId === session.id ? 'text-neutral-500 hover:text-red-600' : 'text-neutral-600 hover:text-red-400'
                      }`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Session</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to delete "{truncateTitle(session.title, 40)}"?
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => deleteSession(session.id)} className="bg-red-600 hover:bg-red-700">
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            ))}
          </div>
        )}
        
        {!isLoading && sessions.length === 0 && (
          <div className="text-center py-12 px-4 text-neutral-500">
            <MessageSquare className="w-10 h-10 mx-auto mb-2" />
            <h3 className="text-white font-medium">No Sessions</h3>
            <p className="text-sm">Start a chat to see your history.</p>
          </div>
        )}
      </div>
    </div>
  );
}
// import { MessageSquare, Plus, Trash2, Clock } from 'lucide-react';
// import { Button } from '@/components/ui/button';
// import { Skeleton } from '@/components/ui/skeleton';
// import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
// import { useSessionContext } from '../../../context/SessionContext';
// import type { Session } from '@/types';

// interface SessionSidebarProps {
//   onItemClick?: () => void; // For mobile - closes the sidebar after an action
// }

// export function SessionSidebar({ onItemClick }: SessionSidebarProps) {
//   const {
//     sessions,
//     isLoading,
//     currentSessionId,
//     setCurrentSessionId,
//     createNewSession,
//     deleteSession,
//   } = useSessionContext();

//   const handleSessionClick = (sessionId: number) => {
//     setCurrentSessionId(sessionId);
//     onItemClick?.();
//   };

//   // Fixed: Now actually creates a new session immediately
//   const handleNewChat = async () => {
//     try {
//       const newSession = await createNewSession();
//       if (newSession) {
//         // The createNewSession function already sets the currentSessionId
//         // so we don't need to call setCurrentSessionId here
//         onItemClick?.();
//       }
//     } catch (error) {
//       console.error('Failed to create new session:', error);
//     }
//   };

//   const truncateTitle = (title: string, maxLength: number = 25) => {
//     return title.length > maxLength ? `${title.substring(0, maxLength)}...` : title;
//   };

//   const getRelativeTime = (timestamp: string) => {
//     if (!timestamp) return 'Just now';
//     const date = new Date(timestamp);
//     const now = new Date();
//     const diffInSeconds = Math.round((now.getTime() - date.getTime()) / 1000);
//     const diffInMinutes = Math.round(diffInSeconds / 60);
//     const diffInHours = Math.round(diffInMinutes / 60);

//     if (diffInSeconds < 60) return 'Just now';
//     if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
//     if (diffInHours < 24) return `${diffInHours}h ago`;
//     return date.toLocaleDateString();
//   };

//   return (
//     <div className="flex h-full flex-col bg-black">
//       <div className="p-4 border-b border-neutral-800">
//         <Button 
//           onClick={handleNewChat} 
//           variant="outline"
//           className="w-full h-10 border-neutral-700 text-white hover:bg-neutral-800 hover:text-white"
//         >
//           <Plus className="mr-2 h-4 w-4" /> 
//           New Chat
//         </Button>
//       </div>

//       <div className="flex-1 overflow-y-auto p-2">
//         {isLoading && (
//           <div className="space-y-2 px-2">
//             {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-[60px] w-full bg-neutral-800 rounded-lg" />)}
//           </div>
//         )}
        
//         {!isLoading && sessions.length > 0 && (
//           <div className="space-y-1">
//             {sessions.map((session: Session) => (
//               <div key={session.id} className="group relative">
//                 <Button
//                   variant="ghost"
//                   className={`w-full h-auto p-3 justify-start text-left rounded-lg transition-colors ${
//                     currentSessionId === session.id 
//                       ? 'bg-white text-black hover:bg-neutral-200' 
//                       : 'text-white hover:bg-neutral-900'
//                   }`}
//                   onClick={() => handleSessionClick(session.id)}
//                 >
//                   <div className="flex-1 min-w-0">
//                     <p className="font-semibold text-sm truncate">{truncateTitle(session.title)}</p>
//                     <div className={`flex items-center gap-1.5 text-xs mt-1 ${currentSessionId === session.id ? 'text-neutral-600' : 'text-neutral-500'}`}>
//                       <Clock className="w-3 h-3" />
//                       <span>{getRelativeTime(session.updated_at || session.created_at)}</span>
//                     </div>
//                   </div>
//                 </Button>
                
//                 <AlertDialog>
//                   <AlertDialogTrigger asChild>
//                     <Button
//                       variant="ghost"
//                       size="icon"
//                       className={`absolute top-1 right-1 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity ${
//                         currentSessionId === session.id ? 'text-neutral-500 hover:text-red-600' : 'text-neutral-600 hover:text-red-400'
//                       }`}
//                     >
//                       <Trash2 className="h-4 w-4" />
//                     </Button>
//                   </AlertDialogTrigger>
//                   <AlertDialogContent>
//                     <AlertDialogHeader>
//                       <AlertDialogTitle>Delete Session</AlertDialogTitle>
//                       <AlertDialogDescription>
//                         Are you sure you want to delete "{truncateTitle(session.title, 40)}"?
//                       </AlertDialogDescription>
//                     </AlertDialogHeader>
//                     <AlertDialogFooter>
//                       <AlertDialogCancel>Cancel</AlertDialogCancel>
//                       <AlertDialogAction onClick={() => deleteSession(session.id)} className="bg-red-600 hover:bg-red-700">
//                         Delete
//                       </AlertDialogAction>
//                     </AlertDialogFooter>
//                   </AlertDialogContent>
//                 </AlertDialog>
//               </div>
//             ))}
//           </div>
//         )}
        
//         {!isLoading && sessions.length === 0 && (
//           <div className="text-center py-12 px-4 text-neutral-500">
//             <MessageSquare className="w-10 h-10 mx-auto mb-2" />
//             <h3 className="text-white font-medium">No Sessions</h3>
//             <p className="text-sm">Start a chat to see your history.</p>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }