/**
 * MessageSuggestions Component
 * Production-grade suggestion system for quick start and empty states
 */

'use client';

import { Button } from '@/components/design-system/Button';

interface MessageSuggestionsProps {
  onSuggestionClick: (suggestion: string) => void;
  onWriteBlog: () => void; // For opening empty blog editor
  isGeneratingBlog: boolean;
}

export const MessageSuggestions: React.FC<MessageSuggestionsProps> = ({
  onSuggestionClick,
  onWriteBlog,
  isGeneratingBlog,
}) => {
  const suggestions = [
    {
      text: "Help me brainstorm ideas about the future of technology and its impact on society",
      category: "Technology and society impact"
    },
    {
      text: "I want to explore the key principles of sustainable innovation in modern business",
      category: "Sustainable business innovation"
    },
    {
      text: "What are the most important skills needed for creative problem-solving in the digital age?",
      category: "Creative problem-solving skills"
    },
    {
      text: "How can I improve my understanding of emerging trends in artificial intelligence and machine learning?",
      category: "AI and machine learning trends"
    }
  ];

  return (
    <div className="mb-6 space-y-6">
      {/* Header with proper visual hierarchy */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-medium text-white/90">Quick start</h3>
        <Button 
          variant="secondary"
          size="sm"
          onClick={onWriteBlog}
          disabled={isGeneratingBlog}
          loading={isGeneratingBlog}
          className="font-medium"
        >
          {isGeneratingBlog ? 'Generating...' : 'Write Blog'}
        </Button>
      </div>
      
      {/* Suggestions Grid - Proper spacing and professional layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {suggestions.map((suggestion, index) => (
          <Button 
            key={index}
            variant="ghost"
            size="lg"
            onClick={() => onSuggestionClick(suggestion.text)}
            className="text-left justify-start h-auto p-4 whitespace-normal leading-relaxed
                     bg-white/3 hover:bg-white/8 border border-white/10 hover:border-white/20
                     transition-all duration-200"
          >
            <div className="space-y-1">
              <div className="font-medium text-white/95 text-sm leading-tight">
                {suggestion.category}
              </div>
              <div className="text-xs text-white/70 line-clamp-2">
                {suggestion.text}
              </div>
            </div>
          </Button>
        ))}
      </div>
    </div>
  );
};
