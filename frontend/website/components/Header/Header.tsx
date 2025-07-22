'use client'

import React from 'react'
import styles from './Header.module.css'
import Image from 'next/image'
import { useSession, signOut } from 'next-auth/react';
import { useState, useRef, useEffect } from 'react';

interface HeaderProps {
  className?: string
}

export default function Header({ className = '' }: HeaderProps) {
  // Use NextAuth session
  const { data: session, status } = useSession();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click or ESC
  useEffect(() => {
    if (!dropdownOpen) return;
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setDropdownOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleEsc);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleEsc);
    };
  }, [dropdownOpen]);

  const handleSignOut = () => {
    signOut({ callbackUrl: '/' });
  };

  return (
    <header className={`${styles.header} ${className}`}>
      <nav className={styles.nav}>
        {/* Logo Section */}
        <div className={styles.logo}>
          <Image
            src="/images/blue_lotus_logo.png"
            alt="AI Social Logo"
            className={styles.logoImage}
            width={40}
            height={40}
            priority
          />
          <span className={styles.logoText}>
            AI Social
          </span>
        </div>

        {/* Navigation Items - Context-aware based on authentication state */}
        <div className={styles.navItems}>
          {!session?.user ? (
            // Non-authenticated: Show only Sign In button
            <button
              className={styles.signInButton}
              aria-label="Sign in to AI Social"
              onClick={() => window.dispatchEvent(new CustomEvent('open-login-modal'))}
            >
              Sign In
            </button>
          ) : (
            // Authenticated: Show profile picture with dropdown
            <div style={{ position: 'relative' }}>
              <div
                className={styles.profilePicWrapper}
                tabIndex={0}
                aria-haspopup="true"
                aria-expanded={dropdownOpen}
                onClick={() => setDropdownOpen(v => !v)}
                onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') setDropdownOpen(v => !v); }}
                style={{ cursor: 'pointer' }}
              >
                <Image
                  src={session.user.image || '/images/blue_lotus_logo.png'}
                  alt={session.user.name || 'Profile'}
                  className={styles.profilePic}
                  width={40}
                  height={40}
                />
              </div>
              {dropdownOpen && (
                <div className={styles.profileDropdown} ref={dropdownRef} role="menu">
                  <div className={styles.profileDropdownName}>{session.user.name}</div>
                  <div className={styles.profileDropdownUsername}>{session.user.email}</div>
                  <hr className={styles.profileDropdownDivider} />
                  <button
                    className={styles.profileDropdownSignOut}
                    onClick={handleSignOut}
                    role="menuitem"
                  >
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
