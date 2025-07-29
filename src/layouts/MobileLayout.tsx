import { useState } from 'react';
import { MessageSquare, CheckSquare, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatPage } from '@/features/chatbot/ChatPage';
import { TodoPage } from '@/features/todos/TodoPage';
import { SessionSidebar } from '@/features/chatbot/components/SessionSidebar';

type MobileView = 'chat' | 'todos';

export function MobileLayout() {
  const [mobileView, setMobileView] = useState<MobileView>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <main className="flex h-[100dvh] w-screen flex-col bg-black text-white">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-neutral-800 px-4 z-20">
        <Button onClick={() => setIsSidebarOpen(p => !p)} variant="ghost" size="icon">
          {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
        
        <div className="flex items-center gap-2">
          <Button variant={mobileView === 'chat' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('chat')}>
            <MessageSquare className="h-4 w-4 mr-2" /> Chat
          </Button>
          <Button variant={mobileView === 'todos' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('todos')}>
            <CheckSquare className="h-4 w-4 mr-2" /> Todos
          </Button>
        </div>
        
        <div className="w-10" />
      </header>

      {/* Sidebar overlay */}
      {isSidebarOpen && (
        <div className="fixed inset-0 z-10">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsSidebarOpen(false)} />
          <div className="absolute left-0 top-14 bottom-0 w-80 max-w-[80vw] bg-black border-r border-neutral-800">
            <SessionSidebar onItemClick={() => setIsSidebarOpen(false)} />
          </div>
        </div>
      )}
      
      {/* Main content - Let ChatPage handle its own connection status */}
      <div className="flex-1 overflow-y-auto">
        {mobileView === 'chat' ? <ChatPage /> : <TodoPage />}
      </div>
    </main>
  );
}
// import { useState } from 'react';
// import { MessageSquare, CheckSquare, Menu, X } from 'lucide-react';
// import { Button } from '@/components/ui/button';
// import { ChatPage } from '@/features/chatbot/ChatPage';
// import { TodoPage } from '@/features/todos/TodoPage';
// import { SessionSidebar } from '@/features/chatbot/components/SessionSidebar';

// type MobileView = 'chat' | 'todos';

// export function MobileLayout() {
//   const [mobileView, setMobileView] = useState<MobileView>('chat');
//   const [isSidebarOpen, setIsSidebarOpen] = useState(false);

//   return (
//     // This main container uses flexbox to manage its children's layout.
//     <main className="flex h-[100dvh] w-screen flex-col bg-black text-white">
//       <header className="flex h-14 shrink-0 items-center justify-between border-b border-neutral-800 px-4 z-20">
//         <Button onClick={() => setIsSidebarOpen(p => !p)} variant="ghost" size="icon">
//           {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
//         </Button>
//         <div className="flex items-center gap-2">
//           <Button variant={mobileView === 'chat' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('chat')}>
//             <MessageSquare className="h-4 w-4 mr-2" /> Chat
//           </Button>
//           <Button variant={mobileView === 'todos' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('todos')}>
//             <CheckSquare className="h-4 w-4 mr-2" /> Todos
//           </Button>
//         </div>
//         <div className="w-10" />
//       </header>

//       {/* The sidebar overlay logic is correct and remains unchanged. */}
//       {isSidebarOpen && (
//         <div className="fixed inset-0 z-10">
//           <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsSidebarOpen(false)} />
//           <div className="absolute left-0 top-14 bottom-0 w-80 max-w-[80vw] bg-black border-r border-neutral-800">
//             <SessionSidebar onItemClick={() => setIsSidebarOpen(false)} />
//           </div>
//         </div>
//       )}
      
//       {/* --- THE DEFINITIVE CSS FIX --- */}
//       {/* This container will grow to fill the remaining space. */}
//       <div className="flex-1 overflow-y-auto">
//         {/* We use standard conditional rendering. The key is that the parent
//             div handles the scrolling, not the children. */}
//         {mobileView === 'chat' ? <ChatPage /> : <TodoPage />}
//       </div>
//     </main>
//   );
// }
// // import { useState } from 'react';
// // import { MessageSquare, CheckSquare, Menu, X } from 'lucide-react';
// // import { Button } from '@/components/ui/button';
// // import { ChatPage } from '@/features/chatbot/ChatPage';
// // import { TodoPage } from '@/features/todos/TodoPage';
// // import { SessionSidebar } from '@/features/chatbot/components/SessionSidebar';

// // type MobileView = 'chat' | 'todos';

// // export function MobileLayout() {
// //   const [mobileView, setMobileView] = useState<MobileView>('chat');
// //   const [isSidebarOpen, setIsSidebarOpen] = useState(false);

