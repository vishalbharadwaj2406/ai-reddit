/**
 * BlogPanelHeader Component
 * Minimal header for blog panel (Claude-style)
 */

'use client';

import { Button } from '@/components/design-system/Button';

interface BlogPanelHeaderProps {
  title: string;
  onEditBlog: () => void;
  onClose?: () => void;
}

export const BlogPanelHeader: React.FC<BlogPanelHeaderProps> = ({
  title,
  onEditBlog,
  onClose,
}) => {
  return (
    <div className="flex items-center justify-end gap-2 p-3 border-b border-gray-700/30 bg-black">
      <Button
        variant="primary"
        size="sm"
        onClick={onEditBlog}
        className="text-xs"
      >
        Edit & Post
      </Button>
      {onClose && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="text-xs w-8 h-8 p-0"
        >
          ✕
        </Button>
      )}
    </div>
  );
};
