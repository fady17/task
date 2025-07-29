import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Trash2, AlertTriangle, Check, RotateCcw } from 'lucide-react';
import type { TodoItem as TodoItemType } from '../../../types';
import { cn } from '@/lib/utils';

interface TodoItemProps {
  item: TodoItemType;
  onToggle: () => void;
  onDelete: () => void;
  isLoading?: boolean;
}

export function TodoItem({ item, onToggle, onDelete, isLoading = false }: TodoItemProps) {
  return (
    <div
      className={cn(
        'group flex items-center gap-4 p-4 rounded-xl border-2 transition-all duration-200 hover:scale-[1.01] hover:shadow-lg',
        item.completed 
          ? 'bg-neutral-900 border-neutral-700 hover:bg-neutral-800' 
          : 'bg-black border-neutral-800 hover:border-neutral-600',
        isLoading && 'opacity-60 pointer-events-none scale-100'
      )}
    >
      {/* Custom checkbox with better styling */}
      <div className="relative shrink-0">
        <Checkbox
          id={`item-${item.id}`}
          checked={item.completed}
          onCheckedChange={onToggle}
          disabled={isLoading}
          className={cn(
            "w-5 h-5 border-2 rounded-md transition-all duration-200",
            item.completed 
              ? "bg-white border-white text-black" 
              : "border-neutral-600 hover:border-white"
          )}
        />
      </div>

      {/* Task title with improved typography */}
      <label
        htmlFor={`item-${item.id}`}
        className={cn(
          'flex-1 text-base cursor-pointer transition-all duration-200 min-w-0 leading-relaxed',
          item.completed 
            ? 'line-through text-neutral-500' 
            : 'text-white hover:text-neutral-100'
        )}
      >
        <span className="break-words">{item.title}</span>
      </label>

      {/* Action buttons with improved responsive design */}
      <div className="flex items-center gap-2 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        {!item.completed ? (
          <Button 
            onClick={onToggle} 
            size="sm"
            disabled={isLoading}
            className="h-8 w-8 p-0 bg-white text-black hover:bg-neutral-200 transition-all duration-200 rounded-lg shadow-sm" 
            title="Mark as completed"
          >
            {isLoading ? (
              <div className="w-3 h-3 border border-black border-t-transparent rounded-full animate-spin" />
            ) : (
              <Check className="w-3 h-3" />
            )}
            <span className="sr-only">Mark as completed</span>
          </Button>
        ) : (
          <Button 
            onClick={onToggle} 
            size="sm"
            disabled={isLoading}
            variant="outline" 
            className="h-8 w-8 p-0 border-2 border-neutral-600 text-neutral-400 hover:bg-neutral-800 hover:border-neutral-500 hover:text-white transition-all duration-200 rounded-lg" 
            title="Mark as incomplete"
          >
            {isLoading ? (
              <div className="w-3 h-3 border border-neutral-400 border-t-transparent rounded-full animate-spin" />
            ) : (
              <RotateCcw className="w-3 h-3" />
            )}
            <span className="sr-only">Mark as incomplete</span>
          </Button>
        )}
        
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button 
              variant="ghost"
              size="sm"
              disabled={isLoading}
              className="h-8 w-8 p-0 text-neutral-500 hover:text-red-400 hover:bg-red-950 transition-all duration-200 rounded-lg"
              title="Delete task"
            >
              <Trash2 className="w-3 h-3" />
              <span className="sr-only">Delete task</span>
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="bg-black border-2 border-neutral-700 text-white max-w-md mx-4">
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-3 text-lg">
                <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center shrink-0">
                  <AlertTriangle className="w-4 h-4 text-white" />
                </div>
                Delete Task
              </AlertDialogTitle>
              <AlertDialogDescription className="text-neutral-300 leading-relaxed">
                Are you sure you want to delete <strong className="text-white">"{item.title}"</strong>? 
                This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter className="gap-3">
              <AlertDialogCancel className="bg-neutral-800 border-2 border-neutral-700 text-white hover:bg-neutral-700 transition-colors duration-200">
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction 
                onClick={onDelete} 
                className="bg-red-600 hover:bg-red-700 text-white transition-colors duration-200"
              >
                Delete Task
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
// import { Button } from '@/components/ui/button';
// import { Checkbox } from '@/components/ui/checkbox';
// import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
// import { Trash2, AlertTriangle, Check, RotateCcw } from 'lucide-react';
// import type { TodoItem as TodoItemType } from '../../../types';
// import { cn } from '@/lib/utils';

// interface TodoItemProps {
//   item: TodoItemType;
//   onToggle: () => void;
//   onDelete: () => void;
// }

// interface TodoItemProps {
//   item: TodoItemType;
//   onToggle: () => void;
//   onDelete: () => void;
//   isLoading?: boolean;
// }

