'use client'

import React from 'react'
import Link from 'next/link'
import styles from './Header.module.css'
import Image from 'next/image'
import { useSessionContext } from '../providers/SessionWrapper';
import { logout, redirectToLogin } from '../../lib/auth/session';
import { useState, useRef, useEffect } from 'react';
import { Menu, Search } from 'lucide-react'
import { useSidebarStore } from '@/lib/stores/sidebarStore'
import { useHeaderStore } from '@/lib/stores/headerStore'
import { usePathname, useRouter } from 'next/navigation'
import { Input } from '@/components/design-system/Input'
import NewChatButton from '@/components/design-system/NewChatButton'
import ProfilePicture from '../ui/ProfilePicture';
import { WithSearchParams } from './WithSearchParams';
import { Button } from '@/components/design-system/Button';

interface HeaderProps {
  className?: string
}

function HeaderContent({ searchParams, className = '' }: HeaderProps & { searchParams: URLSearchParams }) {
  const session = useSessionContext();
  const pathname = usePathname();
  const router = useRouter();
  const { toggleExpanded, toggleMobile } = useSidebarStore()
  const { conversationTitle } = useHeaderStore()
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  // Check if we're on conversations page vs individual conversation
  const isConversationsPage = pathname === '/conversations';
  const isIndividualConversation = pathname.startsWith('/conversations/') && pathname !== '/conversations';

  useEffect(() => {
    if (!dropdownOpen) return;
    function handleClick(e: MouseEvent) {
      const target = e.target as Node;
      const isInsideDropdown = dropdownRef.current && dropdownRef.current.contains(target);
      const isInsideProfile = profileRef.current && profileRef.current.contains(target);
      if (!isInsideDropdown && !isInsideProfile) {
        setDropdownOpen(false);
      }
    }
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setDropdownOpen(false);
    }
    document.addEventListener('click', handleClick);
    document.addEventListener('keydown', handleEsc);
    return () => {
      document.removeEventListener('click', handleClick);
      document.removeEventListener('keydown', handleEsc);
    };
  }, [dropdownOpen]);

  const handleSignOut = () => { logout(); };

  const handleHamburgerClick = () => {
    if (window.innerWidth <= 767) {
      toggleMobile()
    } else {
      toggleExpanded()
    }
  }

  const handleProfileClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDropdownOpen(prev => !prev);
  };

  return (
    <header className={`${styles.header} ${className}`}>
      <nav className={styles.nav}>
        <button
          className={styles.hamburgerButton}
          onClick={handleHamburgerClick}
          aria-label="Toggle navigation menu"
        >
          <Menu className={styles.hamburgerIcon} />
        </button>
        
        {/* Clickable Logo + Title directing to feed page */}
        <Link href="/feed" className={styles.logoLink} aria-label="Go to AI Social feed">
          <div className={styles.logo}>
            <Image
              src="/images/blue_lotus_logo.png"
              alt="AI Social Logo"
              className={styles.logoImage}
              width={40}
              height={40}
              priority
            />
            <span className={styles.logoText}>AI Social</span>
          </div>
        </Link>

        {/* Context-aware center content */}
        {isConversationsPage && (
          <div className={styles.centerContent}>
            <Input
              type="text"
              placeholder="Search conversations..."
              defaultValue={searchParams.get('search') || ''}
              onChange={(e) => {
                const searchValue = e.target.value;
                const params = new URLSearchParams(searchParams.toString());
                if (searchValue) {
                  params.set('search', searchValue);
                } else {
                  params.delete('search');
                }
                router.replace(`/conversations?${params.toString()}`, { scroll: false });
              }}
              leftIcon={<Search size={18} />}
              className={styles.headerSearch}
              data-conversations-search
              aria-label="Search conversations"
            />
          </div>
        )}

        {isIndividualConversation && (
          <div className={styles.centerContent}>
            <div className={styles.conversationTitle}>
              <span className={styles.titleText}>
                {conversationTitle || 'Loading conversation...'}
              </span>
            </div>
          </div>
        )}

        {/* Right side content */}
        <div className={styles.rightContent}>
          {/* New Chat button - only on conversations list page */}
          {isConversationsPage && session.isAuthenticated && (
            <NewChatButton variant="header" />
          )}

          {/* Profile section */}
          {!session.isAuthenticated ? (
          <Button
            variant="primary"
            size="md"
            onClick={() => redirectToLogin(pathname)}
            aria-label="Sign in to AI Social"
          >
            Sign In
          </Button>
        ) : (
          <div style={{ position: 'relative' }}>
            <div
              ref={profileRef}
              className={styles.profilePicWrapper}
              tabIndex={0}
              aria-haspopup="true"
              aria-expanded={dropdownOpen}
              onClick={handleProfileClick}
              onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); setDropdownOpen(prev => !prev); } }}
              style={{ cursor: 'pointer' }}
            >
              <ProfilePicture
                src={session.user?.profile_picture}
                alt={session.user?.user_name || 'Profile'}
                size="md"
                clickable={true}
              />
            </div>
            {dropdownOpen && (
              <div className={styles.profileDropdown} ref={dropdownRef} role="menu">
                <div className={styles.profileDropdownUserInfo}>
                  <div className={styles.profileDropdownName}>{session.user?.user_name}</div>
                  <div className={styles.profileDropdownUsername}>{session.user?.email}</div>
                </div>
                <div className={styles.profileDropdownActions}>
                  <button className={styles.profileDropdownButton} role="menuitem">
                    <svg className={styles.profileDropdownIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Profile
                  </button>
                  <button className={styles.profileDropdownButton} role="menuitem">
                    <svg className={styles.profileDropdownIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Settings
                  </button>
                  <button className={`${styles.profileDropdownButton} ${styles.signOut}`} onClick={handleSignOut} role="menuitem">
                    <svg className={styles.profileDropdownIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        </div>
      </nav>
    </header>
  );
}

export default function Header({ className = '' }: HeaderProps) {
  return (
    <WithSearchParams>
      {(searchParams) => <HeaderContent searchParams={searchParams} className={className} />}
    </WithSearchParams>
  );
}
