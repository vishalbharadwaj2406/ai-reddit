"use client";

import React, { useEffect, useRef, useState } from 'react';
import { signIn } from 'next-auth/react';
import styles from './LoginModal.module.css';

export default function LoginModal() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);

  // Listen for open-login-modal event
  useEffect(() => {
    const handler = () => setOpen(true);
    window.addEventListener('open-login-modal', handler);
    return () => window.removeEventListener('open-login-modal', handler);
  }, []);

  // Close on outside click or ESC
  useEffect(() => {
    if (!open) return;
    function handleClick(e: MouseEvent) {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleEsc);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleEsc);
    };
  }, [open]);

  // Handle Google sign in using NextAuth
  const handleGoogleSignIn = async () => {
    setLoading(true);
    try {
      await signIn('google', {
        callbackUrl: '/feed', // Redirect to feed after login
      });
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setLoading(false);
      setOpen(false);
    }
  };

  if (!open) return null;

  return (
    <div className={styles.backdrop}>
      <div className={styles.modal} ref={modalRef} role="dialog" aria-modal="true">
        <h2 className={styles.title}>Sign in to AI Social</h2>
        
        <button
          onClick={handleGoogleSignIn}
          disabled={loading}
          className={styles.googleSignInButton}
        >
          {loading ? (
            <div className={styles.spinner}></div>
          ) : (
            <>
              <svg className={styles.googleIcon} viewBox="0 0 24 24" width="20" height="20">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Sign in with Google
            </>
          )}
        </button>

        <button 
          className={styles.closeBtn} 
          onClick={() => setOpen(false)} 
          aria-label="Close modal"
        >
          &times;
        </button>
      </div>
    </div>
  );
}
