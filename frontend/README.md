# AI Social - Frontend

> **Status (July 20, 2025)**: Core UI complete with glass morphism design system. Authentication working. One known glass effect issue needs investigation.

## 🏗️ Architecture

Single Next.js 15 application with clean organization:

```
frontend/website/           # Next.js Web Application
├── app/                   # Next.js App Router
│   ├── globals.css       # Global styles & glass effects
│   ├── layout.tsx        # Root layout with background pattern
│   └── page.tsx          # Homepage
├── components/            # React Components
│   ├── Header.tsx        # Fixed header with glass morphism
│   ├── Providers.tsx     # Auth & context providers
│   ├── ui/               # Reusable UI Components
│   └── index.ts          # Component exports
├── lib/                  # Utilities & Configuration
│   ├── auth/             # NextAuth v5 configuration
│   ├── config/           # App configuration
│   ├── data/             # Types & mock data
│   ├── stores/           # State management
│   ├── types/            # TypeScript types
│   ├── utils/            # Utilities
│   └── design-system.ts  # Royal Ink Glass theme
├── public/               # Static assets
├── tests/                # Test suites
└── package.json          # Dependencies
```

## 🎨 Royal Ink Glass Design System

Professional glass morphism with royal blue accents:

- **Pure Black**: `#000000` - Main background
- **Royal Blue**: `#1E3A8A` - Primary brand color  
- **Brilliant Blue**: `#3B82F6` - Secondary brand color
- **Ice White**: `#E6F3FF` - Primary text color

## ✅ Current Status

### Implemented Features ✅ COMPLETE
- ✅ **Authentication**: Google OAuth with NextAuth v5 (full sign-in/out flow)
- ✅ **Header**: Fixed navigation with glass morphism backdrop blur
- ✅ **Glass Design System**: Royal Ink Glass theme with backdrop-filter effects
- ✅ **Background Animation**: Royal blue gradient patterns for glass content
- ✅ **Conversations**: Page with search and filter functionality
- ✅ **UI Components**: Button, Input, Card with consistent glass styling
- ✅ **Testing**: Vitest setup with unit tests
- ✅ **TypeScript**: Full type safety across application
- ✅ **Responsive Design**: Mobile-first approach with Tailwind CSS 4

### Known Issues 🔍 NEEDS INVESTIGATION

#### Glass Effect Inconsistency (Priority: Medium)
- **Problem**: Header backdrop-filter blur works perfectly, dropdown appears transparent
- **Details**: Both use identical `.header-glass` CSS class from globals.css
- **Investigation Attempted**:
  - ✅ Z-index stacking context adjusted (dropdown: 101, header: 100)
  - ✅ Transform animations removed to prevent backdrop-filter interference
  - ✅ Global CSS import verified and working
  - ✅ All conflicting styled-jsx CSS removed
  - ✅ Background pattern properly positioned (z-index: -1)
- **Current State**: Header glass effect beautiful, dropdown transparent
- **Impact**: Visual inconsistency in design system
- **Next Steps**: Deep browser debugging, alternative CSS approaches

### Authentication System ✅ COMPLETE
- Google OAuth sign-in/sign-out with NextAuth v5 beta
- Session persistence across page reloads
- Protected routes with automatic redirects
- Profile picture display in header dropdown
- Clean authentication state management

### Glass Morphism Design System ✅ MOSTLY COMPLETE
- **Working**: Header backdrop-filter blur (beautiful Windows-like effect)
- **Working**: Royal blue gradient background pattern animation
- **Working**: Global CSS architecture with `.header-glass` class
- **Issue**: Dropdown transparency despite identical CSS classes
- Smooth animations and transitions throughout
- Professional glass styling with rgba(0, 0, 0, 0.6) + blur(24px)
- Responsive design maintaining glass effects on all devices

## 🚀 Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

## 📱 Live Preview

Development server: **http://localhost:3001**

## 🔄 Next Steps

1. Individual conversation pages
2. Real-time AI chat interface
3. Enhanced social features
4. Advanced search and filtering

## 🛠️ Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS 4 with custom design system
- **Authentication**: NextAuth v5 (beta)
- **Testing**: Vitest with Testing Library
- **TypeScript**: Full type safety
- **State Management**: React hooks + context

## 🎯 Key Features

### Header Component
- Fixed positioning with backdrop blur
- Animated logo with gradient text
- Profile dropdown with authentication
- Responsive design for mobile
- Glass morphism styling with royal blue accents

### Conversations Page
- Glass morphism conversation cards
- Search and filter functionality
- Royal blue color scheme throughout
- Smooth hover animations
- Professional typography and spacing

### Authentication Flow
- Google OAuth integration
- Session management with NextAuth v5
- Protected route navigation
- Clean sign-in/sign-out experience
- Profile picture display in header
