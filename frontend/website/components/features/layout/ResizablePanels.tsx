/**
 * ResizablePanels Component
 * 
 * Production-grade custom resizable panel system for chat and blog layout.
 * Built with pure CSS and React - no external dependencies for maximum control.
 * 
 * Key Features:
 * - Claude-like 50/50 default split with 30-70% resize constraints
 * - Perfect height inheritance through clean CSS Grid architecture
 * - Smooth drag resize with mouse events and visual feedback
 * - Graceful single-panel mode when blog is hidden
 * - Persists panel sizes in localStorage for UX continuity
 * 
 * Architecture:
 * - Chat Panel: Full height flex column with overflow-hidden for InputArea positioning
 * - Blog Panel: Full height flex column allowing child components to manage overflow
 * - Resize Handle: Custom implementation with drag constraints
 * 
 * Height Management:
 * - Uses CSS Grid for automatic height distribution
 * - Chat panel: overflow-hidden to prevent scroll conflicts with InputArea
 * - Blog panel: No overflow constraint to allow BlogPanel internal scrolling
 */

'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Panel configuration constants for consistent UX
 */
const PANEL_CONFIG = {
  DEFAULT_CHAT_WIDTH: 50, // percentage
  MIN_CHAT_WIDTH: 30,
  MAX_CHAT_WIDTH: 70,
  STORAGE_KEY: 'ai-reddit-panel-sizes',
} as const;

/**
 * CSS classes for CSS Grid panel system - production-grade styling
 */
const PANEL_STYLES = {
  // Grid container provides perfect height inheritance
  CONTAINER: 'grid h-full transition-all duration-200 ease-out',
  
  // Panel wrappers with automatic height from grid
  CHAT_PANEL: 'overflow-hidden flex flex-col bg-black',
  BLOG_PANEL: 'flex flex-col bg-black border-l border-gray-700/30',
  
  // Clean resize handle with grid positioning
  RESIZE_HANDLE: 'bg-gray-700/30 hover:bg-blue-500/40 cursor-col-resize transition-colors duration-200 focus:outline-none focus:bg-blue-500/50 group',
  RESIZE_INDICATOR: 'h-full w-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200',
  
  // Single panel mode
  SINGLE_PANEL: 'h-full flex flex-col',
} as const;

interface ResizablePanelsProps {
  /** Chat and Blog panel components - order matters [ChatPanel, BlogPanel] */
  children: [React.ReactNode, React.ReactNode];
  /** Controls blog panel visibility and layout mode */
  showBlogPanel: boolean;
  /** Handler for blog panel close action - injected into BlogPanel */
  onCloseBlogPanel?: () => void;
  /** Optional callback for panel resize events with chat panel width percentage */
  onPanelResize?: (chatWidthPercent: number) => void;
}

/**
 * Custom hook for managing CSS Grid panel resize functionality
 * Uses fr units for natural grid behavior with perfect height inheritance
 */
