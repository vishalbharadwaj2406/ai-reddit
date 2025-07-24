'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function NewConversationPage() {
  const router = useRouter();
  const [conversationTitle, setConversationTitle] = useState('');
  const [messageText, setMessageText] = useState('');
  const [characterCount, setCharacterCount] = useState(0);

  const handleStartConversation = () => {
    // TODO: Create conversation and redirect
    // For now, just redirect to a mock conversation
    router.push('/conversations/1');
  };

  const handleCustomBlog = () => {
    // TODO: Navigate to custom blog editor
    console.log('Custom blog editor coming soon!');
  };

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
      <div className="px-12 py-12">
        <div className="max-w-4xl mx-auto">
          
          {/* Header */}
          <div className="flex items-center gap-4 mb-12">
            <Link href="/conversations">
              <button className="glass-button-secondary px-4 py-2 text-sm">
                ← Back to Conversations
              </button>
            </Link>
          </div>

          {/* Welcome Section */}
          <div className="text-center mb-16">
            <h1 className="text-display text-gradient-primary mb-6">
              ✨ Start Creating
            </h1>
            <p className="text-body text-caption max-w-2xl mx-auto leading-relaxed">
              Choose how you'd like to create your next piece of content. Start with AI conversation 
              for guided exploration, or jump straight into writing your own blog post.
            </p>
          </div>

          {/* Main Creation Options */}
          <div className="grid lg:grid-cols-2 gap-12 mb-16">
            
            {/* Custom Blog Option */}
            <div className="glass-elevated p-8 text-center">
              <div className="text-6xl mb-6">📝</div>
              <h2 className="text-heading text-gradient-primary mb-4">
                Write Custom Blog
              </h2>
              <p className="text-body text-caption mb-8 leading-relaxed">
                Start with a blank canvas. Perfect for when you already know what you want to write about 
                and prefer a direct approach to content creation.
              </p>
              <button 
                className="glass-button-generate px-12 py-4 text-lg font-bold"
                onClick={handleCustomBlog}
              >
                📝 Start Writing
              </button>
            </div>

            {/* AI Conversation Option */}
            <div className="glass-panel p-8 text-center">
              <div className="text-6xl mb-6">💬</div>
              <h2 className="text-heading text-white mb-4">
                AI Conversation
              </h2>
              <p className="text-body text-caption mb-8 leading-relaxed">
                Explore ideas through natural dialogue with AI. Perfect for developing thoughts, 
                discovering new perspectives, and generating content organically.
              </p>
              <button 
                className="glass-button-primary px-12 py-4 text-lg font-bold"
                onClick={() => document.getElementById('conversation-section')?.scrollIntoView({ behavior: 'smooth' })}
              >
                💬 Start Conversation
              </button>
            </div>
          </div>

          {/* Conversation Starter Section */}
          <div id="conversation-section" className="glass-card">
            <div className="text-center mb-8">
              <h3 className="text-subheading text-gradient-primary mb-4">
                Begin Your AI Conversation
              </h3>
              <p className="text-body text-caption">
                Share what's on your mind. The AI will help you explore, develop, and refine your thoughts 
                into meaningful content.
              </p>
            </div>

            {/* Conversation Title */}
            <div className="mb-6">
              <label className="block text-caption mb-3">Conversation Title (Optional)</label>
              <input
                type="text"
                placeholder="e.g., Exploring sustainable technology trends..."
                value={conversationTitle}
                onChange={(e) => setConversationTitle(e.target.value)}
                className="glass-input w-full px-6 py-4 text-body"
              />
            </div>

            {/* Message Input */}
            <div className="space-y-4">
              <div className="flex items-end justify-between">
                <label className="text-caption">Your Opening Message</label>
                <div className={getCounterClass()}>
                  {characterCount} / 5000
                </div>
              </div>
              
              <textarea
                className="glass-input w-full p-6 min-h-[200px] resize-none text-body"
                placeholder="What would you like to explore today? Share your thoughts, questions, or ideas..."
                value={messageText}
                onChange={handleTextChange}
                maxLength={5000}
              />

              {/* Conversation Starters */}
              <div className="space-y-3">
                <p className="text-caption text-gray-400">Need inspiration? Try one of these:</p>
                <div className="grid md:grid-cols-2 gap-3">
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm"
                    onClick={() => setMessageText("I've been thinking about how AI might change the way we work in the next decade. What are the most significant changes we should prepare for?")}
                  >
                    💼 Future of work and AI
                  </button>
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm"
                    onClick={() => setMessageText("What are the key principles for building sustainable technology that doesn't harm the environment?")}
                  >
                    🌱 Sustainable technology
                  </button>
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm"
                    onClick={() => setMessageText("How can we design digital products that prioritize user wellbeing over engagement metrics?")}
                  >
                    🧠 Digital wellbeing design
                  </button>
                  <button 
                    className="glass-button-toggle px-4 py-3 text-left text-sm"
                    onClick={() => setMessageText("What does it mean to be creative in an age where AI can generate art, music, and writing?")}
                  >
                    🎨 Creativity and AI
                  </button>
                </div>
              </div>
              
              <div className="flex gap-4 pt-4">
                <button 
                  className="glass-button-primary px-12 py-4 flex-1 text-lg"
                  onClick={handleStartConversation}
                  disabled={!messageText.trim()}
                >
                  🚀 Start Conversation
                </button>
              </div>
            </div>
          </div>

          {/* Tips Section */}
          <div className="mt-16 grid md:grid-cols-3 gap-8">
            <div className="glass-card text-center p-6">
              <div className="text-3xl mb-4">💡</div>
              <h4 className="text-subheading mb-3">Explore Freely</h4>
              <p className="text-caption">
                Don't worry about having perfect ideas. The best conversations start with curiosity.
              </p>
            </div>
            <div className="glass-card text-center p-6">
              <div className="text-3xl mb-4">🔄</div>
              <h4 className="text-subheading mb-3">Iterate & Refine</h4>
              <p className="text-caption">
                Use AI feedback to develop and improve your thoughts through natural dialogue.
              </p>
            </div>
            <div className="glass-card text-center p-6">
              <div className="text-3xl mb-4">📖</div>
              <h4 className="text-subheading mb-3">Generate Content</h4>
              <p className="text-caption">
                Transform your conversation into polished blog posts with one click.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
} 