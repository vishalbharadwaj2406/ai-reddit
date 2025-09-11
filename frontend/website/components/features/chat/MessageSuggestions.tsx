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
    <div className="mb-4 space-y-3">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-400">Quick start</p>
        <Button 
          variant="secondary"
          size="sm"
          onClick={onWriteBlog}
          disabled={isGeneratingBlog}
          loading={isGeneratingBlog}
        >
          {isGeneratingBlog ? 'Generating...' : 'Write Blog'}
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {suggestions.map((suggestion, index) => (
          <Button 
            key={index}
            variant="ghost"
            size="md"
            onClick={() => onSuggestionClick(suggestion.text)}
            className="text-left justify-start"
          >
            {suggestion.category}
          </Button>
        ))}
      </div>
    </div>
  );
};
