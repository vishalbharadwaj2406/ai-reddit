/**
 * AI SOCIAL Welcome Page - Simplified & Clean
 * 
 * Single card layout with standardized button components
 * Professional UX without excessive animations
 */

'use client';

import React from 'react';
import Image from 'next/image';
import { Button } from '@/components/design-system/Button';
import { redirectToLogin } from '@/lib/auth/session';
import styles from './Welcome.module.css';

const WelcomePage: React.FC = () => {
  const handleGetStarted = () => {
    // Navigate to same place as Sign In button - Google OAuth login
    redirectToLogin('/');
  };

  const handleLearnMore = () => {
    // Navigate to about or features page
    window.location.href = '/about';
  };

  return (
    <>
      {/* Background Pattern */}
      <div className={styles.backgroundPattern} />
      
      {/* Main Content */}
      <div className={styles.container}>
        <div className={styles.heroCard}>
          
          {/* Logo */}
          <div className={styles.logoContainer}>
            <Image
              src="/images/blue_lotus_logo.png"
              alt="AI Social Logo"
              width={80}
              height={80}
              className={styles.logo}
              priority
            />
          </div>

          {/* Brand & Title */}
          <h1 className={styles.title}>AI Social</h1>
          <p className={styles.tagline}>Diverse Thoughts, Unified Wisdom</p>
          
          {/* Main Message */}
          <p className={styles.message}>
            Tired of shallow social media? Join conversations that challenge, inspire, and evolve your thinking.
          </p>

          {/* Feature Cards */}
          <div className={styles.featuresGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🤖</div>
              <h3 className={styles.featureTitle}>AI-Enhanced Discussions</h3>
              <p className={styles.featureDescription}>
                AI helps you powerfully articulate ideas worth sharing.
              </p>
            </div>
            
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🌍</div>
              <h3 className={styles.featureTitle}>Global Community</h3>
              <p className={styles.featureDescription}>
                Connect with diverse voices from around the world
              </p>
            </div>
            
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>💡</div>
              <h3 className={styles.featureTitle}>Collaborative Wisdom</h3>
              <p className={styles.featureDescription}>
                Build knowledge together through meaningful dialogue
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className={styles.buttonsContainer}>
            <Button
              variant="primary"
              size="lg"
              onClick={handleGetStarted}
            >
              Get Started
            </Button>
            <Button
              variant="secondary"
              size="lg"
              onClick={handleLearnMore}
            >
              Learn More
            </Button>
          </div>
          
        </div>
      </div>
    </>
  );
};

export default WelcomePage;
