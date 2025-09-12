/**
 * Comprehensive API Error Type Definitions
 * Production-grade error handling with full type safety
 */

// FastAPI Error Response Formats
export interface FastAPIValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
  ctx?: Record<string, unknown>;
}

export interface FastAPIDetailError {
  message?: string;
  detail?: string;
  errorCode?: string;
}

export interface FastAPIErrorResponse {
  detail: string | FastAPIDetailError | FastAPIValidationError[];
}

// Standard API Error Response
export interface StandardErrorResponse {
  message?: string;
  error?: string;
  success?: false;
  data?: null;
}

// Union type for all possible error response formats
export type ApiErrorResponse = FastAPIErrorResponse | StandardErrorResponse;

// Parsed error data with consistent structure
export interface ParsedErrorData {
  message: string;
  errorCode?: string;
  validationErrors?: FastAPIValidationError[];
  originalResponse?: unknown;
}

// Type guard functions
export function isFastAPIError(error: unknown): error is FastAPIErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error
  );
}

export function isValidationError(error: unknown): error is { detail: FastAPIValidationError[] } {
  return (
    isFastAPIError(error) &&
    Array.isArray(error.detail) &&
    error.detail.length > 0 &&
    typeof error.detail[0] === 'object' &&
    'loc' in error.detail[0] &&
    'msg' in error.detail[0]
  );
}

export function isDetailError(error: unknown): error is { detail: FastAPIDetailError } {
  return (
    isFastAPIError(error) &&
    typeof error.detail === 'object' &&
    !Array.isArray(error.detail)
  );
}

export function isStandardError(error: unknown): error is StandardErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    ('message' in error || 'error' in error)
  );
}