// export function TodoItem({ item, onToggle, onDelete, isLoading = false }: TodoItemProps) {
//   return (
//     <div
//       className={cn(
//         'flex items-center gap-3 p-3 rounded-lg border transition-all duration-200',
//         item.completed 
//           ? 'bg-green-900/10 border-green-800/20 hover:bg-green-900/20' 
//           : 'bg-neutral-800/30 border-neutral-700/50 hover:bg-neutral-800/50',
//         isLoading && 'opacity-50 pointer-events-none'
//       )}
//     >
//       <Checkbox
//         id={`item-${item.id}`}
//         checked={item.completed}
//         onCheckedChange={onToggle}
//         disabled={isLoading}
//         className="w-4 h-4 shrink-0"
//       />
//       <label
//         htmlFor={`item-${item.id}`}
//         className={cn(
//           'flex-1 text-sm cursor-pointer transition-all duration-200 min-w-0',
//           item.completed 
//             ? 'line-through text-neutral-500' 
//             : 'text-white'
//         )}
//       >
//         <span className="break-words">{item.title}</span>
//       </label>
//       <div className="flex items-center gap-1 shrink-0">
//         {!item.completed ? (
//           <Button 
//             onClick={onToggle} 
//             size="icon"
//             disabled={isLoading}
//             className="h-7 w-7 bg-green-600 hover:bg-green-700 text-white shrink-0" 
//             title="Mark as done"
//           >
//             {isLoading ? (
//               <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
//             ) : (
//               <Check className="w-3 h-3" />
//             )}
//           </Button>
//         ) : (
//           <Button 
//             onClick={onToggle} 
//             size="icon"
//             disabled={isLoading}
//             variant="outline" 
//             className="h-7 w-7 border-orange-400/50 text-orange-400 hover:bg-orange-900/20 hover:border-orange-400 shrink-0" 
//             title="Mark as undone"
//           >
//             {isLoading ? (
//               <div className="w-3 h-3 border border-orange-400 border-t-transparent rounded-full animate-spin" />
//             ) : (
//               <RotateCcw className="w-3 h-3" />
//             )}
//           </Button>
//         )}
//         <AlertDialog>
//           <AlertDialogTrigger asChild>
//             <Button 
//               variant="ghost"
//               size="icon"
//               disabled={isLoading}
//               className="h-7 w-7 text-neutral-400 hover:text-red-400 hover:bg-red-900/20 shrink-0"
//             >
//               <Trash2 className="w-3 h-3" />
//             </Button>
//           </AlertDialogTrigger>
//           <AlertDialogContent className="dark border-neutral-800 bg-neutral-900">
//             <AlertDialogHeader>
//               <AlertDialogTitle className="flex items-center gap-2">
//                 <AlertTriangle className="w-5 h-5 text-red-500" />
//                 Delete Task
//               </AlertDialogTitle>
//               <AlertDialogDescription>
//                 Are you sure you want to delete "{item.title}"? This action cannot be undone.
//               </AlertDialogDescription>
//             </AlertDialogHeader>
//             <AlertDialogFooter>
//               <AlertDialogCancel>Cancel</AlertDialogCancel>
//               <AlertDialogAction 
//                 onClick={onDelete} 
//                 className="bg-red-600 hover:bg-red-700"
//               >
//                 Delete Task
//               </AlertDialogAction>
//             </AlertDialogFooter>
//           </AlertDialogContent>
//         </AlertDialog>
//       </div>
//     </div>
//   );
// }
// // import { Button } from '@/components/ui/button';
// // import { Checkbox } from '@/components/ui/checkbox';
// // import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
// // import { Trash2, AlertTriangle } from 'lucide-react';
// // import type { TodoItem as TodoItemType } from '../../../types';
// // import { cn } from '@/lib/utils';

// // interface TodoItemProps {
// //   item: TodoItemType;
// //   onToggle: () => void;
// //   onDelete: () => void;
// // }

// // export function TodoItem({ item, onToggle, onDelete }: TodoItemProps) {
// //   return (
// //     <div
// //       className={cn(
// //         'flex items-center gap-3 p-3 rounded-md border border-neutral-800 transition-colors',
// //         item.completed
// //           ? 'bg-green-900/20 border-green-800/30'
// //           : 'bg-neutral-900 hover:bg-neutral-800/50'
// //       )}
// //     >
// //       <Checkbox
// //         id={`item-${item.id}`}
// //         checked={item.completed}
// //         onCheckedChange={onToggle}
// //         className="h-5 w-5"
// //       />
// //       <label
// //         htmlFor={`item-${item.id}`}
// //         className={cn(
// //           'flex-1 cursor-pointer',
// //           item.completed && 'line-through text-neutral-500'
// //         )}
// //       >
// //         {item.title}
// //       </label>
// //       <AlertDialog>
// //         <AlertDialogTrigger asChild>
// //           <Button size="icon" variant="ghost" className="h-8 w-8 text-neutral-500 hover:bg-red-900/50 hover:text-red-400">
// //             <Trash2 className="h-4 w-4" />
// //           </Button>
// //         </AlertDialogTrigger>
// //         <AlertDialogContent className="dark border-neutral-800 bg-neutral-900">
// //           <AlertDialogHeader>
// //             <AlertDialogTitle className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-red-500" />Delete Task</AlertDialogTitle>
// //             <AlertDialogDescription>Are you sure you want to delete "{item.title}"? This cannot be undone.</AlertDialogDescription>
// //           </AlertDialogHeader>
// //           <AlertDialogFooter>
// //             <AlertDialogCancel>Cancel</AlertDialogCancel>
// //             <AlertDialogAction onClick={onDelete} className="bg-red-600 hover:bg-red-700">Delete</AlertDialogAction>
// //           </AlertDialogFooter>
// //         </AlertDialogContent>
// //       </AlertDialog>
// //     </div>
// //   );
// // }