/**
 * PanelControls Component
 * Production-grade panel visibility toggles with responsive design
 */

'use client';

interface PanelControlsProps {
  // Panel states
  showOriginalBlog: boolean;
  showGeneratedBlog: boolean;
  
  // Panel availability
  isForked: boolean;
  hasBlogMessages: boolean;
  
  // Actions
  onToggleOriginalBlog: () => void;
  onToggleGeneratedBlog: () => void;
  
  // Mobile support
  isMobile?: boolean;
}

export const PanelControls: React.FC<PanelControlsProps> = ({
  showOriginalBlog,
  showGeneratedBlog,
  isForked,
  hasBlogMessages,
  onToggleOriginalBlog,
  onToggleGeneratedBlog,
  isMobile = false,
}) => {
  // Don't render if no panels are available
  if (!isForked && !hasBlogMessages) {
    return null;
  }

  return (
    <div className={`absolute ${isMobile ? 'bottom-20 right-4' : 'top-20 right-4'} z-10 flex ${isMobile ? 'flex-row gap-2' : 'flex-col gap-2'}`}>
      {/* Original Blog Toggle (only if forked) */}
      {isForked && (
        <button 
          className={`glass-button-toggle px-3 py-2 text-xs transition-all duration-200 ${showOriginalBlog ? 'active bg-blue-500/20 border-blue-400/50' : ''}`}
          onClick={onToggleOriginalBlog}
          aria-label="Toggle original blog panel"
          title="Toggle original blog panel"
        >
          👁 Original
        </button>
      )}
      
      {/* Generated Blog Toggle (only if blog messages exist) */}
      {hasBlogMessages && (
        <button 
          className={`glass-button-toggle px-3 py-2 text-xs transition-all duration-200 ${showGeneratedBlog ? 'active bg-blue-500/20 border-blue-400/50' : ''}`}
          onClick={onToggleGeneratedBlog}
          aria-label="Toggle generated blog panel"
          title="Toggle generated blog panel"
        >
          📝 Blog
        </button>
      )}
    </div>
  );
};
