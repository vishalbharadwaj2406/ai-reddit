'use client';

import { useState } from 'react';

export default function DesignSystemDemo() {
  const [activePanel, setActivePanel] = useState('buttons');
  const [messageText, setMessageText] = useState('');
  const [characterCount, setCharacterCount] = useState(0);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setMessageText(text);
    setCharacterCount(text.length);
  };

  const getCounterClass = () => {
    if (characterCount > 4500) return 'glass-counter error';
    if (characterCount > 4000) return 'glass-counter warning';
    return 'glass-counter';
  };

  return (
    <div className="min-h-screen">
      {/* Content using AppLayout system - no extra padding needed */}
      <div className="px-12 py-12">
        <div className="max-w-7xl mx-auto">
          
          {/* Demo Navigation */}
          <div className="mb-16 text-center">
            <h1 className="text-display text-gradient-logo mb-8">
              ✨ Glass Design System
            </h1>
            <nav className="flex justify-center gap-4 flex-wrap">
              <button 
                className={`glass-button-toggle ${activePanel === 'buttons' ? 'active' : ''}`}
                onClick={() => setActivePanel('buttons')}
              >
                Buttons
              </button>
              <button 
                className={`glass-button-toggle ${activePanel === 'typography' ? 'active' : ''}`}
                onClick={() => setActivePanel('typography')}
              >
                Typography
              </button>
              <button 
                className={`glass-button-toggle ${activePanel === 'conversation' ? 'active' : ''}`}
                onClick={() => setActivePanel('conversation')}
              >
                Sample Chat
              </button>
              <button 
                className={`glass-button-toggle ${activePanel === 'panels' ? 'active' : ''}`}
                onClick={() => setActivePanel('panels')}
              >
                Layout System
              </button>
            </nav>
          </div>

          {/* Buttons Section */}
          {activePanel === 'buttons' && (
            <div className="space-y-16">
              <div className="text-center">
                <h2 className="text-heading text-gradient-primary mb-4">
                  Glass Button System
                </h2>
                <p className="text-body text-caption max-w-2xl mx-auto">
                  Dark theme with sophisticated glass morphism effects and premium interactions.
                </p>
              </div>

                              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-12">
                {/* Original Glass Buttons */}
                <div className="glass-card">
                  <h3 className="text-subheading mb-6">Original Glass System</h3>
                  <div className="space-y-4">
                    <button className="glass-button-primary px-8 py-4 w-full">
                      Primary Button
                    </button>
                    <button className="glass-button-secondary px-8 py-4 w-full">
                      Secondary Button
                    </button>
                  </div>
                </div>

                {/* Sample Website Buttons */}
                <div className="sample-post-card">
                  <h3 className="text-subheading mb-6">Sample Website Style</h3>
                  <div className="space-y-4">
                    <button className="sample-btn w-full">
                      Sample Button
                    </button>
                    <button className="glass-button-toggle px-8 py-4 w-full">
                      Toggle Button
                    </button>
                  </div>
                </div>

                {/* Enhanced Buttons */}
                <div className="glass-elevated">
                  <h3 className="text-subheading mb-6">Enhanced Effects</h3>
                  <div className="space-y-4">
                    <button className="glass-button-generate px-8 py-4 w-full">
                      ✨ Generate Blog
                    </button>
                    <button className="glass-button-toggle active px-6 py-3 w-full">
                      Active Toggle
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Typography Section */}
          {activePanel === 'typography' && (
            <div className="space-y-16">
              <div className="text-center">
                <h2 className="text-heading text-gradient-primary mb-4">
                  Typography System
                </h2>
                <p className="text-body text-caption max-w-2xl mx-auto">
                  Dark theme typography with proper hierarchy and subtle gradient effects.
                </p>
              </div>

                              <div className="grid lg:grid-cols-2 gap-12">
                  {/* Text Hierarchy */}
                  <div className="glass-card">
                  <h3 className="text-subheading mb-6">Text Hierarchy</h3>
                  <div className="space-y-6">
                    <h1 className="text-display">Display Heading</h1>
                    <h2 className="text-heading">Section Heading</h2>
                    <h3 className="text-subheading">Subsection Heading</h3>
                    <p className="text-body">
                      Body text that provides excellent readability with proper contrast on dark background.
                    </p>
                    <p className="text-caption">
                      Caption text for secondary information
                    </p>
                  </div>
                </div>

                {/* Gradient Effects */}
                <div className="glass-card">
                  <h3 className="text-subheading mb-6">Gradient Effects</h3>
                  <div className="space-y-6">
                    <h2 className="text-gradient-logo text-heading">
                      Animated Logo Text
                    </h2>
                    <h2 className="text-gradient-primary text-heading">
                      Primary Gradient
                    </h2>
                    <p className="text-accent text-body">
                      Accent colored text with subtle glow
                    </p>
                    <p className="text-message">
                      Message text optimized for conversations
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Sample Conversation Section */}
          {activePanel === 'conversation' && (
            <div className="space-y-12">
              <div className="text-center">
                <h2 className="text-heading text-gradient-primary mb-4">
                  Sample Website Chat Interface
                </h2>
                <p className="text-body text-caption max-w-2xl mx-auto">
                  Exact recreation of the website-sample.html chat interface with proper dark theme.
                </p>
              </div>

                              <div className="grid lg:grid-cols-2 gap-12">
                  {/* Sample Chat Panel */}
                <div className="sample-chat-panel">
                  <div className="text-center mb-8">
                    <h3 className="text-subheading text-gradient-primary mb-4">
                      Royal Intelligence
                    </h3>
                    <p className="text-caption">
                      Premium AI conversations in elegant style
                    </p>
                  </div>
                  
                  <div className="flex-1 space-y-6 mb-8">
                    {/* AI Message */}
                    <div className="flex justify-start">
                      <div className="sample-message ai">
                        Welcome to Royal Intelligence. I'm here to provide thoughtful, nuanced conversations with the sophistication you deserve. What would you like to explore today?
                      </div>
                    </div>

                    {/* User Message */}
                    <div className="flex justify-end">
                      <div className="sample-message user">
                        I'm interested in discussing the intersection of design psychology and user trust in digital interfaces.
                      </div>
                    </div>

                    {/* AI Message */}
                    <div className="flex justify-start">
                      <div className="sample-message ai">
                        Excellent topic. Design psychology plays a crucial role in establishing trust - from color choices that evoke reliability to micro-interactions that feel natural and predictable. The subtle details often matter most...
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-4 items-end">
                    <textarea 
                      className="sample-input-field" 
                      placeholder="Share your refined thoughts..."
                      rows={3}
                    />
                    <button className="sample-btn">Send</button>
                  </div>
                </div>

                {/* Sample Social Panel */}
                <div className="sample-social-panel">
                  <div>
                    <h3 className="text-subheading mb-6">Royal Insights</h3>
                    <div className="flex gap-4 mb-8">
                      <button className="glass-button-toggle active">Premium</button>
                      <button className="glass-button-toggle">Trending</button>
                      <button className="glass-button-toggle">Design</button>
                      <button className="glass-button-toggle">Tech</button>
                    </div>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="sample-post-card">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-11 h-11 rounded-full bg-gradient-to-br from-blue-800 to-blue-600 flex items-center justify-center font-bold text-sm">
                          EC
                        </div>
                        <div>
                          <div className="font-bold text-white">Elena Chen</div>
                          <div className="text-caption">2 hours ago</div>
                        </div>
                      </div>
                      <div className="text-body mb-6">
                        Had a sophisticated AI conversation about the principles of luxury interface design. We explored how restraint, attention to detail, and invisible complexity create experiences that feel effortless yet powerful.
                      </div>
                      <div className="flex gap-6 text-caption">
                        <span>👑 Royal 45</span>
                        <span>💬 Discuss 18</span>
                        <span>🔄 Share 9</span>
                      </div>
                    </div>

                    <div className="sample-post-card">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-11 h-11 rounded-full bg-gradient-to-br from-blue-800 to-blue-600 flex items-center justify-center font-bold text-sm">
                          MS
                        </div>
                        <div>
                          <div className="font-bold text-white">Marcus Stone</div>
                          <div className="text-caption">4 hours ago</div>
                        </div>
                      </div>
                      <div className="text-body mb-6">
                        Explored the psychology of premium user experiences with AI. Why do certain interfaces feel expensive while others feel cheap? The conversation revealed fascinating insights about perception and expectation.
                      </div>
                      <div className="flex gap-6 text-caption">
                        <span>👑 Royal 62</span>
                        <span>💬 Discuss 24</span>
                        <span>🔄 Share 12</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Layout System Section */}
          {activePanel === 'panels' && (
            <div className="space-y-16">
              <div className="text-center">
                <h2 className="text-heading text-gradient-primary mb-4">
                  Three-Panel Layout System
                </h2>
                <p className="text-body text-caption max-w-2xl mx-auto">
                  Our workspace layout system with proper glass effects and dark theme.
                </p>
              </div>

              <div className="grid lg:grid-cols-3 gap-12 min-h-96">
                {/* Left Panel - Original Blog (Subdued) */}
                <div className="glass-panel-subdued p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-subheading text-gray-300">Original Blog</h3>
                    <button className="glass-button-toggle">👁 Toggle</button>
                  </div>
                  <div className="text-body text-gray-400 space-y-3">
                    <p>This panel shows the original blog post when forking a conversation.</p>
                    <p>Content maintains perfect readability with subtle glass effects.</p>
                    <p>Users can toggle between the blog and its conversation.</p>
                  </div>
                </div>

                {/* Center Panel - Active Conversation (Keep Perfect) */}
                <div className="glass-elevated p-6">
                  <h3 className="text-subheading mb-4">Active Conversation</h3>
                  <div className="space-y-4">
                    <div className="glass-message-ai text-sm">
                      AI responses appear here with beautiful glass effects and proper dark theme styling...
                    </div>
                    <div className="glass-message-user text-sm">
                      User messages have distinct blue gradient styling with excellent contrast...
                    </div>
                    <div className="flex gap-2 mt-4">
                      <input 
                        className="glass-input flex-1 px-3 py-2 text-sm" 
                        placeholder="Type message..."
                      />
                      <button className="glass-button-primary px-4 py-2 text-sm">Send</button>
                    </div>
                  </div>
                </div>

                {/* Right Panel - Generated Blog (Active/Prominent) */}
                <div className="glass-panel-active p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-subheading text-blue-300">Generated Blog</h3>
                    <button className="glass-button-generate px-4 py-2 text-sm">Post</button>
                  </div>
                  <div className="text-body text-blue-100 space-y-3">
                    <p>Generated blog content appears here with inline editing capabilities.</p>
                    <p>Users can refine and perfect their content before publishing.</p>
                    <p>Character limits and formatting tools are available.</p>
                  </div>
                </div>
              </div>

              {/* Additional Layout Examples */}
                              <div className="grid md:grid-cols-2 gap-12">
                  <div className="glass-card">
                    <h3 className="text-subheading mb-4">Glass Card (Original)</h3>
                  <p className="text-body">
                    Standard glass card with subtle effects and dark theme. 
                    Perfect for content containers and information display.
                  </p>
                </div>

                <div className="sample-post-card">
                  <h3 className="text-subheading mb-4">Sample Style Card</h3>
                  <p className="text-body">
                    Enhanced glass card matching the website sample styling 
                    with stronger effects and interactive hover states.
                  </p>
                </div>
              </div>
            </div>
          )}

                 </div>
        </div>

      {/* Footer */}
      <footer className="mt-20 pb-16">
        <div className="max-w-7xl mx-auto px-12 text-center">
          <div className="glass-card">
            <h3 className="text-subheading text-gradient-primary mb-4">
              Dark Theme Glass Design System
            </h3>
            <p className="text-body text-caption">
              Sophisticated, dark-themed interface with subtle glass effects. 
              Perfect balance of elegance and functionality.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
} 