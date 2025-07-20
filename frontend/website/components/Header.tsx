'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useSession, signIn, signOut } from 'next-auth/react'
import Image from 'next/image'
import { User, LogOut } from 'lucide-react'

interface HeaderProps {
  className?: string
}

export default function Header({ className = '' }: HeaderProps) {
  const { data: session, status } = useSession()
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowProfileMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleProfileClick = () => {
    if (session) {
      setShowProfileMenu(!showProfileMenu)
    } else {
      signIn('google')
    }
  }

  const handleSignOut = () => {
    setShowProfileMenu(false)
    signOut({ callbackUrl: '/' })
  }

  return (
    <>
      <header className={`header header-glass ${className}`}>
        <nav className="nav">
          {/* Logo Section */}
          <a href="/feed" className="logo">
            <img 
              src="/images/blue_lotus_logo.png" 
              alt="AI Social Logo" 
              className="logo-image" 
              onError={(e) => {
                const target = e.target as HTMLImageElement
                target.style.display = 'none'
              }}
            />
            <span className="logo-text">AI Social</span>
          </a>

          {/* Navigation Items */}
          <div className="nav-items">
            <a href="/feed" className="nav-item">Feed</a>
            <a href="/conversations" className="nav-item">Conversations</a>
            
            {/* Profile Section */}
            <div className="profile-section" ref={menuRef}>
              {session ? (
                <>
                  <button 
                    onClick={handleProfileClick}
                    className="profile-button"
                  >
                    {session.user?.image ? (
                      <div className="profile-image-wrapper">
                        <Image
                          src={session.user.image}
                          alt="Profile"
                          width={40}
                          height={40}
                          className="profile-image-inner"
                          style={{
                            borderRadius: '50%',
                            objectFit: 'cover',
                          }}
                          priority
                        />
                      </div>
                    ) : (
                      <div className="profile-avatar">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </button>

                  {/* Profile Dropdown */}
                  {showProfileMenu && (
                    <div className="profile-dropdown header-glass">
                      <div className="profile-info">
                        <div className="profile-details">
                          <p className="profile-name">
                            {session.user?.name || session.user?.email || 'User'}
                          </p>
                          <p className="profile-email">{session.user?.email}</p>
                        </div>
                      </div>
                      <div className="dropdown-divider"></div>
                      <button
                        onClick={handleSignOut}
                        className="sign-out-button"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <button 
                  onClick={handleProfileClick}
                  className="sign-in-button"
                  disabled={status === 'loading'}
                >
                  {status === 'loading' ? 'Loading...' : 'Sign In'}
                </button>
              )}
            </div>
          </div>
        </nav>
      </header>
      
      {/* Demo Content for Testing Glass Effect */}
      <div className="demo-content">
        <div className="content-section">
          <h1>Welcome to AI Social</h1>
          <p>Scroll to see the beautiful glass morphism effect of the header.</p>
          <div className="demo-cards">
            <div className="demo-card">Sample Content 1</div>
            <div className="demo-card">Sample Content 2</div>
            <div className="demo-card">Sample Content 3</div>
          </div>
        </div>
      </div>

      <style jsx>{`
        /* Override Next.js Image default styles for profile images */
        :global(.profile-image-inner) {
          border-radius: 50% !important;
          object-fit: cover !important;
        }

        /* HEADER POSITIONING ONLY - Glass effect comes from global CSS */
        .header {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 100;
          padding: 12px 32px;
          border-bottom: 1px solid rgba(59, 130, 246, 0.25);
          border-radius: 0 0 24px 24px;
        }

        /* DROPDOWN POSITIONING ONLY - Glass effect comes from global CSS */
        .profile-dropdown {
          position: absolute;
          top: calc(100% + 12px);
          right: 0;
          border-radius: 24px;
          min-width: 260px;
          animation: dropdownFadeIn 0.2s ease-out;
          z-index: 101;
          overflow: hidden;
        }

        /* Auto-adjust content below header */
        .demo-content {
          margin-top: 0; /* Remove margin since body has padding */
          min-height: 200vh;
          background: linear-gradient(135deg, #000000, #1E3A8A);
          padding: 48px;
        }

        .nav {
          display: flex;
          justify-content: space-between;
          align-items: center;
          max-width: 1400px;
          margin: 0 auto;
          position: relative;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 24px;
          font-weight: 800;
          position: relative;
          padding: 8px 16px;
          border-radius: 16px;
          text-decoration: none;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        /* Symmetrical Glow Effect for Logo - No Movement */
        .logo::before {
          content: '';
          position: absolute;
          top: -6px;
          left: -12px;
          right: -12px;
          bottom: -6px;
          background: radial-gradient(ellipse, rgba(59, 130, 246, 0.1) 0%, transparent 60%);
          border-radius: 20px;
          z-index: -1;
          transition: opacity 0.3s ease;
        }

        .logo:hover::before {
          opacity: 1;
        }

        .logo-text {
          background: linear-gradient(135deg, #E6F3FF, #3B82F6, #E6F3FF, #60A5FA, #E6F3FF);
          background-size: 400% 400%;
          background-clip: text;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          color: transparent;
          filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.5));
          animation: gradientShift 25s ease-in-out infinite;
        }

        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          25% { background-position: 100% 50%; }
          50% { background-position: 100% 100%; }
          75% { background-position: 0% 100%; }
          100% { background-position: 0% 50%; }
        }

        .logo-image {
          width: 36px;
          height: 36px;
          object-fit: contain;
          filter: drop-shadow(0 0 12px rgba(59, 130, 246, 0.4));
        }

        .nav-items {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .nav-item {
          color: rgba(255, 255, 255, 0.7);
          text-decoration: none;
          font-weight: 600;
          font-size: 15px;
          transition: all 0.3s ease;
          padding: 8px 16px;
          border-radius: 16px;
          background: transparent;
        }

        .nav-item:hover {
          color: #3B82F6;
          filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.4));
        }

        .profile-section {
          position: relative;
          overflow: visible;
        }

        .profile-button {
          background: transparent;
          border: none;
          cursor: pointer;
          padding: 4px;
          border-radius: 50%;
          transition: all 0.3s ease;
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .profile-image-wrapper {
          width: 46px;
          height: 46px;
          border-radius: 50%;
          position: relative;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(45deg, #E6F3FF, #3B82F6, #E6F3FF, #60A5FA);
          background-size: 400% 400%;
          animation: gradientShift 15s ease-in-out infinite;
          padding: 3px;
        }

        .profile-image-wrapper:hover {
          filter: drop-shadow(0 0 12px rgba(59, 130, 246, 0.6));
        }

        .profile-image-inner {
          width: 40px !important;
          height: 40px !important;
          border-radius: 50% !important;
          object-fit: cover !important;
          border: none !important;
          position: relative !important;
          z-index: 2 !important;
          display: block !important;
          overflow: hidden !important;
        }

        .profile-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(59, 130, 246, 0.3));
          border: 3px solid rgba(59, 130, 246, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          backdrop-filter: blur(8px);
          transition: all 0.3s ease;
          box-shadow: 
            0 0 20px rgba(59, 130, 246, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .profile-avatar:hover {
          border-color: rgba(59, 130, 246, 0.8);
          background: linear-gradient(135deg, rgba(30, 58, 138, 0.5), rgba(59, 130, 246, 0.4));
          box-shadow: 
            0 0 25px rgba(59, 130, 246, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
          transform: scale(1.05);
        }

        @keyframes dropdownFadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .profile-info {
          padding: 20px;
          background: transparent;
        }

        .profile-details {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .profile-name {
          color: rgba(255, 255, 255, 0.95);
          font-weight: 700;
          font-size: 16px;
          margin: 0;
        }

        .profile-email {
          color: rgba(255, 255, 255, 0.6);
          font-size: 14px;
          margin: 0;
        }

        .dropdown-divider {
          height: 1px;
          background: linear-gradient(90deg, 
            transparent, 
            rgba(59, 130, 246, 0.3), 
            transparent);
          margin: 0 16px;
        }

        .sign-out-button {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px 20px;
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.9);
          font-weight: 500;
          font-size: 15px;
          cursor: pointer;
          transition: all 0.3s ease;
          border-radius: 0 0 22px 22px;
        }

        .sign-out-button:hover {
          background: rgba(59, 130, 246, 0.1);
          color: #60A5FA;
        }

        .sign-in-button {
          background: rgba(255, 255, 255, 0.1);
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 16px;
          padding: 12px 24px;
          color: rgba(255, 255, 255, 0.95);
          font-weight: 600;
          font-size: 15px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .sign-in-button:hover {
          background: rgba(255, 255, 255, 0.15);
          border-color: rgba(255, 255, 255, 0.6);
          color: rgba(255, 255, 255, 1);
        }

        .sign-in-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        /* Demo Content Styling */
        .content-section {
          max-width: 1200px;
          margin: 0 auto;
          text-align: center;
        }

        .content-section h1 {
          font-size: 48px;
          font-weight: 800;
          color: #E6F3FF;
          margin-bottom: 24px;
          background: linear-gradient(135deg, #E6F3FF, #3B82F6, #E6F3FF);
          background-clip: text;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .content-section p {
          font-size: 18px;
          color: rgba(255, 255, 255, 0.7);
          margin-bottom: 48px;
        }

        .demo-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 24px;
          margin-top: 48px;
        }

        .demo-card {
          padding: 32px;
          background: rgba(255, 255, 255, 0.03);
          backdrop-filter: blur(32px) saturate(180%);
          border: 2px solid rgba(59, 130, 246, 0.2);
          border-radius: 24px;
          color: rgba(255, 255, 255, 0.9);
          font-weight: 600;
          transition: all 0.3s ease;
        }

        .demo-card:hover {
          background: rgba(255, 255, 255, 0.05);
          border-color: rgba(59, 130, 246, 0.4);
          transform: translateY(-4px);
        }

        /* Responsive */
        @media (max-width: 768px) {
          .header {
            padding: 10px 20px;
            border-radius: 0 0 20px 20px;
          }
          
          .logo {
            font-size: 20px;
            gap: 10px;
            padding: 6px 12px;
          }
          
          .logo-image {
            width: 28px;
            height: 28px;
          }
          
          .nav-items {
            gap: 8px;
          }
          
          .nav-item {
            padding: 6px 12px;
            font-size: 14px;
          }
          
          .profile-dropdown {
            min-width: 200px;
          }
        }
      `}</style>
    </>
  )
}
