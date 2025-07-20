// Demo data for development and testing

import type { Conversation, Message, Post, User } from '../types';

export const DEMO_USERS: User[] = [
  {
    id: 'user-1',
    userName: 'Demo User',
    email: 'demo@aisocial.com',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-20T15:30:00Z',
  },
  {
    id: 'user-2',
    userName: 'AI Explorer',
    email: 'explorer@aisocial.com',
    createdAt: '2024-01-10T08:00:00Z',
    updatedAt: '2024-01-18T12:00:00Z',
  },
];

export const DEMO_CONVERSATIONS: Conversation[] = [
  {
    id: 'conv-1',
    title: 'Design Psychology Discussion',
    lastMessage: 'The subtle details often matter most in building user trust...',
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    messageCount: 12,
    isPosted: true,
    userId: 'user-1',
    createdAt: '2024-01-20T10:00:00Z',
  },
  {
    id: 'conv-2',
    title: 'AI Future Predictions',
    lastMessage: 'What are your thoughts on AI consciousness?',
    updatedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
    messageCount: 8,
    isPosted: false,
    userId: 'user-1',
    createdAt: '2024-01-19T14:30:00Z',
  },
  {
    id: 'conv-3',
    title: 'Premium UX Patterns',
    lastMessage: 'True elegance lies in what you don\'t see.',
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
    messageCount: 15,
    isPosted: true,
    userId: 'user-1',
    createdAt: '2024-01-17T09:15:00Z',
  },
  {
    id: 'conv-4',
    title: 'Ethical AI Development',
    lastMessage: 'How do we ensure AI systems remain beneficial for humanity?',
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
    messageCount: 22,
    isPosted: false,
    userId: 'user-1',
    createdAt: '2024-01-15T16:45:00Z',
  },
];

export const DEMO_MESSAGES: Message[] = [
  {
    id: 'msg-1',
    conversationId: 'conv-1',
    content: 'What makes a user interface feel trustworthy to users?',
    role: 'user',
    timestamp: '2024-01-20T10:00:00Z',
  },
  {
    id: 'msg-2',
    conversationId: 'conv-1',
    content: 'Trust in UI design comes from several key factors: consistency, clarity, and subtle attention to detail. When users can predict how interface elements will behave, they feel more confident interacting with them.',
    role: 'assistant',
    timestamp: '2024-01-20T10:01:00Z',
  },
  {
    id: 'msg-3',
    conversationId: 'conv-1',
    content: 'Can you elaborate on the "subtle attention to detail" part?',
    role: 'user',
    timestamp: '2024-01-20T10:02:00Z',
  },
  {
    id: 'msg-4',
    conversationId: 'conv-1',
    content: 'The subtle details often matter most in building user trust. Things like proper spacing, micro-animations that guide the eye, appropriate contrast ratios, and consistent typography all contribute to a sense of polish and reliability.',
    role: 'assistant',
    timestamp: '2024-01-20T10:03:00Z',
  },
];

export const DEMO_POSTS: Post[] = [
  {
    id: 'post-1',
    title: 'The Psychology of Trust in UI Design',
    content: 'A fascinating discussion about what makes users trust digital interfaces...',
    conversationId: 'conv-1',
    userId: 'user-1',
    createdAt: '2024-01-20T11:00:00Z',
    updatedAt: '2024-01-20T11:00:00Z',
    likes: 45,
    shares: 12,
    isPublished: true,
  },
  {
    id: 'post-2',
    title: 'Premium UX Patterns That Actually Work',
    content: 'Exploring the hidden elegance in minimalist design approaches...',
    conversationId: 'conv-3',
    userId: 'user-1',
    createdAt: '2024-01-18T14:30:00Z',
    updatedAt: '2024-01-18T14:30:00Z',
    likes: 78,
    shares: 23,
    isPublished: true,
  },
];

// Helper functions to get demo data
export const getDemoConversations = (userId?: string): Conversation[] => {
  if (userId) {
    return DEMO_CONVERSATIONS.filter(conv => conv.userId === userId);
  }
  return DEMO_CONVERSATIONS;
};

export const getDemoMessages = (conversationId: string): Message[] => {
  return DEMO_MESSAGES.filter(msg => msg.conversationId === conversationId);
};

export const getDemoPosts = (userId?: string): Post[] => {
  if (userId) {
    return DEMO_POSTS.filter(post => post.userId === userId);
  }
  return DEMO_POSTS;
};

export const createDemoConversation = (title: string, userId: string): Conversation => {
  return {
    id: `conv-${Date.now()}`,
    title,
    lastMessage: 'Start a new conversation with AI...',
    updatedAt: new Date().toISOString(),
    messageCount: 0,
    isPosted: false,
    userId,
    createdAt: new Date().toISOString(),
  };
};
