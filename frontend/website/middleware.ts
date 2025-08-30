/**
 * Production-Grade Route Protection Middleware
 * 
 * Simplified middleware that handles route protection without backend calls.
 * Authentication state is managed client-side through SessionWrapper for reliability.
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

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
 * Check if user has session cookie (basic check only)
 */
function hasSessionCookie(request: NextRequest): boolean {
  return request.cookies.has('ai_social_session');
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
 * Production-grade simplified middleware function
 * 
 * This middleware only handles basic route protection without backend authentication calls.
 * All authentication state management is handled client-side through SessionWrapper.
 */
export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  
  // Handle post-authentication URLs with special logic
  const isPostAuth = request.nextUrl.searchParams.has('auth_success') ||
                     request.nextUrl.searchParams.has('auth_timestamp');
  
  if (isPostAuth && pathname === '/') {
    // For post-auth, always allow access to home page - client will handle redirect
    console.log('🎉 Post-auth: Allowing access to home page for client-side handling');
    return NextResponse.next();
  }
  
  // Basic cookie presence check (not validation - client handles that)
  const hasSession = hasSessionCookie(request);

  // Development mode debugging
  if (process.env.NODE_ENV === 'development') {
    console.log(`🚀 Middleware: ${pathname} (session cookie: ${hasSession ? 'present' : 'none'})`);
  }

  // Handle protected routes - redirect to home if no session cookie
  if (isProtectedRoute(pathname)) {
    if (!hasSession) {
      const redirectUrl = getRedirectUrl(request, '/');
      console.log(`🔐 Middleware: Redirecting to home from ${pathname} (no session cookie)`);
      return NextResponse.redirect(redirectUrl);
    }
    // Has session cookie - allow access, client will validate
    return NextResponse.next();
  }

  // Handle auth routes - if has session, redirect to callback or feed
  if (isAuthRoute(pathname)) {
    if (hasSession) {
      const callbackUrl = request.nextUrl.searchParams.get('callbackUrl') || '/feed';
      const redirectUrl = getRedirectUrl(request, callbackUrl);
      console.log(`✅ Middleware: Redirecting authenticated user from ${pathname} to ${callbackUrl}`);
      return NextResponse.redirect(redirectUrl);
    }
  }

  // Allow all other requests
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
