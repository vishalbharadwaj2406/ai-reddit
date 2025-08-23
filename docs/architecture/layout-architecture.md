# Layout Architecture Documentation

## Overview

This document outlines the production-grade layout architecture implemented to resolve the global scrolling and height calculation issues across the AI Reddit application.

## Root Problem

The original implementation had multiple height calculation conflicts:

1. **Fixed Header**: 64px height, positioned `fixed` at top
2. **AppLayout**: Added `padding-top: 64px` to push content below header
3. **Page Components**: Used `h-screen` (100vh) without accounting for header
4. **Result**: Total height = 64px + 64px + 100vh = 128px + 100vh (exceeding viewport)

## Architecture Solution

### 1. Global Layout Structure

```
<html>
  <body>                           <!-- min-height: 100vh -->
    <Header />                     <!-- Fixed position, height: 64px -->
    <AppLayout>                    <!-- height: calc(100vh - 64px) -->
      <main className="mainContent"> <!-- padding-top: 64px, overflow: hidden -->
        <PageComponent>              <!-- height: 100% (of available space) -->
          <!-- Page content -->
        </PageComponent>
      </main>
    </AppLayout>
  </body>
</html>
```

### 2. Key Components

#### AppLayout (`components/layout/AppLayout.tsx`)
- **Main Container**: Fixed height calculation accounting for header
- **Overflow Management**: `overflow: hidden` to prevent double scrollbars
- **Responsive Margins**: Sidebar-aware spacing

#### Layout Hook (`hooks/useViewportLayout.ts`)
- **Consistent Heights**: Centralized height calculations
- **Responsive Updates**: Handles window resize and orientation changes
- **Reusable Patterns**: Common layout patterns for all pages

#### Global CSS Constants (`app/globals.css`)
- **CSS Custom Properties**: `--header-height`, `--available-height`
- **Utility Classes**: `.h-available`, `.page-container`, `.scrollable-content`
- **Tailwind Extensions**: Custom height utilities in config

### 3. Implementation Patterns

#### For Full-Height Pages
```tsx
import { usePageLayout } from '@/hooks/useViewportLayout';

export default function MyPage() {
  const layout = usePageLayout();
  
  return (
    <div {...layout.containerProps}>
      {/* Fixed header content */}
      <div {...layout.fixedProps}>
        <PageHeader />
      </div>
      
      {/* Scrollable content */}
      <div {...layout.scrollableProps}>
        <PageContent />
      </div>
      
      {/* Fixed footer content */}
      <div {...layout.fixedProps}>
        <PageFooter />
      </div>
    </div>
  );
}
```

#### For CSS-Only Solutions
```css
.my-page {
  height: var(--available-height);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.my-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}
```

## Benefits

### 1. **No Double Scrollbars**
- Each page manages its own scrolling within allocated space
- Global layout prevents content overflow

### 2. **Consistent Height Calculations**
- Centralized height management via hook and CSS constants
- Automatic responsive updates

### 3. **Production-Grade Architecture**
- Type-safe layout calculations
- Reusable patterns across components
- Performance optimized with proper overflow management

### 4. **Developer Experience**
- Simple API via layout hook
- Clear documentation and examples
- CSS utilities for common patterns

## Usage Guidelines

### Do's ✅
- Use `usePageLayout()` hook for full-height pages
- Apply `{...layout.containerProps}` to page container
- Use `{...layout.scrollableProps}` for content areas
- Use CSS custom properties for static calculations

### Don'ts ❌
- Don't use `h-screen` or `min-h-screen` on page components
- Don't add manual `padding-top` for header offset
- Don't create nested scroll containers without proper height constraints
- Don't override layout heights without understanding the architecture

## Migration Guide

### Existing Pages
1. Replace `h-screen` with `h-full` or layout hook
2. Remove manual header offset calculations
3. Use layout hook for consistent height management
4. Test scrolling behavior across different screen sizes

### New Pages
1. Import and use `usePageLayout()` hook
2. Apply layout props to container and content areas
3. Follow established patterns for fixed vs scrollable content

## Performance Considerations

- Layout calculations are cached and only update on resize
- CSS custom properties enable efficient static calculations
- Overflow management prevents unnecessary reflows
- Mobile-optimized with safe area considerations

## Browser Support

- Modern browsers with CSS custom properties support
- Responsive design with mobile-first approach
- Safe area support for iOS devices
- Graceful degradation for older browsers
