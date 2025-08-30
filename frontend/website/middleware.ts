/**
 * Production-Grade Authentication Middleware
 * 
 * Handles route protection at the middleware level with backend validation
 * and performance optimization through caching
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Production-grade session cache for middleware performance
interface SessionValidationCache {
  [sessionToken: string]: {
    isValid: boolean;
    timestamp: number;
    ttl: number;
  };
}

const sessionCache: SessionValidationCache = {};
const CACHE_TTL = 30000; // 30 seconds cache for middleware performance

/**
 * Clean up expired cache entries to prevent memory leaks
 */
function cleanupExpiredCache(): void {
  const now = Date.now();
  Object.keys(sessionCache).forEach(token => {
    const entry = sessionCache[token];
    if (now - entry.timestamp > entry.ttl) {
      delete sessionCache[token];
    }
  });
}

// Clean up cache every 5 minutes in production
if (typeof setInterval !== 'undefined') {
  setInterval(cleanupExpiredCache, 300000);
}

// Define protected and public routes
const PROTECTED_ROUTES = [
  '/conversations',
  '/feed',
  '/profile',
  '/settings',
  '/dashboard'
];

const AUTH_ROUTES = [
  '/login',
  '/signup',
  '/auth'
];

const PUBLIC_ROUTES = [
  '/',
  '/about',
  '/help',
  '/blog-editor-demo',
  '/design-system-demo',
  '/markdown-demo'
];

/**
 * Check if the user has a valid authentication session by validating with backend
 */
async function isAuthenticated(request: NextRequest): Promise<boolean> {
  try {
    // Check for our backend session cookie (matches backend SESSION_COOKIE_NAME: ai_social_session)
    const sessionToken = request.cookies.get('ai_social_session')?.value;
    
    if (!sessionToken) {
      return false;
    }
    
    // Check cache first for performance
    const cachedResult = sessionCache[sessionToken];
    if (cachedResult && Date.now() - cachedResult.timestamp < cachedResult.ttl) {
      return cachedResult.isValid;
    }
    
    // Production-grade validation: Actually validate with backend API
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Create a timeout promise for reliability
    const timeoutPromise = new Promise<Response>((_, reject) => {
      setTimeout(() => reject(new Error('Session validation timeout')), 5000);
    });
    
    // Validate session with backend - Production-grade header forwarding
    const fetchPromise = fetch(`${apiBaseUrl}/api/v1/auth/session`, {
      method: 'GET',
      headers: {
        'Cookie': `ai_social_session=${sessionToken}`,
        'Accept': 'application/json',
        // Forward original browser headers for fingerprint validation (industry standard)
        'User-Agent': request.headers.get('user-agent') || 'AI-Social-Middleware/1.0',
        'X-Forwarded-For': request.headers.get('x-forwarded-for') || request.nextUrl.hostname || '127.0.0.1',
        'X-Real-IP': request.headers.get('x-real-ip') || request.nextUrl.hostname || '127.0.0.1',
      },
      cache: 'no-store'
    });
    
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    
    if (!response.ok) {
      // Cache negative result briefly to prevent spam
      sessionCache[sessionToken] = {
        isValid: false,
        timestamp: Date.now(),
        ttl: 5000 // 5 seconds for negative cache
      };
      return false;
    }
    
    const sessionData = await response.json();
    const isValid = sessionData.authenticated === true;
    
    // Cache the result
    sessionCache[sessionToken] = {
      isValid,
      timestamp: Date.now(),
      ttl: isValid ? CACHE_TTL : 5000
    };
    
    return isValid;
    
  } catch (error) {
    console.error('Auth validation failed:', error);
    // In case of error, default to false for security
    return false;
  }
}

/**
 * Get the appropriate redirect URL based on the original request
 */
function getRedirectUrl(request: NextRequest, destination: string): string {
  const url = request.nextUrl.clone();
  url.pathname = destination;
  
  // Preserve the original URL as a callback for post-login redirect
  if (destination === '/') {
    url.searchParams.set('callbackUrl', request.nextUrl.pathname + request.nextUrl.search);
  }
  
  return url.toString();
}

/**
 * Check if a route requires authentication
 */
function isProtectedRoute(pathname: string): boolean {
  return PROTECTED_ROUTES.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  );
}

/**
 * Check if a route is an authentication route
 */
function isAuthRoute(pathname: string): boolean {
  return AUTH_ROUTES.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  );
}

/**
 * Main middleware function
 */
export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const isUserAuthenticated = await isAuthenticated(request);

  // Development mode: Add comprehensive debug headers
  if (process.env.NODE_ENV === 'development') {
    const response = NextResponse.next();
    response.headers.set('X-Auth-Status', isUserAuthenticated ? 'authenticated' : 'unauthenticated');
    response.headers.set('X-Route-Type', isProtectedRoute(pathname) ? 'protected' : 'public');
    response.headers.set('X-Middleware-Version', '2.1-production-headers');
    response.headers.set('X-Session-Cookie-Present', request.cookies.has('ai_social_session') ? 'true' : 'false');
    response.headers.set('X-User-Agent-Forwarded', request.headers.get('user-agent')?.substring(0, 50) || 'none');
    
    // Continue with normal middleware logic but return the response with debug headers
    if (isProtectedRoute(pathname) && !isUserAuthenticated) {
      const redirectUrl = getRedirectUrl(request, '/');
      console.log(`🔐 Middleware: Redirecting unauthenticated user from ${pathname} to ${redirectUrl}`);
      return NextResponse.redirect(redirectUrl);
    }
    
    if (isAuthRoute(pathname) && isUserAuthenticated) {
      const callbackUrl = request.nextUrl.searchParams.get('callbackUrl') || '/conversations';
      const redirectUrl = getRedirectUrl(request, callbackUrl);
      console.log(`✅ Middleware: Redirecting authenticated user from ${pathname} to ${redirectUrl}`);
      return NextResponse.redirect(redirectUrl);
    }
    
    console.log(`🚀 Middleware: Allowing access to ${pathname} (auth: ${isUserAuthenticated})`);
    return response;
  }

  // Production mode: Optimized middleware logic with minimal logging
  
  // Handle protected routes
  if (isProtectedRoute(pathname)) {
    if (!isUserAuthenticated) {
      // Redirect to login with callback URL
      const redirectUrl = getRedirectUrl(request, '/');
      
      // Log security events in production
      if (process.env.NODE_ENV === 'production') {
        const clientIP = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown';
        console.log(`🔐 SECURITY: Unauthenticated access attempt to ${pathname} from ${clientIP}`);
      }
      
      return NextResponse.redirect(redirectUrl);
    }
  }

  // Handle auth routes (login, signup) - redirect authenticated users
  if (isAuthRoute(pathname)) {
    if (isUserAuthenticated) {
      // Get callback URL from query params or default to conversations
      const callbackUrl = request.nextUrl.searchParams.get('callbackUrl') || '/conversations';
      const redirectUrl = getRedirectUrl(request, callbackUrl);
      return NextResponse.redirect(redirectUrl);
    }
  }

  // Allow the request to continue
  return NextResponse.next();
}

/**
 * Configure which routes the middleware should run on
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.).*)',
  ],
};
