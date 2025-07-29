import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { CardTitle } from '@/components/ui/card';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Edit3, Save, X, Trash2, AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import type { TodoList } from '../../../types';

interface TodoListHeaderProps {
  list: TodoList;
  onDelete: (listId: number) => void;
  onEditTitle: (listId: number, newTitle: string) => void;
  isLoading?: boolean;
}

export function TodoListHeader({ list, onDelete, onEditTitle, isLoading = false }: TodoListHeaderProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(list.title);

  const handleSave = () => {
    if (editTitle.trim() && editTitle.trim() !== list.title) {
      onEditTitle(list.id, editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(list.title);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  return (
    <div className="flex flex-col gap-4 p-1">
      {isEditing ? (
        <div className="flex items-center gap-3 w-full">
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 h-11 bg-black border-2 border-neutral-700 focus:border-white text-white placeholder:text-neutral-400 rounded-lg transition-all duration-200"
            autoFocus
            placeholder="Enter list title..."
          />
          <div className="flex items-center gap-2 shrink-0">
            <Button
              onClick={handleSave}
              disabled={!editTitle.trim()}
              size="sm"
              className="h-9 px-3 bg-white text-black hover:bg-neutral-200 transition-colors duration-200 rounded-lg font-medium"
            >
              <Save className="w-4 h-4" />
              <span className="sr-only">Save changes</span>
            </Button>
            <Button 
              onClick={handleCancel} 
              size="sm" 
              variant="outline"
              className="h-9 px-3 border-2 border-neutral-700 text-white hover:bg-neutral-800 transition-colors duration-200 rounded-lg"
            >
              <X className="w-4 h-4" />
              <span className="sr-only">Cancel editing</span>
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <CardTitle className="text-2xl font-bold text-white mb-3 truncate">
                {list.title}
              </CardTitle>
              
              {/* Stats section with improved responsive design */}
              <div className="flex flex-wrap items-center gap-4 text-sm text-neutral-400">
                <div className="flex items-center gap-2 min-w-fit">
                  <Clock className="w-4 h-4 shrink-0" />
                  <span className="whitespace-nowrap">
                    {list.stats.total_items} {list.stats.total_items === 1 ? 'task' : 'tasks'}
                  </span>
                </div>
                
                <div className="flex items-center gap-2 min-w-fit">
                  <CheckCircle className="w-4 h-4 text-white shrink-0" />
                  <span className="whitespace-nowrap">
                    {list.stats.completed_items} completed
                  </span>
                </div>
                
                {list.stats.total_items > 0 && (
                  <div className="flex items-center gap-3 min-w-fit">
                    <div className="w-20 h-2 bg-neutral-800 rounded-full overflow-hidden border border-neutral-700">
                      <div
                        className="h-full bg-white transition-all duration-500 ease-out"
                        style={{ width: `${list.stats.percentage_complete}%` }}
                      />
                    </div>
                    <span className="text-white font-semibold tabular-nums">
                      {list.stats.percentage_complete}%
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Action buttons with improved layout */}
            <div className="flex items-center gap-2 shrink-0">
              <Button 
                onClick={() => setIsEditing(true)} 
                size="sm" 
                variant="outline"
                disabled={isLoading}
                className="h-9 w-9 p-0 border-2 border-neutral-700 text-white hover:bg-neutral-800 hover:border-neutral-600 transition-all duration-200 rounded-lg"
                title="Edit list title"
              >
                <Edit3 className="w-4 h-4" />
                <span className="sr-only">Edit list title</span>
              </Button>
              
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    size="sm"
                    disabled={isLoading}
                    className="h-9 w-9 p-0 bg-red-600 hover:bg-red-700 text-white transition-all duration-200 rounded-lg"
                    title="Delete list"
                  >
                    {isLoading ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                    <span className="sr-only">Delete list</span>
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent className="bg-black border-2 border-neutral-700 text-white max-w-md mx-4">
                  <AlertDialogHeader>
                    <AlertDialogTitle className="flex items-center gap-3 text-lg">
                      <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center shrink-0">
                        <AlertTriangle className="w-4 h-4 text-white" />
                      </div>
                      Delete List
                    </AlertDialogTitle>
                    <AlertDialogDescription className="text-neutral-300 leading-relaxed">
                      Are you sure you want to delete <strong className="text-white">"{list.title}"</strong>? 
                      This will permanently delete the list and all {list.items.length} tasks inside it. 
                      This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter className="gap-3">
                    <AlertDialogCancel className="bg-neutral-800 border-2 border-neutral-700 text-white hover:bg-neutral-700 transition-colors duration-200">
                      Cancel
                    </AlertDialogCancel>
                    <AlertDialogAction 
                      onClick={() => onDelete(list.id)} 
                      className="bg-red-600 hover:bg-red-700 text-white transition-colors duration-200"
                    >
                      Delete List
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
// import { useState } from 'react';
// import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
// import { CardTitle } from '@/components/ui/card';
// import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
// import { Edit3, Save, X, Trash2, AlertTriangle, Clock, CheckCircle } from 'lucide-react';
// import type { TodoList } from '../../../types';

// interface TodoListHeaderProps {
//   list: TodoList;
//   onDelete: (listId: number) => void;
//   onEditTitle: (listId: number, newTitle: string) => void;
//   isLoading?: boolean;
// }

// export function TodoListHeader({ list, onDelete, onEditTitle, isLoading = false }: TodoListHeaderProps) {
//   const [isEditing, setIsEditing] = useState(false);
//   const [editTitle, setEditTitle] = useState(list.title);

//   const handleSave = () => {
//     if (editTitle.trim() && editTitle.trim() !== list.title) {
//       onEditTitle(list.id, editTitle.trim());
//     }
//     setIsEditing(false);
//   };

//   const handleCancel = () => {
//     setEditTitle(list.title);
//     setIsEditing(false);
//   };

//   const handleKeyDown = (e: React.KeyboardEvent) => {
//     if (e.key === 'Enter') {
//       handleSave();
//     } else if (e.key === 'Escape') {
//       handleCancel();
//     }
//   };

//   return (
//     <div className="flex items-center justify-between">
//       {isEditing ? (
//         <div className="flex items-center gap-2 flex-1">
//           <Input
//             value={editTitle}
//             onChange={(e) => setEditTitle(e.target.value)}
//             onKeyDown={handleKeyDown}
//             className="flex-1 h-10 bg-neutral-800 border-neutral-700"
//             autoFocus
//           />
//           <Button
//             onClick={handleSave}
//             disabled={!editTitle.trim()}
//             size="sm"
//             className="bg-green-600 hover:bg-green-700"
//           >
//             <Save className="w-4 h-4" />
//           </Button>
//           <Button 
//             onClick={handleCancel} 
//             size="sm" 
//             variant="outline"
//             className="border-neutral-700"
//           >
//             <X className="w-4 h-4" />
//           </Button>
//         </div>
//       ) : (
//         <>
//           <div className="flex-1">
//             <CardTitle className="text-2xl text-white mb-2">{list.title}</CardTitle>
//             {/* Stats section */}
//             <div className="flex items-center gap-4 text-sm text-neutral-400">
//               <div className="flex items-center gap-1">
//                 <Clock className="w-4 h-4" />
//                 <span>{list.stats.total_items} tasks</span>
//               </div>
//               <div className="flex items-center gap-1">
//                 <CheckCircle className="w-4 h-4 text-green-400" />
//                 <span>{list.stats.completed_items} completed</span>
//               </div>
//               {list.stats.total_items > 0 && (
//                 <div className="flex items-center gap-2">
//                   <div className="w-20 h-2 bg-neutral-700 rounded-full overflow-hidden">
//                     <div
//                       className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
//                       style={{ width: `${list.stats.percentage_complete}%` }}
//                     />
//                   </div>
//                   <span className="text-green-400 font-medium">{list.stats.percentage_complete}%</span>
//                 </div>
//               )}
//             </div>
//           </div>
//           <div className="flex items-center gap-2">
//             <Button 
//               onClick={() => setIsEditing(true)} 
//               size="sm" 
//               variant="outline"
//               disabled={isLoading}
//               className="border-neutral-700 hover:bg-neutral-800"
//             >
//               <Edit3 className="w-4 h-4" />
//             </Button>
//             <AlertDialog>
//               <AlertDialogTrigger asChild>
//                 <Button 
//                   variant="destructive" 
//                   size="sm"
//                   disabled={isLoading}
//                   className="hover:bg-red-600"
//                 >
//                   {isLoading ? (
//                     <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
//                   ) : (
//                     <Trash2 className="w-4 h-4" />
//                   )}
//                 </Button>
//               </AlertDialogTrigger>
//               <AlertDialogContent className="dark border-neutral-800 bg-neutral-900">
//                 <AlertDialogHeader>
//                   <AlertDialogTitle className="flex items-center gap-2">
//                     <AlertTriangle className="w-5 h-5 text-red-500" />
//                     Delete List
//                   </AlertDialogTitle>
//                   <AlertDialogDescription>
//                     Are you sure you want to delete "{list.title}"? This will permanently delete the list and all {list.items.length} tasks inside it. This action cannot be undone.
//                   </AlertDialogDescription>
//                 </AlertDialogHeader>
//                 <AlertDialogFooter>
//                   <AlertDialogCancel>Cancel</AlertDialogCancel>
//                   <AlertDialogAction 
//                     onClick={() => onDelete(list.id)} 
//                     className="bg-red-600 hover:bg-red-700"
//                   >
//                     Delete List
//                   </AlertDialogAction>
//                 </AlertDialogFooter>
//               </AlertDialogContent>
//             </AlertDialog>
//           </div>
//         </>
//       )}
//     </div>
//   );
// }
// // import { useState } from 'react';
// // import { Button } from '@/components/ui/button';
// // import { Input } from '@/components/ui/input';
// // import { CardTitle } from '@/components/ui/card';
// // import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
// // import { Trash2, Edit3, Save, X, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
// // import type { TodoList } from '../../../types';

// // interface TodoListHeaderProps {
// //   list: TodoList;
// //   onDelete: (listId: number) => void;
// //   onEditTitle: (listId: number, newTitle: string) => void;
// // }

// // export function TodoListHeader({ list, onDelete, onEditTitle }: TodoListHeaderProps) {
// //   const [isEditing, setIsEditing] = useState(false);
// //   const [editingTitle, setEditingTitle] = useState(list.title);

// //   const handleSave = () => {
// //     if (editingTitle.trim()) {
// //       onEditTitle(list.id, editingTitle.trim());
// //       setIsEditing(false);
// //     }
// //   };

// //   const handleCancel = () => {
// //     setEditingTitle(list.title);
// //     setIsEditing(false);
// //   };

// //   if (isEditing) {
// //     return (
// //       <div className="flex w-full items-center gap-2">
// //         <Input
// //           value={editingTitle}
// //           onChange={(e) => setEditingTitle(e.target.value)}
// //           onKeyDown={(e) => {
// //             if (e.key === 'Enter') handleSave();
// //             if (e.key === 'Escape') handleCancel();
// //           }}
// //           className="flex-1 bg-neutral-800 border-neutral-700"
// //           autoFocus
// //         />
// //         <Button onClick={handleSave} size="icon" className="bg-green-600 hover:bg-green-700">
// //           <Save className="h-4 w-4" />
// //         </Button>
// //         <Button onClick={handleCancel} size="icon" variant="outline" className="border-neutral-700 hover:bg-neutral-800">
// //           <X className="h-4 w-4" />
// //         </Button>
// //       </div>
// //     );
// //   }

// //   return (
// //     <div className="flex items-start justify-between gap-4">
// //       <div className="flex-1">
// //         <CardTitle className="text-2xl mb-2">{list.title}</CardTitle>
// //         <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-neutral-400">
// //           <div className="flex items-center gap-1.5"><Clock className="h-4 w-4" /><span>{list.stats.total_items} tasks</span></div>
// //           <div className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-green-500" /><span>{list.stats.completed_items} completed</span></div>
// //           {list.stats.total_items > 0 && (
// //             <div className="flex items-center gap-2">
// //               <div className="w-20 h-1.5 bg-neutral-700 rounded-full overflow-hidden">
// //                 <div
// //                   className="h-full bg-green-500"
// //                   style={{ width: `${list.stats.percentage_complete}%` }}
// //                 />
// //               </div>
// //               <span className="text-green-500 font-medium">{list.stats.percentage_complete}%</span>
// //             </div>
// //           )}
// //         </div>
// //       </div>
// //       <div className="flex items-center gap-2">
// //         <Button onClick={() => setIsEditing(true)} size="icon" variant="ghost" className="hover:bg-neutral-800">
// //             <Edit3 className="h-4 w-4" />
// //         </Button>
// //         <AlertDialog>
// //             <AlertDialogTrigger asChild>
// //                 <Button size="icon" variant="destructive" className="bg-red-900/50 hover:bg-red-900/80 text-red-400 hover:text-red-300">
// //                     <Trash2 className="h-4 w-4" />
// //                 </Button>
// //             </AlertDialogTrigger>
// //             <AlertDialogContent className="dark border-neutral-800 bg-neutral-900">
// //                 <AlertDialogHeader>
// //                     <AlertDialogTitle className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-red-500" />Delete List</AlertDialogTitle>
// //                     <AlertDialogDescription>
// //                         This will permanently delete "{list.title}" and all its tasks. This action cannot be undone.
// //                     </AlertDialogDescription>
// //                 </AlertDialogHeader>
// //                 <AlertDialogFooter>
// //                     <AlertDialogCancel>Cancel</AlertDialogCancel>
// //                     <AlertDialogAction onClick={() => onDelete(list.id)} className="bg-red-600 hover:bg-red-700">Delete</AlertDialogAction>
// //                 </AlertDialogFooter>
// //             </AlertDialogContent>
// //         </AlertDialog>
// //       </div>
// //     </div>
// //   );
// // }