const useGridPanelResize = (
  initialChatWidth: number,
  onResize?: (chatWidthPercent: number) => void
) => {
  const [chatWidth, setChatWidth] = useState(initialChatWidth);
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const startResize = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault();
        const delta = e.key === 'ArrowLeft' ? -2 : 2;
        const newWidth = Math.min(
          Math.max(chatWidth + delta, PANEL_CONFIG.MIN_CHAT_WIDTH),
          PANEL_CONFIG.MAX_CHAT_WIDTH
        );
        setChatWidth(newWidth);
        onResize?.(newWidth);
        
        try {
          localStorage.setItem(PANEL_CONFIG.STORAGE_KEY, newWidth.toString());
        } catch (error) {
          console.warn('Failed to persist panel size:', error);
        }
      }
    },
    [chatWidth, onResize]
  );

  const handleResize = useCallback(
    (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;

      const container = containerRef.current;
      const containerRect = container.getBoundingClientRect();
      const newChatWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Apply constraints
      const constrainedWidth = Math.min(
        Math.max(newChatWidth, PANEL_CONFIG.MIN_CHAT_WIDTH),
        PANEL_CONFIG.MAX_CHAT_WIDTH
      );

      setChatWidth(constrainedWidth);
      onResize?.(constrainedWidth);

      // Persist to localStorage
      try {
        localStorage.setItem(PANEL_CONFIG.STORAGE_KEY, constrainedWidth.toString());
      } catch (error) {
        console.warn('Failed to persist panel size:', error);
      }
    },
    [isResizing, onResize]
  );

  const stopResize = useCallback(() => {
    setIsResizing(false);
  }, []);

  // Mouse event listeners
  useEffect(() => {
    if (isResizing && typeof document !== 'undefined') {
      document.addEventListener('mousemove', handleResize);
      document.addEventListener('mouseup', stopResize);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleResize);
        document.removeEventListener('mouseup', stopResize);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isResizing, handleResize, stopResize]);

  // Load persisted size on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(PANEL_CONFIG.STORAGE_KEY);
      if (saved) {
        const savedWidth = parseFloat(saved);
        if (savedWidth >= PANEL_CONFIG.MIN_CHAT_WIDTH && savedWidth <= PANEL_CONFIG.MAX_CHAT_WIDTH) {
          setChatWidth(savedWidth);
        }
      }
    } catch (error) {
      console.warn('Failed to load persisted panel size:', error);
    }
  }, []);

  /**
   * Generate CSS Grid template columns for dynamic resizing
   * Uses fr units for natural grid behavior
   */
  const getGridTemplate = useCallback(() => {
    const chatFr = chatWidth;
    const blogFr = 100 - chatWidth;
    return `${chatFr}fr 4px ${blogFr}fr`;
  }, [chatWidth]);

  return {
    chatWidth,
    isResizing,
    containerRef,
    startResize,
    handleKeyDown,
    getGridTemplate,
  };
};

export const ResizablePanels: React.FC<ResizablePanelsProps> = ({
  children,
  showBlogPanel,
  onCloseBlogPanel,
  onPanelResize,
}) => {
  // Always call hooks at the top level
  const { chatWidth, isResizing, containerRef, startResize, handleKeyDown, getGridTemplate } = useGridPanelResize(
    PANEL_CONFIG.DEFAULT_CHAT_WIDTH,
    onPanelResize
  );
  
  // Validate children array structure after hooks
  if (!Array.isArray(children) || children.length !== 2) {
    console.error('ResizablePanels: Expected exactly 2 children [ChatPanel, BlogPanel]');
    return null;
  }

  const [chatPanel, originalBlogPanel] = children;

  // Production-safe clone with onClose handler injection
  const blogPanel = React.isValidElement(originalBlogPanel) 
    ? React.cloneElement(
        originalBlogPanel as React.ReactElement<{onClose?: () => void}>, 
        { 
          onClose: onCloseBlogPanel
        }
      )
    : originalBlogPanel;

  // Single panel mode - clean and simple
  if (!showBlogPanel) {
    return (
      <div className="h-full">
        <div className={PANEL_STYLES.SINGLE_PANEL}>
          {chatPanel}
        </div>
      </div>
    );
  }

  // CSS Grid template for perfect height inheritance
  const gridStyle = {
    gridTemplateColumns: getGridTemplate()
  };

  return (
    <div 
      ref={containerRef}
      className={PANEL_STYLES.CONTAINER}
      style={gridStyle}
    >
      {/* Chat Panel - Automatic height from CSS Grid */}
      <div className={PANEL_STYLES.CHAT_PANEL}>
        {chatPanel}
      </div>

      {/* Resize Handle - Grid column with perfect height */}
      <div
        className={PANEL_STYLES.RESIZE_HANDLE}
        onMouseDown={startResize}
        onKeyDown={handleKeyDown}
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize panels - use arrow keys to adjust"
        tabIndex={0}
      >
        <div className={PANEL_STYLES.RESIZE_INDICATOR}>
          <div className="w-0.5 h-8 bg-blue-500/60 rounded-full" />
        </div>
      </div>

      {/* Blog Panel - Automatic height from CSS Grid */}
      <div className={PANEL_STYLES.BLOG_PANEL}>
        {blogPanel}
      </div>

      {/* Resize overlay for better UX during drag */}
      {isResizing && (
        <div 
          className="fixed inset-0 bg-transparent cursor-col-resize z-50" 
          style={{ pointerEvents: 'auto' }}
        />
      )}
    </div>
  );
};
