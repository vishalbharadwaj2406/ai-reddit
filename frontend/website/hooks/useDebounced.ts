import { useCallback, useRef, useState, useEffect } from 'react';

/**
 * Hook to debounce rapid state updates during streaming
 */
export function useDebounced<T>(value: T, delay: number): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const valueRef = useRef<T>(value);
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  const updateValue = useCallback(() => {
    setDebouncedValue(valueRef.current);
  }, []);

  useEffect(() => {
    valueRef.current = value;
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(updateValue, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, delay, updateValue]);

  return debouncedValue;
}

/**
 * Hook specifically for debouncing markdown content during streaming
 */
export function useDebouncedMarkdown(content: string, isStreaming: boolean): string {
  // Use shorter debounce for streaming, immediate for static content
  const debounceDelay = isStreaming ? 100 : 0;
  return useDebounced(content, debounceDelay);
}
