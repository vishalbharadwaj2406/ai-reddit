# AI Reddit Design System

**Theme**: Royal Ink Glass  
**Status**: Production Ready  
**Platforms**: Web, Mobile, Desktop  

---

## 🌈 **Colors**

### **Primary Palette**
```
Pure Black: #000000 (background)
Royal Ink Blue: #1E3A8A (primary brand)
Brilliant Blue: #3B82F6 (interactive)
Light Blue: #60A5FA (accents)
Ice White: #E6F3FF (text/gradients)
```

### **Functional Colors**
```
Success: #10B981  Warning: #F59E0B  Error: #EF4444  Info: #3B82F6
```

### **Surfaces**
```
Background: #000000
Glass Level 1: rgba(255, 255, 255, 0.03)
Glass Level 2: rgba(255, 255, 255, 0.05)
Glass Elevated: rgba(30, 58, 138, 0.15)
Border: rgba(59, 130, 246, 0.2)
```

---

## ✨ **Glass Effects**

### **Standard Glass**
```css
background: rgba(255, 255, 255, 0.03)
backdrop-filter: blur(32px) saturate(180%)
border: 2px solid rgba(59, 130, 246, 0.2)
border-radius: 24px
```

### **Elevated Glass**
```css
background: linear-gradient(135deg, rgba(30, 58, 138, 0.15), rgba(59, 130, 246, 0.08))
backdrop-filter: blur(40px) saturate(200%)
border: 2px solid rgba(59, 130, 246, 0.35)
border-radius: 24px
```

---

## 🎭 **Typography**

### **Font Stack**
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', Roboto, sans-serif
```

### **Scale**
```
Display: 48px/56px (3rem/3.5rem)
Heading Large: 28px/36px (1.75rem/2.25rem)
Heading Medium: 24px/32px (1.5rem/2rem)
Body Large: 17px/26px (1.0625rem/1.625rem)
Body: 16px/24px (1rem/1.5rem)
Caption: 14px/20px (0.875rem/1.25rem)
```

### **Weights**
```
Light: 300  Regular: 400  Medium: 500  Semibold: 600  Bold: 700  Heavy: 800
```

---

## 📐 **Spacing**

### **Scale (8px base)**
```
xs: 4px   sm: 8px   md: 16px   lg: 24px   xl: 32px   2xl: 48px   3xl: 64px
```

### **Components**
```
Button: 12px 20px
Card: 24px 32px
Section: 48px
Page: 48px
```

---

## 🌟 **Animation**

### **Timing**
```
Quick: 200ms   Standard: 300ms   Slow: 600ms   Ultra Slow: 25s (gradients)
```

### **Easing**
```
ease-out, ease-in-out, cubic-bezier(0.4, 0, 0.2, 1)
```

---

## 📱 **Responsive**

### **Breakpoints**
```
Mobile: 0-767px   Tablet: 768-1023px   Desktop: 1024px+
```

### **Adaptations**
- Mobile: Reduce spacing 25-50%, larger touch targets (44px min)
- Desktop: Full glass effects, hover states

---

## 🎯 **Implementation**

### **Performance**
- Use transform/opacity for animations
- Limit backdrop-filter on mobile
- GPU acceleration for smooth effects

### **Accessibility**
- 4.5:1 contrast ratio minimum
- Keyboard navigation support
- Reduced motion alternatives

---

**Resources**: [Website Sample](./website-sample.html)
