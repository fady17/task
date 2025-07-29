import { useState, type FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus } from 'lucide-react';

interface CreateItemFormProps {
  listId: number;
  onAddItem: (listId: number, title: string) => void;
  isLoading?: boolean;
}

export function CreateItemForm({ listId, onAddItem, isLoading = false }: CreateItemFormProps) {
  const [title, setTitle] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (title.trim() && !isLoading) {
      onAddItem(listId, title.trim());
      setTitle('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row w-full items-start sm:items-center gap-3">
      <div className="flex-1 w-full">
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a new task..."
          className="h-11 bg-black border-2 border-neutral-700 focus:border-white transition-all duration-200 text-white placeholder:text-neutral-400 rounded-xl"
          disabled={isLoading}
          maxLength={200}
        />
        {/* Character count for longer inputs */}
        {title.length > 150 && (
          <div className="mt-1 text-right">
            <span className={`text-xs ${title.length > 180 ? 'text-red-400' : 'text-neutral-500'}`}>
              {title.length}/200
            </span>
          </div>
        )}
      </div>
      
      <Button 
        type="submit" 
        size="sm" 
        disabled={!title.trim() || isLoading}
        className="h-11 px-6 bg-white text-black hover:bg-neutral-200 transition-all duration-200 shadow-sm rounded-xl font-medium whitespace-nowrap"
      >
        {isLoading ? (
          <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin mr-2" />
        ) : (
          <Plus className="h-4 w-4 mr-2" />
        )}
        {isLoading ? 'Adding...' : 'Add Task'}
      </Button>
    </form>
  );
}
// import { useState, type FormEvent } from 'react';
// import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
// import { Plus } from 'lucide-react';

// interface CreateItemFormProps {
//   listId: number;
//   onAddItem: (listId: number, title: string) => void;
//   // --- ADDED: isLoading prop ---
//   isLoading?: boolean;
// }

// export function CreateItemForm({ listId, onAddItem, isLoading = false }: CreateItemFormProps) {
//   const [title, setTitle] = useState('');

//   const handleSubmit = (e: FormEvent) => {
//     e.preventDefault();
//     if (title.trim() && !isLoading) { // Prevent submit if loading
//       onAddItem(listId, title.trim());
//       setTitle('');
//     }
//   };

//   return (
//     <form onSubmit={handleSubmit} className="flex w-full items-center gap-2">
//       <Input
//         value={title}
//         onChange={(e) => setTitle(e.target.value)}
//         placeholder="Add a new task..."
//         className="flex-1 bg-neutral-800 border-neutral-700"
//         // --- ADDED: Disable input when loading ---
//         disabled={isLoading}
//       />
//       <Button 
//         type="submit" 
//         size="sm" 
//         // --- UPDATED: Disable button based on title OR loading state ---
//         disabled={!title.trim() || isLoading}
//       >
//         {/* --- ADDED: Show spinner when loading, otherwise show Plus icon --- */}
//         {isLoading ? (
//           <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
//         ) : (
//           <Plus className="h-4 w-4" />
//         )}
//       </Button>
//     </form>
//   );
// }
// // import { useState, type FormEvent } from 'react';
// // import { Button } from '@/components/ui/button';
// // import { Input } from '@/components/ui/input';
// // import { Plus } from 'lucide-react';

// // interface CreateItemFormProps {
// //   listId: number;
// //   onAddItem: (listId: number, title: string) => void;
// // }

// // export function CreateItemForm({ listId, onAddItem }: CreateItemFormProps) {
// //   const [title, setTitle] = useState('');

// //   const handleSubmit = (e: FormEvent) => {
// //     e.preventDefault();
// //     if (title.trim()) {
// //       onAddItem(listId, title.trim());
// //       setTitle('');
// //     }
// //   };

// //   return (
// //     <form onSubmit={handleSubmit} className="flex w-full items-center gap-2">
// //       <Input
// //         value={title}
// //         onChange={(e) => setTitle(e.target.value)}
// //         placeholder="Add a new task..."
// //         className="flex-1 bg-neutral-800 border-neutral-700"
// //       />
// //       <Button type="submit" size="sm" disabled={!title.trim()}>
// //         <Plus className="h-4 w-4" />
// //       </Button>
// //     </form>
// //   );
// // }