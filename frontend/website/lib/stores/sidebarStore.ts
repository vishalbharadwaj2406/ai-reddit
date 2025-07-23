import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SidebarState {
  isExpanded: boolean
  isMobileOpen: boolean
  toggleExpanded: () => void
  setExpanded: (expanded: boolean) => void
  toggleMobile: () => void
  setMobileOpen: (open: boolean) => void
}

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      isExpanded: true, // Default to expanded for better UX
      isMobileOpen: false,
      
      toggleExpanded: () => set((state) => ({ 
        isExpanded: !state.isExpanded 
      })),
      
      setExpanded: (expanded: boolean) => set({ 
        isExpanded: expanded 
      }),
      
      toggleMobile: () => set((state) => ({ 
        isMobileOpen: !state.isMobileOpen 
      })),
      
      setMobileOpen: (open: boolean) => set({ 
        isMobileOpen: open 
      }),
    }),
    {
      name: 'ai-social-sidebar', // Unique localStorage key
      partialize: (state) => ({ 
        isExpanded: state.isExpanded // Only persist expanded state, not mobile state
      }),
      // Persist across all authentication state changes
      version: 1,
    }
  )
) 