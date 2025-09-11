/**
 * BlogMessageButton Component
 * Clean button for blog messages (like Claude's artifact button)
 */

'use client';

import { Button } from '@/components/design-system/Button';

interface BlogMessageButtonProps {
  onClick: () => void;
  isActive?: boolean;
}

export const BlogMessageButton: React.FC<BlogMessageButtonProps> = ({
  onClick,
  isActive = false,
}) => {
  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={onClick}
      className={`
        mt-2 
        ${isActive 
          ? 'bg-blue-600/20 border-blue-500/40 text-blue-300' 
          : 'bg-white/5 border-white/10 text-gray-300 hover:text-white'
        }
      `}
    >
      View Blog
    </Button>
  );
};
