import { memo, useMemo, type ChangeEvent, type FormEvent } from 'react';

interface ChatInputProps {
  input: string;
  handleInputChange: (e: ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export const ChatInput = memo(function ChatInput({ 
  input, 
  handleInputChange, 
  handleSubmit, 
  isLoading, 
  disabled = false 
}: ChatInputProps) {
  const isDisabled = disabled || isLoading;
  
  // Memoize placeholder text to prevent recalculation
  const placeholder = useMemo(() => {
    if (disabled) return "Connecting to server...";
    if (isLoading) return "Sending message...";
    return "Type your message...";
  }, [disabled, isLoading]);
  
  // Memoize input className to prevent recalculation
  const inputClassName = useMemo(() => `
    flex-1 rounded-lg border px-3 py-2 text-sm transition-colors
    ${isDisabled 
      ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-not-allowed' 
      : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
    }
  `, [isDisabled]);
  
  // Memoize button states
  const isButtonDisabled = isDisabled || !input.trim();
  const buttonText = isLoading ? 'Sending...' : 'Send';
  
  // Memoize button className to prevent recalculation
  const buttonClassName = useMemo(() => `
    px-4 py-2 rounded-lg text-sm font-medium transition-colors
    ${isButtonDisabled
      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
      : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
    }
  `, [isButtonDisabled]);
  
  // Force debug render info
  // console.log('🎯 ChatInput RENDER - disabled:', disabled, 'isLoading:', isLoading, 'isDisabled:', isDisabled, 'buttonDisabled:', isButtonDisabled);

  return (
    <form onSubmit={handleSubmit} className="p-4">
      <div className="flex gap-2">
        <input
          key={`input-${isDisabled}`} // Force re-render when disabled state changes
          type="text"
          value={input}
          onChange={handleInputChange}
          disabled={isDisabled}
          placeholder={placeholder}
          className={inputClassName}
        />
        <button
          key={`button-${isButtonDisabled}`} // Force re-render when button state changes
          type="submit"
          disabled={isButtonDisabled}
          className={buttonClassName}
        >
          {buttonText}
        </button>
      </div>
      
      {/* Debug info - remove in production */}
      {/* <div className="text-xs text-gray-500 mt-1">
        Debug: disabled={String(disabled)}, isLoading={String(isLoading)}, status={isDisabled ? 'disabled' : 'enabled'}
      </div> */}
    </form>
  );
});
// import { type ChangeEvent, type FormEvent } from 'react';

// interface ChatInputProps {
//   input: string;
//   handleInputChange: (e: ChangeEvent<HTMLInputElement>) => void;
//   handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
//   isLoading: boolean;
//   disabled?: boolean;
// }

// export function ChatInput({ 
//   input, 
//   handleInputChange, 
//   handleSubmit, 
//   isLoading, 
//   disabled = false 
// }: ChatInputProps) {
//   const isDisabled = disabled || isLoading;
  
//   // Add debugging
//   console.log('🎯 ChatInput render - disabled:', disabled, 'isLoading:', isLoading, 'isDisabled:', isDisabled);

//   return (
//     <form onSubmit={handleSubmit} className="p-4">
//       <div className="flex gap-2">
//         <input
//           type="text"
//           value={input}
//           onChange={handleInputChange}
//           disabled={isDisabled}
//           placeholder={
//             disabled 
//               ? "Connecting to server..." 
//               : isLoading 
//                 ? "Sending message..." 
//                 : "Type your message..."
//           }
//           className={`
//             flex-1 rounded-lg border px-3 py-2 text-sm transition-colors
//             ${isDisabled 
//               ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-not-allowed' 
//               : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
//             }
//           `}
//         />
//         <button
//           type="submit"
//           disabled={isDisabled || !input.trim()}
//           className={`
//             px-4 py-2 rounded-lg text-sm font-medium transition-colors
//             ${isDisabled || !input.trim()
//               ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
//               : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
//             }
//           `}
//         >
//           {isLoading ? 'Sending...' : 'Send'}
//         </button>
//       </div>
//     </form>
//   );
// }
// // import { type ChangeEvent, type FormEvent } from 'react';

// // interface ChatInputProps {
// //   input: string;
// //   handleInputChange: (e: ChangeEvent<HTMLInputElement>) => void;
// //   handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
// //   isLoading: boolean;
// //   disabled?: boolean;
// // }

// // export function ChatInput({ 
// //   input, 
// //   handleInputChange, 
// //   handleSubmit, 
// //   isLoading, 
// //   disabled = false 
// // }: ChatInputProps) {
// //   const isDisabled = disabled || isLoading;

// //   return (
// //     <form onSubmit={handleSubmit} className="p-4">
// //       <div className="flex gap-2">
// //         <input
// //           type="text"
// //           value={input}
// //           onChange={handleInputChange}
// //           disabled={isDisabled}
// //           placeholder={
// //             disabled 
// //               ? "Connecting to server..." 
// //               : isLoading 
// //                 ? "Sending message..." 
// //                 : "Type your message..."
// //           }
// //           className={`
// //             flex-1 rounded-lg border px-3 py-2 text-sm transition-colors
// //             ${isDisabled 
// //               ? 'bg-gray-50 border-gray-200 text-gray-400 cursor-not-allowed' 
// //               : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
// //             }
// //           `}
// //         />
// //         <button
// //           type="submit"
// //           disabled={isDisabled || !input.trim()}
// //           className={`
// //             px-4 py-2 rounded-lg text-sm font-medium transition-colors
// //             ${isDisabled || !input.trim()
// //               ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
// //               : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
// //             }
// //           `}
// //         >
// //           {isLoading ? 'Sending...' : 'Send'}
// //         </button>
// //       </div>
// //     </form>
// //   );
// // }
// // // import { Button } from '@/components/ui/button';
// // // import { Input } from '@/components/ui/input';
// // // import { SendHorizonal } from 'lucide-react';
// // // import type { ChangeEvent, FormEvent } from 'react';

// // // interface ChatInputProps {
// // //   input: string;
// // //   handleInputChange: (e: ChangeEvent<HTMLInputElement>) => void;
// // //   handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
// // //   isLoading: boolean;
// // // }

// // // export function ChatInput({ input, handleInputChange, handleSubmit, isLoading }: ChatInputProps) {
// // //   return (
// // //     <form onSubmit={handleSubmit} className="flex w-full items-center space-x-2 p-4">
// // //       <Input
// // //         type="text"
// // //         placeholder="Ask me to manage your todo list..."
// // //         value={input}
// // //         onChange={handleInputChange}
// // //         disabled={isLoading}
// // //         className="flex-1"
// // //       />
// // //       <Button type="submit" disabled={isLoading}>
// // //         {isLoading ? '...' : <SendHorizonal className="h-4 w-4" />}
// // //       </Button>
// // //     </form>
// // //   );
// // // }