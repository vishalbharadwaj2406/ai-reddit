'use client'

import React from 'react';
import WelcomeHero from './WelcomeHero';

const WelcomePage: React.FC = () => {
  return (
    <>
      {/* Minimal background pattern */}
      <div className="welcome-bg-pattern" />
      
      {/* Main welcome container */}
      <div className="welcome-container">
        {/* Central hero content only */}
        <WelcomeHero />
      </div>
    </>
  );
};

export default WelcomePage;
