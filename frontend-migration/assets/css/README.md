# CSS Architecture Documentation

## Overview

This project follows **Atomic Design Principles** combined with **Tailwind CSS** utility-first approach and **CSS Layers** for optimal organization and maintainability.

## File Structure

```
assets/css/
├── colors.css    # Design tokens (CSS variables)
├── main.css      # Main stylesheet with layers
└── README.md     # This file
```

## Architecture Layers

### 1. **Base Layer** (`@layer base`)
- **Purpose**: Global resets, base element styles
- **Atomic Level**: Foundation/Atoms
- **Contains**:
  - HTML/Body styles
  - Typography defaults
  - Focus styles for accessibility

### 2. **Components Layer** (`@layer components`)
- **Purpose**: Reusable component classes
- **Atomic Level**: Atoms → Molecules → Organisms
- **Contains**:
  - **Atoms**: `.btn`, `.input-field`, `.label`
  - **Molecules**: `.card`
  - **Organisms**: `.container-custom`

### 3. **Utilities Layer** (`@layer utilities`)
- **Purpose**: Single-purpose utility classes
- **Atomic Level**: Utilities
- **Contains**:
  - `.scrollbar-hide` - Hide scrollbars
  - `.touch-manipulation` - Touch optimization
  - `.animate-blob` - Animation utilities

## Design Tokens (`colors.css`)

All colors are defined as CSS custom properties following the CoMET-RS logo palette:

- **Primary Colors**: Purple shades
- **Secondary Colors**: Indigo/Dark Blue
- **Accent Colors**: Orange/Gold
- **Extended Palette**: Pink, Cyan, Gold
- **Semantic Colors**: Success, Warning, Error, Info
- **Neutral Colors**: Gray scale

## Best Practices

### ✅ DO:
1. **Use Tailwind utilities** for component-specific styles
2. **Use component classes** (`.btn-primary`, `.card`) for reusable patterns
3. **Use CSS variables** for colors and design tokens
4. **Keep scoped styles minimal** - prefer utilities or component classes
5. **Follow atomic design hierarchy**: Atoms → Molecules → Organisms

### ❌ DON'T:
1. **Don't use inline styles** - use Tailwind or component classes
2. **Don't duplicate styles** - extract to utilities or components
3. **Don't use `!important`** - use proper specificity
4. **Don't mix approaches** - be consistent within components

## Component Style Guidelines

### Atoms (Basic building blocks)
- Use Tailwind utilities directly
- Minimal custom CSS
- Examples: `Button.vue`, `Input.vue`, `Logo.vue`

### Molecules (Simple component groups)
- Combine atoms with Tailwind utilities
- May use component classes (`.card`, `.btn`)
- Examples: `Card.vue`, `PlatformButton.vue`

### Organisms (Complex components)
- Compose molecules and atoms
- May have minimal scoped styles for complex interactions
- Prefer utilities over custom CSS
- Examples: `Navigation.vue`, `Footer.vue`, `PlatformCarousel.vue`

## Responsive Design

All components use Tailwind's responsive prefixes:
- `sm:` - Small screens (640px+)
- `md:` - Medium screens (768px+)
- `lg:` - Large screens (1024px+)
- `xl:` - Extra large screens (1280px+)

## Accessibility

- Focus styles defined in base layer
- Touch targets minimum 44x44px
- Semantic HTML with proper ARIA labels
- Color contrast ratios meet WCAG AA standards

## Performance

- CSS variables for runtime theming
- Tailwind purges unused styles
- Minimal custom CSS
- Scoped styles only when necessary
