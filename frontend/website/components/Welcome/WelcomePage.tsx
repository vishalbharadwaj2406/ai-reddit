'use client'

import React from 'react'
import styles from './Welcome.module.css'
import Image from 'next/image'
import Link from 'next/link'

const WelcomePage: React.FC = () => {
  return (
    <>
      {/* Background Pattern */}
      <div className={styles.backgroundPattern} />
      
      {/* Main Container */}
      <div className={styles.container}>
        <div className={styles.heroCard}>
          {/* Lotus Logo */}
          <Image
            src="/images/blue_lotus_logo.png"
            unoptimized
            alt="AI Social Lotus Logo"
            className={styles.logo}
            width={120}
            height={120}
            priority
          />
          
          {/* App Title */}
          <h1 className={styles.title}>
            AI SOCIAL
          </h1>
          
          {/* Prominent Tagline */}
          <p className={styles.tagline}>
            Diverse Thoughts, Unified Wisdom
          </p>
          
          {/* Concise Welcome Message */}
          <div className={styles.message}>
            <p>
              Join a community where diverse thoughts create unified wisdom through AI-powered conversations.
            </p>
          </div>
          
          {/* Call to Action Buttons */}
          <div className={styles.buttons}>
            <button
              className={styles.primaryButton}
              aria-label="Sign in to AI Social"
              onClick={() => window.dispatchEvent(new CustomEvent('open-login-modal'))}
            >
              Sign In
            </button>
            <Link 
              href="/about" 
              className={styles.secondaryButton}
              aria-label="Learn more about AI Social"
            >
              Learn More
            </Link>
          </div>
        </div>
      </div>
    </>
  )
}

export default WelcomePage
