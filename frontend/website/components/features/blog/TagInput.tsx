/**
 * Smart Tag Input Component
 * 
 * Advanced tag input with autocomplete, normalization, and tag creation.
 * Reuses existing design system components for consistency.
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Badge } from '@/components/design-system/Badge';
import { Button } from '@/components/design-system/Button';
import { usePortalDropdown } from '@/components/design-system/hooks/usePortalDropdown';
import { tagService, type Tag } from '@/lib/services/tagService';
import clsx from 'clsx';

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
  className?: string;
  disabled?: boolean;
}

interface TagSuggestion {
  tag?: Tag;
  displayText: string;
  normalizedName: string;
  exists: boolean;
  isCreateOption: boolean;
}

export function TagInput({ 
  value, 
  onChange, 
  placeholder = 'Add tags...', 
  maxTags = 5,
  className = '',
  disabled = false
}: TagInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState<TagSuggestion[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionRefs = useRef<(HTMLButtonElement | null)[]>([]);
  
  const {
    isOpen,
    toggle,
    open,
    close,
    triggerRef,
    dropdownRef,
    position
  } = usePortalDropdown({
    closeOnClickOutside: true,
    closeOnEscape: true,
    onOpenChange: (isOpen) => {
      if (!isOpen) {
        setSelectedIndex(-1);
      }
    }
  });

  // Debounced search
  const searchTags = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSuggestions([]);
      close();
      return;
    }

    setIsLoading(true);
    
    try {
      const normalizedQuery = tagService.normalizeTagName(query);
      const existingTags = await tagService.searchTags(query, 4); // Leave room for create option
      
      const suggestions: TagSuggestion[] = existingTags
        .filter(tag => !value.includes(tag.name)) // Exclude already selected tags
        .map(tag => ({
          tag,
          displayText: tagService.getDisplayName(tag.name),
          normalizedName: tag.name,
          exists: true,
          isCreateOption: false
        }));

      // Add create option if normalized query doesn't exist and isn't already selected
      const exactMatch = existingTags.find(tag => tag.name === normalizedQuery);
      if (!exactMatch && normalizedQuery && !value.includes(normalizedQuery)) {
        suggestions.push({
          displayText: tagService.getDisplayName(normalizedQuery),
          normalizedName: normalizedQuery,
          exists: false,
          isCreateOption: true
        });
      }

      setSuggestions(suggestions);
      setSelectedIndex(-1);
      
      if (suggestions.length > 0) {
        open();
      } else {
        close();
      }
    } catch (error) {
      console.error('Tag search failed:', error);
      setSuggestions([]);
      close();
    } finally {
      setIsLoading(false);
    }
  }, [value, close, open]);

  // Debounce search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchTags(inputValue);
    }, 200);

    return () => clearTimeout(timeoutId);
  }, [inputValue, searchTags]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (isOpen && suggestions.length > 0) {
          setSelectedIndex(prev => (prev + 1) % suggestions.length);
        }
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        if (isOpen && suggestions.length > 0) {
          setSelectedIndex(prev => prev <= 0 ? suggestions.length - 1 : prev - 1);
        }
        break;
        
      case 'Enter':
        e.preventDefault();
        if (isOpen && selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSuggestionSelect(suggestions[selectedIndex]);
        } else if (inputValue.trim()) {
          handleCreateTag(inputValue);
        }
        break;
        
        case 'Escape':
        close();
        break;      case 'Backspace':
        if (!inputValue && value.length > 0) {
          handleRemoveTag(value[value.length - 1]);
        }
        break;
        
      case ',':
      case 'Tab':
        if (inputValue.trim()) {
          e.preventDefault();
          handleCreateTag(inputValue);
        }
        break;
    }
  };

  const handleSuggestionSelect = (suggestion: TagSuggestion) => {
    if (value.length >= maxTags) return;
    
    const newTags = [...value, suggestion.normalizedName];
    onChange(newTags);
    setInputValue('');
    close();
    inputRef.current?.focus();
  };

  const handleCreateTag = (tagName: string) => {
    if (value.length >= maxTags) return;
    
    const normalizedName = tagService.normalizeTagName(tagName);
    if (normalizedName && !value.includes(normalizedName)) {
      const newTags = [...value, normalizedName];
      onChange(newTags);
    }
    setInputValue('');
    close();
    inputRef.current?.focus();
  };

  const handleRemoveTag = (tagToRemove: string) => {
    if (disabled) return;
    onChange(value.filter(tag => tag !== tagToRemove));
  };

  // Scroll to selected suggestion
  useEffect(() => {
    if (selectedIndex >= 0 && suggestionRefs.current[selectedIndex]) {
      suggestionRefs.current[selectedIndex]?.scrollIntoView({
        block: 'nearest'
      });
    }
  }, [selectedIndex]);

  const canAddMore = value.length < maxTags;

  return (
    <div className={clsx('relative', className)}>
      {/* Tag Input Container */}
      <div
        ref={triggerRef}
        className={clsx(
          'min-h-[2.5rem] p-2 rounded-lg border bg-black/20 backdrop-blur-sm',
          'border-white/10 focus-within:border-white/20 transition-colors',
          'flex flex-wrap items-center gap-1.5',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onClick={() => {
          if (!disabled) {
            inputRef.current?.focus();
          }
        }}
      >
        {/* Selected Tags */}
        {value.map((tag) => (
          <Badge 
            key={tag} 
            variant="blue" 
            className="flex items-center gap-1 text-xs"
          >
            <span>{tagService.getDisplayName(tag)}</span>
            {!disabled && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveTag(tag);
                }}
                className="ml-1 hover:text-red-300 transition-colors"
                aria-label={`Remove ${tag} tag`}
              >
                ×
              </button>
            )}
          </Badge>
        ))}
        
        {/* Input Field */}
        {canAddMore && !disabled && (
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleInputKeyDown}
            placeholder={value.length === 0 ? placeholder : ''}
            className={clsx(
              'flex-1 min-w-[120px] bg-transparent border-none outline-none',
              'text-sm text-white placeholder-gray-400',
              'disabled:cursor-not-allowed'
            )}
            disabled={disabled}
          />
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white/40" />
        )}
      </div>

      {/* Tag count indicator */}
      <div className="flex justify-between items-center mt-1 text-xs text-gray-400">
        <span>{value.length} / {maxTags} tags</span>
        {!canAddMore && (
          <span className="text-amber-400">Maximum tags reached</span>
        )}
      </div>

      {/* Dropdown Suggestions */}
      {isOpen && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="glass-dropdown w-full mt-1"
          style={position}
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={`${suggestion.normalizedName}-${suggestion.isCreateOption}`}
              ref={el => {
                suggestionRefs.current[index] = el;
              }}
              type="button"
              onClick={() => handleSuggestionSelect(suggestion)}
              className={clsx(
                'glass-dropdown-item w-full text-left flex items-center justify-between',
                'px-3 py-2 text-sm',
                selectedIndex === index && 'bg-white/10'
              )}
            >
              <div className="flex items-center gap-2">
                <span className="text-white">
                  {suggestion.displayText}
                </span>
                {suggestion.isCreateOption && (
                  <Badge variant="muted" className="text-2xs">
                    Create
                  </Badge>
                )}
              </div>
              
              {suggestion.tag && (
                <span className="text-gray-400 text-xs">
                  {suggestion.tag.postCount} posts
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}