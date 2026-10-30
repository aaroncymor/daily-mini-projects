import { useState, useEffect } from 'react';

// Extract stateful logic into custom hooks and optimize re-renders using
// useMemo (derived values) and useCallback (memoized functions)

// Custom Hook for persistent state
export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : initialValue
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue]
}
