import type { ApiResponse } from '@/types';

/**
 * A pure API client function for sending a chat prompt.
 * It takes the full endpoint URL as an argument, making it independent of any config file.
 *
 * @param apiUrl The full URL of the chat endpoint (e.g., 'https://<host>/api/ai/chat').
 * @param prompt The user's message.
 * @returns A promise that resolves to the API response.
 */
export const fetchChatResponse = async (apiUrl: string, prompt: string): Promise<ApiResponse> => {
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'An API error occurred.' }));
      throw new Error(errorData.detail);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch chat response:', error);
    throw new Error('Could not connect to the AI assistant. Please try again.');
  }
};
// import { API_CONFIG } from '@/config';
// import type { ApiResponse } from '../../../types';

// // const API_URL = 'http://localhost:8000/ai/chat';
// const API_URL = `${API_CONFIG.HTTP_URL}/chat`;


// export const fetchChatResponse = async (prompt: string): Promise<ApiResponse> => {
//   try {
//     const response = await fetch(API_URL, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify({ prompt }),
//     });

//     if (!response.ok) {
//       const errorData = await response.json();
//       throw new Error(errorData.detail || 'An API error occurred.');
//     }

//     return await response.json();
//   } catch (error) {
//     console.error('Failed to fetch chat response:', error);
//     // Re-throw a user-friendly error
//     throw new Error('Could not connect to the AI assistant. Please try again.');
//   }
// };