/**
 * Production-Grade Authentication Middleware
 * 
 * Handles route protection at the middleware level for better performance
 * and user experience
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define protected and public routes
const PROTECTED_ROUTES = [
  '/conversations',
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
  '/feed',
  '/about',
  '/help'
];

/**
 * Check if the user has a valid authentication session
 */
async function isAuthenticated(request: NextRequest): Promise<boolean> {
  try {
    // Check for NextAuth session cookie
    const sessionToken = request.cookies.get('next-auth.session-token')?.value ||
                        request.cookies.get('__Secure-next-auth.session-token')?.value;
    
    // Check for our backend JWT cookie
    const backendToken = request.cookies.get('ai_social_jwt')?.value;
    
    // Check for localStorage-based session (fallback for client-side routing)
    const authHeader = request.headers.get('authorization');
    
    return !!(sessionToken || backendToken || authHeader);
  } catch (error) {
    console.error('Auth check failed:', error);
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

  // Development mode: Add debug headers
  if (process.env.NODE_ENV === 'development') {
    const response = NextResponse.next();
    response.headers.set('X-Auth-Status', isUserAuthenticated ? 'authenticated' : 'unauthenticated');
    response.headers.set('X-Route-Type', isProtectedRoute(pathname) ? 'protected' : 'public');
    
    // Continue with normal middleware logic but return the response with debug headers
    if (isProtectedRoute(pathname) && !isUserAuthenticated) {
      const redirectUrl = getRedirectUrl(request, '/');
      return NextResponse.redirect(redirectUrl);
    }
    
    if (isAuthRoute(pathname) && isUserAuthenticated) {
      const callbackUrl = request.nextUrl.searchParams.get('callbackUrl') || '/conversations';
      const redirectUrl = getRedirectUrl(request, callbackUrl);
      return NextResponse.redirect(redirectUrl);
    }
    
    return response;
  }

  // Production mode: Standard middleware logic
  
  // Handle protected routes
  if (isProtectedRoute(pathname)) {
    if (!isUserAuthenticated) {
      // Redirect to login with callback URL
      const redirectUrl = getRedirectUrl(request, '/');
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
