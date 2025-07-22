"use client";

import { useEffect } from 'react';

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!;

declare global {
  interface Window {
    google?: {
      accounts?: {
        id?: {
          initialize: (config: any) => void;
          renderButton: (element: HTMLElement, options: any) => void;
        };
      };
    };
  }
}

export default function GoogleTest() {
  useEffect(() => {
    console.log('=== GOOGLE TEST PAGE DEBUG ===');
    console.log('Current URL:', window.location.href);
    console.log('Current Origin:', window.location.origin);
    console.log('Client ID:', GOOGLE_CLIENT_ID);
    console.log('Client ID exists:', !!GOOGLE_CLIENT_ID);
    console.log('================================');

    // Load Google script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.onload = () => {
      console.log('Google script loaded');
      
      if (window.google?.accounts?.id) {
        console.log('Google accounts available');
        
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: (response: any) => {
            console.log('Google callback response:', response);
          },
          ux_mode: 'popup',
        });

        const buttonElement = document.getElementById('google-test-btn');
        if (buttonElement) {
          window.google.accounts.id.renderButton(buttonElement, {
            theme: 'outline',
            size: 'large',
            width: 260
          });
        }
      }
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <h1>Google OAuth Test Page</h1>
      <p>Current Origin: {typeof window !== 'undefined' ? window.location.origin : 'Loading...'}</p>
      <p>Client ID: {GOOGLE_CLIENT_ID}</p>
      <p style={{ background: '#333', padding: '10px', borderRadius: '5px' }}>
        <strong>Try with IP instead:</strong><br/>
        <a href="http://127.0.0.1:3000/google-test" style={{ color: '#60A5FA' }}>
          http://127.0.0.1:3000/google-test
        </a>
      </p>
      <div id="google-test-btn" style={{ margin: '20px auto' }}></div>
      <p>Check console for detailed logs</p>
    </div>
  );
} 