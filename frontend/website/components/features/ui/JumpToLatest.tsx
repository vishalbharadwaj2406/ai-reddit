/**
 * JumpToLatest Component
 * Production-grade scroll-to-bottom button with glass morphism
 */

'use client';

interface JumpToLatestProps {
  onJumpToLatest: () => void;
  className?: string;
}

export const JumpToLatest: React.FC<JumpToLatestProps> = ({
  onJumpToLatest,
  className = '',
}) => {
  return (
    <button
      onClick={onJumpToLatest}
      className={`w-7 h-7 rounded-full bg-white/5 backdrop-blur-xl border border-white/10 flex items-center justify-center hover:bg-white/10 hover:border-white/20 transition-all duration-300 shadow-2xl hover:shadow-blue-500/20 hover:scale-110 ${className}`}
      aria-label="Scroll to latest message"
      style={{ 
        backdropFilter: 'blur(20px)',
        background: 'rgba(255, 255, 255, 0.05)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.1)'
      }}
    >
      <svg className="w-3 h-3 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 14l-7 7m0 0l-7-7" />
      </svg>
    </button>
  );
};
