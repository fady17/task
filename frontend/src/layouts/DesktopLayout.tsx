import { useState, useRef, type RefObject } from 'react';
import { PanelLeft, PanelLeftClose, CheckSquare } from 'lucide-react';
import { type ImperativePanelHandle } from "react-resizable-panels";
import { Button } from '@/components/ui/button';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { ChatPage } from '@/features/chatbot/ChatPage';
import { TodoPage } from '@/features/todos/TodoPage';
import { SessionSidebar } from '@/features/chatbot/components/SessionSidebar';

export function DesktopLayout() {
  const [isSessionsCollapsed, setIsSessionsCollapsed] = useState(false);
  
  // Initialize refs correctly with null. TypeScript infers the nullable type.
  const sessionsPanelRef = useRef<ImperativePanelHandle>(null);
  const todosPanelRef = useRef<ImperativePanelHandle>(null);

  // Fix: Accept the correct nullable ref type
  const togglePanel = (panelRef: RefObject<ImperativePanelHandle | null>) => {
    const panel = panelRef.current;
    // The null check makes this function type-safe and runtime-safe.
    if (panel) {
      if (panel.isCollapsed()) {
        panel.expand();
      } else {
        panel.collapse();
      }
    }
  };

  return (
    <main className="flex h-screen w-screen flex-col bg-black text-white">
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-neutral-800 px-4">
        <Button onClick={() => togglePanel(sessionsPanelRef)} variant="ghost" size="icon">
          {isSessionsCollapsed ? <PanelLeft className="h-5 w-5" /> : <PanelLeftClose className="h-5 w-5" />}
        </Button>
        <h1 className="text-lg font-semibold">AI Todo Assistant</h1>
        <Button onClick={() => togglePanel(todosPanelRef)} variant="ghost" size="icon">
          <CheckSquare className="h-5 w-5" />
        </Button>
      </header>

      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal" className="h-full w-full">
          <ResizablePanel
            ref={sessionsPanelRef}
            collapsible
            collapsedSize={0}
            minSize={15}
            defaultSize={20}
            onCollapse={() => setIsSessionsCollapsed(true)}
            onExpand={() => setIsSessionsCollapsed(false)}
          >
            <SessionSidebar />
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          <ResizablePanel defaultSize={45} minSize={30}>
            <ChatPage />
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          <ResizablePanel ref={todosPanelRef} collapsible minSize={25} defaultSize={35}>
            <TodoPage />
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </main>
  );
}