import { useState, useEffect } from 'react';
import { useTodos } from "./hooks/useTodos";
import { TodoList } from "./components/TodoList";
import { CreateListForm } from "./components/CreateListForm";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ListTodo, CheckCircle } from "lucide-react";

export function TodoPage() {
  const { lists, loading, error, addList, removeList, editListTitle, addItem, removeItem, toggleItemCompletion } = useTodos();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Auto-hide success messages
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // Enhanced wrapper functions with success messages
  const handleAddList = async (title: string) => {
    await addList(title);
    if (!error) {
      setSuccessMessage(`List "${title}" created successfully!`);
    }
  };

  const handleRemoveList = async (listId: number) => {
    const listToDelete = lists.find(list => list.id === listId);
    await removeList(listId);
    if (!error && listToDelete) {
      setSuccessMessage(`List "${listToDelete.title}" deleted successfully!`);
    }
  };

  const handleEditListTitle = async (listId: number, newTitle: string) => {
    await editListTitle(listId, newTitle);
    if (!error) {
      setSuccessMessage('List updated successfully!');
    }
  };

  const handleAddItem = async (listId: number, title: string) => {
    await addItem(listId, title);
    if (!error) {
      setSuccessMessage('Task added successfully!');
    }
  };

  const handleRemoveItem = async (listId: number, itemId: number) => {
    await removeItem(listId, itemId);
    if (!error) {
      setSuccessMessage('Task deleted successfully!');
    }
  };

  const handleToggleItem = async (listId: number, item: any) => {
    const wasCompleted = item.completed;
    await toggleItemCompletion(listId, item);
    if (!error) {
      setSuccessMessage(
        !wasCompleted 
          ? 'Task marked as completed! 🎉' 
          : 'Task marked as incomplete.'
      );
    }
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Fixed header section with alerts and form */}
      <div className="flex-shrink-0 p-6 space-y-6">
        {/* Status Messages */}
        {error && (
          <Alert variant="destructive" className="animate-in slide-in-from-top-2 duration-300 border-red-800 bg-red-900/20">
            <AlertDescription className="font-medium text-red-400">{error}</AlertDescription>
          </Alert>
        )}
        {successMessage && (
          <Alert className="border-green-800 bg-green-900/20 text-green-400 animate-in slide-in-from-top-2 duration-300">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <AlertDescription className="font-medium">{successMessage}</AlertDescription>
          </Alert>
        )}

        <CreateListForm onAddList={handleAddList} />
      </div>

      {/* Scrollable content area */}
      <div className="flex-1 overflow-y-auto px-6 pb-6">
        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-flex items-center gap-3 text-blue-400">
              <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-lg font-medium">Loading your lists...</span>
            </div>
          </div>
        )}
        
        {/* Empty State */}
        {!loading && lists.length === 0 && (
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <ListTodo className="w-12 h-12 text-blue-400" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">No lists yet!</h2>
            <p className="text-xl text-neutral-400 mb-8 max-w-md mx-auto">
              Create your first todo list above to start organizing your tasks and boosting your productivity.
            </p>
            <div className="flex items-center justify-center gap-8 text-sm text-neutral-500">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Create lists</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Add tasks</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span>Track progress</span>
              </div>
            </div>
          </div>
        )}

        {/* Todo Lists Grid */}
        {lists.length > 0 && (
          <div className="grid gap-6 lg:grid-cols-2">
            {lists.map((list) => (
              <TodoList
                key={list.id}
                list={list}
                onDelete={handleRemoveList}
                onEditTitle={handleEditListTitle}
                onAddItem={handleAddItem}
                onToggleItem={handleToggleItem}
                onDeleteItem={handleRemoveItem}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
// import { useState, useEffect } from 'react';
// import { useTodos } from "./hooks/useTodos";
// import { TodoList } from "./components/TodoList";
// import { CreateListForm } from "./components/CreateListForm";
// import { Alert, AlertDescription } from "@/components/ui/alert";
// import { ListTodo, CheckCircle } from "lucide-react";

// export function TodoPage() {
//   const { lists, loading, error, addList, removeList, editListTitle, addItem, removeItem, toggleItemCompletion } = useTodos();
//   const [successMessage, setSuccessMessage] = useState<string | null>(null);

//   // Auto-hide success messages
//   useEffect(() => {
//     if (successMessage) {
//       const timer = setTimeout(() => setSuccessMessage(null), 3000);
//       return () => clearTimeout(timer);
//     }
//   }, [successMessage]);

//   // Enhanced wrapper functions with success messages
//   const handleAddList = async (title: string) => {
//     await addList(title);
//     if (!error) {
//       setSuccessMessage(`List "${title}" created successfully!`);
//     }
//   };

//   const handleRemoveList = async (listId: number) => {
//     const listToDelete = lists.find(list => list.id === listId);
//     await removeList(listId);
//     if (!error && listToDelete) {
//       setSuccessMessage(`List "${listToDelete.title}" deleted successfully!`);
//     }
//   };

//   const handleEditListTitle = async (listId: number, newTitle: string) => {
//     await editListTitle(listId, newTitle);
//     if (!error) {
//       setSuccessMessage('List updated successfully!');
//     }
//   };

//   const handleAddItem = async (listId: number, title: string) => {
//     await addItem(listId, title);
//     if (!error) {
//       setSuccessMessage('Task added successfully!');
//     }
//   };

//   const handleRemoveItem = async (listId: number, itemId: number) => {
//     await removeItem(listId, itemId);
//     if (!error) {
//       setSuccessMessage('Task deleted successfully!');
//     }
//   };

//   const handleToggleItem = async (listId: number, item: any) => {
//     const wasCompleted = item.completed;
//     await toggleItemCompletion(listId, item);
//     if (!error) {
//       setSuccessMessage(
//         !wasCompleted 
//           ? 'Task marked as completed! 🎉' 
//           : 'Task marked as incomplete.'
//       );
//     }
//   };

//   return (
//     <div className="p-6 space-y-6">
     
//       {/* Status Messages */}
//       {error && (
//         <Alert variant="destructive" className="animate-in slide-in-from-top-2 duration-300 border-red-800 bg-red-900/20">
//           <AlertDescription className="font-medium text-red-400">{error}</AlertDescription>
//         </Alert>
//       )}
//       {successMessage && (
//         <Alert className="border-green-800 bg-green-900/20 text-green-400 animate-in slide-in-from-top-2 duration-300">
//           <CheckCircle className="w-4 h-4 text-green-500" />
//           <AlertDescription className="font-medium">{successMessage}</AlertDescription>
//         </Alert>
//       )}

//       <CreateListForm onAddList={handleAddList} />

//       {/* Loading State */}
//       {loading && (
//         <div className="text-center py-12">
//           <div className="inline-flex items-center gap-3 text-blue-400">
//             <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
//             <span className="text-lg font-medium">Loading your lists...</span>
//           </div>
//         </div>
//       )}
      
//       {/* Empty State */}
//       {!loading && lists.length === 0 && (
//         <div className="text-center py-16">
//           <div className="w-24 h-24 bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-6">
//             <ListTodo className="w-12 h-12 text-blue-400" />
//           </div>
//           <h2 className="text-3xl font-bold text-white mb-4">No lists yet!</h2>
//           <p className="text-xl text-neutral-400 mb-8 max-w-md mx-auto">
//             Create your first todo list above to start organizing your tasks and boosting your productivity.
//           </p>
//           <div className="flex items-center justify-center gap-8 text-sm text-neutral-500">
//             <div className="flex items-center gap-2">
//               <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
//               <span>Create lists</span>
//             </div>
//             <div className="flex items-center gap-2">
//               <div className="w-3 h-3 bg-green-500 rounded-full"></div>
//               <span>Add tasks</span>
//             </div>
//             <div className="flex items-center gap-2">
//               <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
//               <span>Track progress</span>
//             </div>
//           </div>
//         </div>
//       )}

//       {/* Todo Lists Grid */}
//       <div className="grid gap-6 lg:grid-cols-2">
//         {lists.map((list) => (
//           <TodoList
//             key={list.id}
//             list={list}
//             onDelete={handleRemoveList}
//             onEditTitle={handleEditListTitle}
//             onAddItem={handleAddItem}
//             onToggleItem={handleToggleItem}
//             onDeleteItem={handleRemoveItem}
//           />
//         ))}
//       </div>
//     </div>
//   );
// }
// import { useTodos } from "./hooks/useTodos";
// import { TodoList } from "./components/TodoList";
// import { CreateListForm } from "./components/CreateListForm"; // We'll create this next
// import { Alert, AlertDescription } from "@/components/ui/alert";
// import { ListTodo } from "lucide-react";

// export function TodoPage() {
//   const { lists, loading, error, addList, removeList, editListTitle, addItem, removeItem, toggleItemCompletion } = useTodos();

//   return (
//     <div className="p-6 space-y-6">
//       <h1 className="text-4xl font-bold text-center">My Todo Lists</h1>
//       {error && (
//         <Alert variant="destructive">
//           <AlertDescription>{error}</AlertDescription>
//         </Alert>
//       )}

//       <CreateListForm onAddList={addList} />

//       {loading && <p className="text-center">Loading...</p>}
      
//       {!loading && lists.length === 0 && (
//         <div className="text-center py-16 text-neutral-500">
//           <ListTodo className="mx-auto h-16 w-16 mb-4" />
//           <h2 className="text-2xl font-semibold">No lists found</h2>
//           <p>Create your first list to get started!</p>
//         </div>
//       )}

//       <div className="grid gap-6 lg:grid-cols-2">
//         {lists.map((list) => (
//           <TodoList
//             key={list.id}
//             list={list}
//             onDelete={removeList}
//             onEditTitle={editListTitle}
//             onAddItem={addItem}
//             onToggleItem={toggleItemCompletion}
//             onDeleteItem={removeItem}
//           />
//         ))}
//       </div>
//     </div>
//   );
// }