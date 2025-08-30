/**
 * Production Authentication Test Component
 * 
 * This component helps test and validate the authentication flow
 */
'use client'

import React, { useState, useEffect, useCallback } from 'react';
import { getSessionStatus, redirectToLogin, logout } from '../../../lib/auth/session';
import type { SessionStatus } from '../../../lib/auth/session';

interface AuthTestProps {
  className?: string;
}

export default function AuthTest({ className = '' }: AuthTestProps) {
  const [sessionStatus, setSessionStatus] = useState<SessionStatus>({
    isAuthenticated: false,
    user: null,
    loading: true
  });
  const [testResults, setTestResults] = useState<string[]>([]);

  const addTestResult = (result: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`]);
  };

  const checkSession = useCallback(async () => {
    try {
      addTestResult('🔍 Testing session validation...');
      const status = await getSessionStatus(true); // Force refresh
      setSessionStatus(status);
      addTestResult(`✅ Session check complete: ${status.isAuthenticated ? 'AUTHENTICATED' : 'NOT AUTHENTICATED'}`);
      if (status.user) {
        addTestResult(`👤 User: ${status.user.user_name} (${status.user.email})`);
      }
    } catch (error) {
      addTestResult(`❌ Session check failed: ${error}`);
    }
  }, []);

  const testLogin = () => {
    addTestResult('🔐 Initiating OAuth login...');
    redirectToLogin('/feed');
  };

  const testLogout = async () => {
    try {
      addTestResult('🚪 Testing logout...');
      await logout();
      addTestResult('✅ Logout successful');
      await checkSession(); // Refresh session after logout
    } catch (error) {
      addTestResult(`❌ Logout failed: ${error}`);
    }
  };

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  return (
    <div className={`p-6 border rounded-lg bg-gray-50 ${className}`}>
      <h3 className="text-lg font-semibold mb-4">🧪 Authentication Test Panel</h3>
      
      {/* Session Status */}
      <div className="mb-4 p-3 border rounded bg-white">
        <h4 className="font-medium mb-2">Current Session Status:</h4>
        <div className="space-y-1 text-sm">
          <div>Status: <span className={sessionStatus.isAuthenticated ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
            {sessionStatus.loading ? 'Loading...' : sessionStatus.isAuthenticated ? 'AUTHENTICATED ✅' : 'NOT AUTHENTICATED ❌'}
          </span></div>
          {sessionStatus.user && (
            <>
              <div>User: <span className="font-medium">{sessionStatus.user.user_name}</span></div>
              <div>Email: <span className="font-medium">{sessionStatus.user.email}</span></div>
              <div>User ID: <span className="font-mono text-xs">{sessionStatus.user.user_id}</span></div>
            </>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mb-4 flex gap-2 flex-wrap">
        <button 
          onClick={checkSession}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
        >
          🔍 Check Session
        </button>
        <button 
          onClick={testLogin}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
        >
          🔐 Test Login
        </button>
        <button 
          onClick={testLogout}
          disabled={!sessionStatus.isAuthenticated}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:bg-gray-400 text-sm"
        >
          🚪 Test Logout
        </button>
        <button 
          onClick={() => setTestResults([])}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
        >
          🗑️ Clear Log
        </button>
      </div>

      {/* Test Results Log */}
      <div className="bg-black text-green-400 p-3 rounded font-mono text-xs max-h-60 overflow-y-auto">
        <div className="mb-2 text-white">🔍 Authentication Test Log:</div>
        {testResults.length === 0 ? (
          <div className="text-gray-500">No test results yet...</div>
        ) : (
          testResults.map((result, index) => (
            <div key={index} className="mb-1">{result}</div>
          ))
        )}
      </div>
    </div>
  );
}