// //   return (
// //     <main className="flex h-[100dvh] w-screen flex-col bg-black text-white">
// //       <header className="flex h-14 shrink-0 items-center justify-between border-b border-neutral-800 px-4 z-20">
// //         <Button onClick={() => setIsSidebarOpen(p => !p)} variant="ghost" size="icon">
// //           {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
// //         </Button>
// //         <div className="flex items-center gap-2">
// //           <Button variant={mobileView === 'chat' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('chat')}>
// //             <MessageSquare className="h-4 w-4 mr-2" /> Chat
// //           </Button>
// //           <Button variant={mobileView === 'todos' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('todos')}>
// //             <CheckSquare className="h-4 w-4 mr-2" /> Todos
// //           </Button>
// //         </div>
// //         <div className="w-10" />
// //       </header>

// //       {/* This logic correctly renders the sidebar as an overlay when isSidebarOpen is true */}
// //       {isSidebarOpen && (
// //         <div className="fixed inset-0 z-10">
// //           <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsSidebarOpen(false)} />
// //           <div className="absolute left-0 top-14 bottom-0 w-80 max-w-[80vw] bg-black border-r border-neutral-800">
// //             <SessionSidebar onItemClick={() => setIsSidebarOpen(false)} />
// //           </div>
// //         </div>
// //       )}
      
// //       {/* The main content area */}
// //       <div className="flex-1 relative">
// //         <div className={`absolute inset-0 h-full w-full ${mobileView === 'chat' ? 'block' : 'hidden'}`}>
// //           <ChatPage />
// //         </div>
// //         <div className={`absolute inset-0 h-full w-full ${mobileView === 'todos' ? 'block' : 'hidden'}`}>
// //           <TodoPage />
// //         </div>
// //       </div>
// //     </main>
// //   );
// // }
// // // import { useState } from 'react';
// // // import { MessageSquare, CheckSquare, Menu, X } from 'lucide-react';
// // // import { Button } from '@/components/ui/button';
// // // import { ChatPage } from '@/features/chatbot/ChatPage';
// // // import { TodoPage } from '@/features/todos/TodoPage';
// // // import { SessionSidebar } from '@/features/chatbot/components/SessionSidebar';

// // // type MobileView = 'chat' | 'todos';

// // // export function MobileLayout() {
// // //   const [mobileView, setMobileView] = useState<MobileView>('chat');
// // //   const [isSidebarOpen, setIsSidebarOpen] = useState(false);

// // //   return (
// // //     // Use dynamic viewport height (dvh) to ensure the layout respects the browser's UI
// // //     <main className="flex h-[100dvh] w-screen flex-col bg-black text-white">
// // //       <header className="flex h-14 shrink-0 items-center justify-between border-b border-neutral-800 px-4 z-20">
// // //         <Button onClick={() => setIsSidebarOpen(p => !p)} variant="ghost" size="icon">
// // //           {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
// // //         </Button>
// // //         <div className="flex items-center gap-2">
// // //           <Button variant={mobileView === 'chat' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('chat')}>
// // //             <MessageSquare className="h-4 w-4 mr-2" /> Chat
// // //           </Button>
// // //           <Button variant={mobileView === 'todos' ? 'default' : 'ghost'} size="sm" onClick={() => setMobileView('todos')}>
// // //             <CheckSquare className="h-4 w-4 mr-2" /> Todos
// // //           </Button>
// // //         </div>
// // //         <div className="w-10" />
// // //       </header>

// // //       {/* The mobile sidebar is now managed cleanly within this layout */}
// // //       {isSidebarOpen && (
// // //         <div className="fixed inset-0 z-10">
// // //           <div className="absolute inset-0 bg-black/60" onClick={() => setIsSidebarOpen(false)} />
// // //           <div className="absolute left-0 top-14 bottom-0 w-80 bg-black border-r border-neutral-800">
// // //             <SessionSidebar onItemClick={() => setIsSidebarOpen(false)} />
// // //           </div>
// // //         </div>
// // //       )}
      
// // //       {/* The main content area correctly takes up the remaining space */}
// // //       <div className="flex-1 relative">
// // //         {/* We use absolute positioning to make the views fill the parent,
// // //             which avoids flexbox conflicts and ensures only one is visible and active at a time. */}
// // //         <div className={`absolute inset-0 h-full w-full ${mobileView === 'chat' ? 'z-10' : 'z-0'}`}>
// // //           <ChatPage />
// // //         </div>
// // //         <div className={`absolute inset-0 h-full w-full ${mobileView === 'todos' ? 'z-10' : 'z-0'}`}>
// // //           <TodoPage />
// // //         </div>
// // //       </div>
// // //     </main>
// // //   );
// // // }