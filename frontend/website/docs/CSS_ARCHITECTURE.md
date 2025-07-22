# CSS Modules + Design System Architecture

## Overview

This project uses a **CSS Modules + Design System** architecture for scalable, maintainable styling. This approach provides:

✅ **Component Encapsulation** - Styles are scoped to components  
✅ **Reusable Design System** - Consistent glass morphism effects  
✅ **Better Performance** - Only loads styles for used components  
✅ **Team Collaboration** - Clear separation of concerns  
✅ **Type Safety** - CSS Modules provide TypeScript integration  

## Architecture Structure

```
styles/
  design-system.css      # Global design tokens & reusable classes
  globals.css           # Global styles only (resets, body, etc.)

components/
  Header/
    Header.tsx          # Component logic
    Header.module.css   # Component-specific styles
    index.ts           # Clean exports
  Welcome/
    WelcomePage.tsx
    Welcome.module.css
    index.ts

lib/
  design-system.ts      # TypeScript utilities & tokens
```

## Design System Files

### `styles/design-system.css`
- **Design tokens** (colors, spacing, typography, shadows)
- **Reusable glass morphism classes** (`glass-base`, `glass-card`, etc.)
- **Button system** (`glass-button-primary`, `glass-button-secondary`)
- **Text utilities** (`text-gradient-primary`, `text-accent`)
- **Utility classes** (`glow-blue`, `focus-ring`)

### `styles/globals.css`
- **Global resets** (`*, body, html`)
- **Background patterns** (`.bg-pattern`)
- **Scrollbar styling**
- **Imports design system**

### `lib/design-system.ts`
- **TypeScript design tokens**
- **Class name constants**
- **Utility functions**
- **Component presets**

## Component Structure

### CSS Modules Pattern
```typescript
// Component.tsx
import styles from './Component.module.css'

export default function Component() {
  return (
    <div className={styles.container}>
      <button className={styles.primaryButton}>
        Click me
      </button>
    </div>
  )
}
```

```css
/* Component.module.css */
.container {
  composes: glass-card from '../../styles/design-system.css';
  padding: var(--space-lg);
}

.primaryButton {
  composes: glass-button-primary from '../../styles/design-system.css';
  font-size: var(--text-base);
}
```

## Using the Design System

### 1. CSS Variables (Design Tokens)
```css
.myComponent {
  padding: var(--space-lg);        /* 24px */
  border-radius: var(--radius-lg); /* 16px */
  color: var(--color-light-blue);  /* #60A5FA */
  font-size: var(--text-xl);       /* responsive clamp() */
}
```

### 2. Composing from Design System
```css
.myCard {
  composes: glass-card from '../../styles/design-system.css';
  /* Additional component-specific styles */
  max-width: 500px;
}

.myButton {
  composes: glass-button-primary from '../../styles/design-system.css';
  /* Override specific properties */
  min-width: 200px;
}
```

### 3. TypeScript Integration
```typescript
import { glassClasses, designTokens } from '@/lib/design-system'

// Use class constants
const buttonClass = glassClasses.buttonPrimary

// Access design tokens
const primaryColor = designTokens.colors.brilliantBlue
```

## Glass Morphism System

### Available Classes

#### Base Effects
- `glass-base` - Core glass morphism effect
- `glass-card` - Card container with glass effect
- `glass-elevated` - Enhanced glass for special elements
- `glass-header` - Fixed header with glass effect

#### Buttons
- `glass-button-primary` - Primary action button
- `glass-button-secondary` - Secondary action button

#### Text Effects
- `text-gradient-primary` - Primary gradient text
- `text-gradient-logo` - Logo gradient text
- `text-accent` - Accent color text

#### Utilities
- `glow-blue` - Blue glow effect
- `focus-ring` - Accessible focus ring

### Responsive Design

The design system includes responsive design tokens:

```css
.title {
  font-size: var(--text-4xl); /* clamp(32px, 6vw, 48px) */
}

.spacing {
  padding: var(--space-lg);    /* 24px base, scales with breakpoints */
}
```

## Best Practices

### Do ✅
- Use CSS Modules for component-specific styles
- Compose from design system classes when possible
- Use design tokens (CSS variables) for consistency
- Keep component styles focused and minimal
- Document any custom utilities

### Don't ❌
- Put component-specific styles in globals.css
- Create duplicate glass effects
- Use hardcoded values (use design tokens)
- Mix different styling approaches in same component
- Override design system classes excessively

## Migration Guide

### From Global CSS to CSS Modules

1. **Create component directory**:
   ```
   components/MyComponent/
     MyComponent.tsx
     MyComponent.module.css
     index.ts
   ```

2. **Move component styles** from globals.css to module
3. **Use `composes` to inherit** from design system
4. **Update imports** to use CSS Modules
5. **Test component** in isolation

### Example Migration

**Before (Global CSS):**
```css
/* globals.css */
.my-card {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(24px);
  /* ... glass effect styles */
}
```

**After (CSS Module):**
```css
/* MyCard.module.css */
.card {
  composes: glass-card from '../../styles/design-system.css';
  /* Only component-specific overrides */
  max-width: 400px;
}
```

## Development Workflow

1. **Check design system** first for existing patterns
2. **Create CSS Module** for component-specific styles
3. **Compose from design system** when possible
4. **Add new patterns** to design system if reusable
5. **Document any new utilities**
6. **Test responsive behavior**

This architecture scales well as the application grows and makes it easy for teams to collaborate on styling without conflicts.
