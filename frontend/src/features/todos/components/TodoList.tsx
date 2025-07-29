import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { TodoList as TodoListType, TodoItem as TodoItemType } from "../../../types";
import { TodoListHeader } from "./TodoListHeader";
import { CreateItemForm } from "./CreateItemForm";
import { TodoItem } from "./TodoItem";
import { ListTodo } from "lucide-react";

interface TodoListProps {
  list: TodoListType;
  onDelete: (listId: number) => void;
  onEditTitle: (listId: number, newTitle: string) => void;
  onAddItem: (listId: number, title: string) => void;
  onToggleItem: (listId: number, item: TodoItemType) => void;
  onDeleteItem: (listId: number, itemId: number) => void;
  isActionLoading?: (action: string, ...ids: (string | number)[]) => boolean;
}

export function TodoList({ 
  list, 
  onDelete, 
  onEditTitle, 
  onAddItem, 
  onToggleItem, 
  onDeleteItem,
  isActionLoading = () => false
}: TodoListProps) {
  const isListLoading = isActionLoading('remove_list', list.id) || 
                       isActionLoading('edit_list', list.id);
  const isAddingItem = isActionLoading('add_item', list.id);

  return (
    <Card className={`
      border-2 border-neutral-800 bg-black text-white shadow-2xl 
      transition-all duration-300 hover:shadow-3xl hover:border-neutral-700
      ${isListLoading ? 'opacity-50 pointer-events-none' : ''}
    `}>
      <CardHeader className="pb-4">
        <TodoListHeader 
          list={list} 
          onDelete={onDelete} 
          onEditTitle={onEditTitle}
          isLoading={isListLoading}
        />
      </CardHeader>
      
      <CardContent className="space-y-6 px-6 pb-6">
        {/* Add item form with improved styling */}
        <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-800">
          <CreateItemForm 
            listId={list.id} 
            onAddItem={onAddItem}
            isLoading={isAddingItem}
          />
        </div>

        {/* Tasks list with better organization */}
        {list.items.length > 0 ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm text-neutral-400 px-1">
              <span>Tasks ({list.items.length})</span>
              {list.stats.completed_items > 0 && (
                <span>{list.stats.completed_items} completed</span>
              )}
            </div>
            
            {/* Scrollable container with custom scrollbar */}
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-neutral-700 hover:scrollbar-thumb-neutral-600">
              {list.items.map((item) => (
                <TodoItem
                  key={item.id}
                  item={item}
                  onToggle={() => onToggleItem(list.id, item)}
                  onDelete={() => onDeleteItem(list.id, item.id)}
                  isLoading={isActionLoading('toggle_item', list.id, item.id) || 
                            isActionLoading('remove_item', list.id, item.id)}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-neutral-500">
            <div className="w-16 h-16 bg-neutral-900 rounded-full flex items-center justify-center mx-auto mb-4 border border-neutral-800">
              <ListTodo className="w-8 h-8" />
            </div>
            <p className="text-lg font-medium mb-2">No tasks yet</p>
            <p className="text-sm text-neutral-600">Add your first task above to get started!</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
// import { Card, CardContent, CardHeader } from "@/components/ui/card";
// import type { TodoList as TodoListType, TodoItem as TodoItemType } from "../../../types";
// import { TodoListHeader } from "./TodoListHeader";
// import { CreateItemForm } from "./CreateItemForm";
// import { TodoItem } from "./TodoItem";
// import { ListTodo } from "lucide-react";

// interface TodoListProps {
//   list: TodoListType;
//   onDelete: (listId: number) => void;
//   onEditTitle: (listId: number, newTitle: string) => void;
//   onAddItem: (listId: number, title: string) => void;
//   onToggleItem: (listId: number, item: TodoItemType) => void;
//   onDeleteItem: (listId: number, itemId: number) => void;
//   isActionLoading?: (action: string, ...ids: (string | number)[]) => boolean;
// }

// export function TodoList({ 
//   list, 
//   onDelete, 
//   onEditTitle, 
//   onAddItem, 
//   onToggleItem, 
//   onDeleteItem,
//   isActionLoading = () => false
// }: TodoListProps) {
//   const isListLoading = isActionLoading('remove_list', list.id) || 
//                        isActionLoading('edit_list', list.id);
//   const isAddingItem = isActionLoading('add_item', list.id);

//   return (
//     <Card className={`border-neutral-800 bg-neutral-900 text-white shadow-lg transition-all duration-200 ${
//       isListLoading ? 'opacity-50 pointer-events-none' : ''
//     }`}>
//       <CardHeader>
//         <TodoListHeader 
//           list={list} 
//           onDelete={onDelete} 
//           onEditTitle={onEditTitle}
//           isLoading={isListLoading}
//         />
//       </CardHeader>
//       <CardContent className="space-y-4">
//         <CreateItemForm 
//           listId={list.id} 
//           onAddItem={onAddItem}
//           isLoading={isAddingItem}
//         />
//         {list.items.length > 0 ? (
//           <div className="space-y-2 max-h-96 overflow-y-auto">
//             {list.items.map((item) => (
//               <TodoItem
//                 key={item.id}
//                 item={item}
//                 onToggle={() => onToggleItem(list.id, item)}
//                 onDelete={() => onDeleteItem(list.id, item.id)}
//                 isLoading={isActionLoading('toggle_item', list.id, item.id) || 
//                           isActionLoading('remove_item', list.id, item.id)}
//               />
//             ))}
//           </div>
//         ) : (
//           <div className="text-center py-8 text-neutral-500">
//             <ListTodo className="mx-auto h-8 w-8 mb-2" />
//             <p className="text-sm">No tasks yet. Add one above!</p>
//           </div>
//         )}
//       </CardContent>
//     </Card>
//   );
// }
// // import { Card, CardContent, CardHeader } from "@/components/ui/card";
// // import type { TodoList as TodoListType, TodoItem as TodoItemType } from "../../../types";
// // import { TodoListHeader } from "./TodoListHeader";
// // import { CreateItemForm } from "./CreateItemForm";
// // import { TodoItem } from "./TodoItem";
// // import { ListTodo } from "lucide-react";

// // interface TodoListProps {
// //   list: TodoListType;
// //   onDelete: (listId: number) => void;
// //   onEditTitle: (listId: number, newTitle: string) => void;
// //   onAddItem: (listId: number, title: string) => void;
// //   onToggleItem: (listId: number, item: TodoItemType) => void;
// //   onDeleteItem: (listId: number, itemId: number) => void;
// // }

// // export function TodoList({ list, onDelete, onEditTitle, onAddItem, onToggleItem, onDeleteItem }: TodoListProps) {
// //   return (
// //     <Card className="border-neutral-800 bg-neutral-900 text-white shadow-lg">
// //       <CardHeader>
// //         <TodoListHeader list={list} onDelete={onDelete} onEditTitle={onEditTitle} />
// //       </CardHeader>
// //       <CardContent className="space-y-4">
// //         <CreateItemForm listId={list.id} onAddItem={onAddItem} />
// //         {list.items.length > 0 ? (
// //           <div className="space-y-2">
// //             {list.items.map((item) => (
// //               <TodoItem
// //                 key={item.id}
// //                 item={item}
// //                 onToggle={() => onToggleItem(list.id, item)}
// //                 onDelete={() => onDeleteItem(list.id, item.id)}
// //               />
// //             ))}
// //           </div>
// //         ) : (
// //           <div className="text-center py-8 text-neutral-500">
// //             <ListTodo className="mx-auto h-8 w-8 mb-2" />
// //             <p>No tasks yet. Add one above!</p>
// //           </div>
// //         )}
// //       </CardContent>
// //     </Card>
// //   );
// // }