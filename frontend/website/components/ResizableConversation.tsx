/**
 * Resizable Conversation Component
 * 
 * Production-grade resizable panel system using react-resizable-panels:
 * - Clean 50/50 default split
 * - Professional resize handles
 * - Complete blog panel collapse
 * - No state persistence (resets on reload)
 * - Responsive design
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

interface ResizableConversationProps {
  children: [React.ReactNode, React.ReactNode]; // [ChatPanel, BlogPanel]
  showBlogPanel?: boolean;
}

export const ResizableConversation: React.FC<ResizableConversationProps> = ({
  children,
  showBlogPanel = false,
}) => {
  const [chatPanel, blogPanel] = children;
  const [isMounted, setIsMounted] = useState(false);

  // Prevent hydration issues with resizable panels
  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    // Fallback during SSR/hydration
    return (
      <div className="h-full flex">
        <div className={showBlogPanel ? "flex-1" : "w-full"}>
          {chatPanel}
        </div>
        {showBlogPanel && (
          <div className="flex-1 border-l border-gray-700/30">
            {blogPanel}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="h-full relative">
      <PanelGroup direction="horizontal" className="h-full">
        {/* Chat Panel - Always visible */}
        <Panel 
          defaultSize={showBlogPanel ? 50 : 100}
          minSize={showBlogPanel ? 30 : 100}
          className="relative"
        >
          {chatPanel}
        </Panel>

        {/* Blog Panel - Conditionally rendered */}
        {showBlogPanel && (
          <>
            {/* Resize Handle - Professional styling */}
            <PanelResizeHandle className="w-1 bg-gray-700/30 hover:bg-blue-500/50 
                                         transition-colors duration-200 cursor-col-resize
                                         relative group">
              {/* Visual indicator */}
              <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-px 
                              bg-gray-600 group-hover:bg-blue-400 transition-colors" />
            </PanelResizeHandle>

            {/* Blog Panel */}
            <Panel 
              defaultSize={50}
              minSize={25}
              maxSize={70}
              className="relative"
            >
              <div className="border-l border-gray-700/30 h-full">
                {blogPanel}
              </div>
            </Panel>
          </>
        )}
      </PanelGroup>
    </div>
  );
};

export default ResizableConversation;