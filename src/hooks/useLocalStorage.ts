import { useState, useEffect } from 'react';

// A helper function to safely parse JSON from localStorage
function getSavedValue<T>(key: string, initialValue: T | (() => T)): T {
  try {
    const savedValue = localStorage.getItem(key);
    if (savedValue) {
      return JSON.parse(savedValue);
    }
  } catch (error) {
    console.error(`Error reading localStorage key “${key}”:`, error);
  }

  // If we get here, there was no saved value or an error occurred.
  // We handle the case where the initial value is a function, just like useState.
  if (initialValue instanceof Function) {
    return initialValue();
  }
  return initialValue;
}

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    return getSavedValue(key, initialValue);
  });

  // This useEffect hook will run only when the 'key' or 'value' changes.
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error setting localStorage key “${key}”:`, error);
    }
  }, [key, value]);

  return [value, setValue] as const;
}