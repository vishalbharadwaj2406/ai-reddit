"use client";

import { create } from 'zustand';
import type { Conversation } from '@/lib/services/conversationService';

interface ConversationsStoreState {
  conversations: Conversation[];
  lastFetched: number; // epoch ms
  setFromServer: (list: Conversation[]) => void;
  setStatus: (id: string, status: Conversation['status']) => void;
  clear: () => void;
}

export const useConversationsStore = create<ConversationsStoreState>((set) => ({
  conversations: [],
  lastFetched: 0,
  setFromServer: (list) => set({ conversations: list, lastFetched: Date.now() }),
  setStatus: (id, status) => set((state) => ({
    conversations: state.conversations.map(c => c.conversation_id === id ? { ...c, status } : c)
  })),
  clear: () => set({ conversations: [], lastFetched: 0 }),
}));
