/**
 * PanelControls Component
 * Production-grade panel visibility toggles with responsive design
 */

'use client';

import { Button } from '@/components/design-system/Button';

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
        <Button 
          variant="ghost"
          size="sm"
          onClick={onToggleOriginalBlog}
          aria-label="Toggle original blog panel"
          title="Toggle original blog panel"
          className={showOriginalBlog ? 'bg-blue-500/20 border-blue-400/50' : ''}
        >
          👁 Original
        </Button>
      )}
      
      {/* Generated Blog Toggle (only if blog messages exist) */}
      {hasBlogMessages && (
        <Button 
          variant="ghost"
          size="sm"
          onClick={onToggleGeneratedBlog}
          aria-label="Toggle generated blog panel"
          title="Toggle generated blog panel"
          className={showGeneratedBlog ? 'bg-blue-500/20 border-blue-400/50' : ''}
        >
          📝 Blog
        </Button>
      )}
    </div>
  );
};
