/**
 * Utility functions for the frontend
 */

import { type ClassValue, clsx } from 'clsx';

/**
 * Merge and conditionally apply CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
