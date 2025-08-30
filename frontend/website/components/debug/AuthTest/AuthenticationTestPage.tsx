'use client'

import React, { useState, useEffect, useCallback } from 'react';

interface AuthTestData {
  authenticated: boolean;
  user: {
    user_id: string;
    user_name: string;
    email: string;
    profile_picture?: string;
    is_private: boolean;
    created_at: string;
  } | null;
  debug?: {
    timestamp: string;
    host: string;
    user_agent: string;
    cookies_received: string[];
    session_cookie_name: string;
    session_cookie_present: boolean;
    total_cookies: number;
    request_url: string;
  };
  failure_reason?: string;
  session_token_length?: number;
  available_cookies?: Record<string, string>;
}

interface CookieTestData {
  test_cookie_found: boolean;
  test_cookie_value: string;
  all_cookies: Record<string, string>;
  session_cookie_present: boolean;
  host: string;
  timestamp: string;
}

export default function AuthenticationTestPage() {
  const [sessionData, setSessionData] = useState<AuthTestData | null>(null);
  const [cookieTestData, setCookieTestData] = useState<CookieTestData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);
  const [authTimestamp, setAuthTimestamp] = useState<string | null>(null);

  // Handle client-side mounting and URL parameter extraction
  useEffect(() => {
    setMounted(true);
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      setAuthSuccess(urlParams.get('auth_success'));
      setAuthTimestamp(urlParams.get('auth_timestamp'));
    }
  }, []);

  const checkSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/auth/session', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      setSessionData(data);
    } catch (err) {
      setError(`Session check failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }, []); // No dependencies needed for this function

  // Auto-check session on mount
  useEffect(() => {
    if (mounted) {
      checkSession();
    }
  }, [mounted, checkSession]); // Include checkSession in dependencies

  const testCookieSet = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/auth/test-cookie', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      console.log('Cookie set response:', data);
      
      // Wait a moment then check if cookie was received
      setTimeout(async () => {
        const checkResponse = await fetch('/api/v1/auth/test-cookie', {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const checkData = await checkResponse.json();
        setCookieTestData(checkData);
      }, 100);
    } catch (err) {
      setError(`Cookie test failed: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const startGoogleLogin = () => {
    if (typeof window !== 'undefined') {
      window.location.href = '/api/v1/auth/google/login?return_url=/auth-test';
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
      if (typeof window !== 'undefined') {
        window.location.reload();
      }
    } catch (err) {
      setError(`Logout failed: ${err}`);
    }
  };

  // Show loading state until mounted
  if (!mounted) {
    return (
      <div className="max-w-4xl mx-auto p-6 bg-white">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">
          🔧 Authentication Comprehensive Test Suite
        </h1>
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">Initializing test suite...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">
        🔧 Authentication Comprehensive Test Suite
      </h1>

      {/* URL Parameters Detection */}
      {authSuccess && (
        <div className="mb-6 p-4 bg-green-100 border border-green-400 rounded">
          <h3 className="font-semibold text-green-800">✅ OAuth Success Detected</h3>
          <p className="text-green-700">
            Auth success: {authSuccess}, Timestamp: {authTimestamp}
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-100 border border-red-400 rounded">
          <h3 className="font-semibold text-red-800">❌ Error</h3>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mb-6 space-x-4">
        <button
          onClick={checkSession}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Loading...' : '🔍 Check Session'}
        </button>
        
        <button
          onClick={testCookieSet}
          disabled={loading}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
        >
          🍪 Test Cookie Setting
        </button>
        
        <button
          onClick={startGoogleLogin}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          🔐 Start Google Login
        </button>
        
        {sessionData?.authenticated && (
          <button
            onClick={logout}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            🚪 Logout
          </button>
        )}
      </div>

      {/* Session Status */}
      <div className="mb-6 p-4 border rounded">
        <h2 className="text-xl font-semibold mb-3">📊 Session Status</h2>
        {sessionData ? (
          <div className="space-y-2">
            <div className={`p-3 rounded ${sessionData.authenticated ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              <strong>Authentication Status:</strong> {sessionData.authenticated ? '✅ Authenticated' : '❌ Not Authenticated'}
            </div>
            
            {sessionData.authenticated && sessionData.user && (
              <div className="p-3 bg-blue-100 text-blue-800 rounded">
                <strong>User:</strong> {sessionData.user.user_name} ({sessionData.user.email})
              </div>
            )}
            
            {!sessionData.authenticated && sessionData.failure_reason && (
              <div className="p-3 bg-yellow-100 text-yellow-800 rounded">
                <strong>Failure Reason:</strong> {sessionData.failure_reason}
              </div>
            )}
            
            {sessionData.session_token_length !== undefined && (
              <div className="text-sm text-gray-600">
                <strong>Session Token Length:</strong> {sessionData.session_token_length} characters
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500">No session data available</p>
        )}
      </div>

      {/* Debug Information */}
      {sessionData?.debug && (
        <div className="mb-6 p-4 border rounded">
          <h2 className="text-xl font-semibold mb-3">🐛 Debug Information</h2>
          <div className="bg-gray-100 p-3 rounded overflow-auto text-sm">
            <pre>{JSON.stringify(sessionData.debug, null, 2)}</pre>
          </div>
        </div>
      )}

      {/* Cookie Test Results */}
      {cookieTestData && (
        <div className="mb-6 p-4 border rounded">
          <h2 className="text-xl font-semibold mb-3">🍪 Cookie Test Results</h2>
          <div className="space-y-2">
            <div className={`p-3 rounded ${cookieTestData.test_cookie_found ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              <strong>Test Cookie Found:</strong> {cookieTestData.test_cookie_found ? '✅ Yes' : '❌ No'}
            </div>
            
            <div className={`p-3 rounded ${cookieTestData.session_cookie_present ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              <strong>Session Cookie Present:</strong> {cookieTestData.session_cookie_present ? '✅ Yes' : '❌ No'}
            </div>
            
            <div className="p-3 bg-gray-100 rounded">
              <strong>All Cookies:</strong> {Object.keys(cookieTestData.all_cookies).join(', ') || 'None'}
            </div>
            
            <div className="text-sm text-gray-600">
              <strong>Host:</strong> {cookieTestData.host}<br/>
              <strong>Timestamp:</strong> {cookieTestData.timestamp}
            </div>
          </div>
        </div>
      )}

      {/* Available Cookies (if debugging enabled) */}
      {sessionData?.available_cookies && Object.keys(sessionData.available_cookies).length > 0 && (
        <div className="mb-6 p-4 border rounded">
          <h2 className="text-xl font-semibold mb-3">🍪 Available Cookies (Debug Mode)</h2>
          <div className="bg-gray-100 p-3 rounded overflow-auto text-sm">
            <pre>{JSON.stringify(sessionData.available_cookies, null, 2)}</pre>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded">
        <h2 className="text-xl font-semibold mb-3">📋 Test Instructions</h2>
        <ol className="list-decimal list-inside space-y-2 text-sm">
          <li>Click &quot;Check Session&quot; to see current authentication status</li>
          <li>Click &quot;Test Cookie Setting&quot; to verify cookie functionality</li>
          <li>Click &quot;Start Google Login&quot; to test OAuth flow</li>
          <li>After OAuth, you should be redirected back here with success parameters</li>
          <li>Check if session status changes to authenticated</li>
          <li>Use browser dev tools (F12) → Application → Cookies to inspect cookies manually</li>
        </ol>
      </div>
    </div>
  );
}
