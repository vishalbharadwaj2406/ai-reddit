'use client'

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';

const WelcomeHero: React.FC = () => {
  return (
    <div className="welcome-hero-card">
      {/* Lotus Logo */}
      <Image
        src="/images/blue_lotus_logo.png"
        unoptimized
        alt="AI Social Lotus Logo"
        className="welcome-logo"
        width={120}
        height={120}
        priority
      />
      
      {/* App Title */}
      <h1 className="welcome-title">
        AI SOCIAL
      </h1>
      
      {/* Prominent Tagline */}
      <p className="welcome-tagline">
        Diverse Thoughts, Unified Wisdom
      </p>
      
      {/* Concise Welcome Message */}
      <div className="welcome-message">
        <p>
          Join a community where diverse thoughts create unified wisdom through AI-powered conversations.
        </p>
      </div>
      
      {/* Call to Action Buttons */}
      <div className="welcome-buttons">
        <Link 
          href="/api/auth/signin" 
          className="welcome-btn-primary"
          aria-label="Sign in to AI Social"
        >
          Sign In
        </Link>
        <Link 
          href="/about" 
          className="welcome-btn-secondary"
          aria-label="Learn more about AI Social"
        >
          Learn More
        </Link>
      </div>
    </div>
  );
};

export default WelcomeHero;
