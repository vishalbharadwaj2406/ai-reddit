import { create } from 'zustand'

interface HeaderState {
  conversationTitle: string | null
  setConversationTitle: (title: string | null) => void
}

export const useHeaderStore = create<HeaderState>((set) => ({
  conversationTitle: null,
  setConversationTitle: (title) => set({ conversationTitle: title }),
}))
