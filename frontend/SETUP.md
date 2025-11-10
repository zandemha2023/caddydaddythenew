# Theo Frontend - Setup Guide

Complete setup guide for the Theo CAD frontend application.

## Quick Start (5 Minutes)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create environment file
cp .env.example .env.local

# 4. Start development server
npm run dev
```

Visit http://localhost:3000 to see the application!

## Detailed Setup

### Step 1: Prerequisites

Ensure you have:
- **Node.js 18+** (check with `node --version`)
- **npm** or **pnpm** (check with `npm --version`)

If not installed:
```bash
# macOS (using Homebrew)
brew install node

# Windows (using Chocolatey)
choco install nodejs

# Linux (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 2: Install Dependencies

```bash
cd frontend
npm install
```

This installs:
- Next.js 14 with App Router
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Framer Motion for animations
- Radix UI primitives
- Lucide React icons
- And more...

### Step 3: Environment Configuration

Create `.env.local`:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
# For local development (backend running on localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production (replace with your Railway backend URL)
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Step 4: Verify Installation

Run the development server:

```bash
npm run dev
```

You should see:
```
▲ Next.js 14.2.15
- Local:        http://localhost:3000
- Environments: .env.local

✓ Ready in 2.5s
```

### Step 5: Test the Design System

Visit http://localhost:3000/test

You should see a comprehensive showcase of all components:
- ✅ Color palette displaying correctly
- ✅ All button variants working
- ✅ Status badges animating
- ✅ Agent avatars showing with tooltips
- ✅ Loading spinners and progress bars
- ✅ Input fields with floating labels
- ✅ Agent message cards
- ✅ Glassmorphism effects
- ✅ All animations smooth

## Development Workflow

### Running the App

```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### File Structure

```
frontend/
├── app/                     # Next.js App Router
│   ├── layout.tsx          # Root layout with fonts
│   ├── page.tsx            # Home page
│   ├── globals.css         # Global styles + custom utilities
│   └── test/
│       └── page.tsx        # Design system showcase
│
├── components/
│   ├── theo/               # Custom Theo components
│   │   ├── TheoButton.tsx
│   │   ├── TheoCard.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── AgentAvatar.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── TheoInput.tsx
│   │   └── AgentMessage.tsx
│   │
│   ├── animations/         # Framer Motion wrappers
│   │   ├── FadeIn.tsx
│   │   ├── SlideIn.tsx
│   │   └── PulsingDot.tsx
│   │
│   └── ui/                 # shadcn/ui base components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── badge.tsx
│       ├── toast.tsx
│       ├── tooltip.tsx
│       └── avatar.tsx
│
├── lib/
│   └── utils.ts            # Utility functions + cn()
│
├── types/
│   └── index.ts            # TypeScript type definitions
│
└── public/                 # Static assets
```

### Key Configuration Files

- **package.json** - Dependencies and scripts
- **tsconfig.json** - TypeScript configuration
- **tailwind.config.ts** - Tailwind + brand colors
- **next.config.mjs** - Next.js configuration
- **postcss.config.mjs** - PostCSS for Tailwind
- **components.json** - shadcn/ui configuration

## Customization

### Adding New Colors

Edit `tailwind.config.ts`:

```typescript
colors: {
  // Add your custom color
  'custom-blue': '#0066FF',
}
```

### Adding New Components

1. Create file in `/components/theo/YourComponent.tsx`
2. Follow TypeScript + shadcn patterns
3. Add to `/app/test/page.tsx` for showcase

Example:

```typescript
"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface YourComponentProps {
  className?: string
  // ... your props
}

export function YourComponent({
  className,
  ...props
}: YourComponentProps) {
  return (
    <div className={cn("base-styles", className)} {...props}>
      {/* Your component */}
    </div>
  )
}
```

### Modifying Animations

Edit animation components in `/components/animations/`:

```typescript
// Adjust duration and delay
<FadeIn delay={0.5} duration={1.0}>
  {children}
</FadeIn>
```

## Troubleshooting

### Issue: Module not found errors

```bash
# Clear cache and reinstall
rm -rf node_modules
rm package-lock.json
npm install
```

### Issue: Tailwind styles not applying

1. Check `tailwind.config.ts` has correct content paths
2. Ensure `globals.css` imports Tailwind directives:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```
3. Restart dev server

### Issue: Fonts not loading

Fonts are loaded via Next.js font optimization:
```typescript
// app/layout.tsx
import { Inter, JetBrains_Mono } from "next/font/google"
```

If fonts don't load, check:
1. Font variables in tailwind.config.ts
2. className in layout.tsx includes font variables

### Issue: TypeScript errors

```bash
# Regenerate TypeScript types
npx next clean
rm -rf .next
npm run dev
```

### Issue: Build errors

```bash
# Check for errors
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

## Testing

### Manual Testing

1. Visit http://localhost:3000
2. Navigate to /test for design system
3. Check all components render
4. Test interactions (buttons, inputs)
5. Verify animations work
6. Check responsive design

### Browser Testing

Test in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Performance Testing

```bash
# Build for production
npm run build

# Check bundle size
npm run build -- --analyze  # (requires next-bundle-analyzer)
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub:
   ```bash
   git add .
   git commit -m "feat: Theo frontend complete"
   git push origin main
   ```

2. Import in Vercel:
   - Visit https://vercel.com
   - Click "New Project"
   - Import your repository
   - Framework preset: Next.js
   - Root directory: `frontend`

3. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

4. Deploy!

Vercel will auto-deploy on every push to main.

### Manual Deployment

```bash
# Build the app
npm run build

# Output is in .next folder
# Deploy entire project directory to your hosting
```

## Performance Optimization

### Bundle Size

Already optimized:
- Tree-shaking enabled
- Code splitting by route
- Dynamic imports for heavy components
- Font optimization with next/font
- Image optimization with next/image

### Loading Performance

- Server Components by default
- Client Components only where needed (marked with "use client")
- Suspense boundaries for async data
- Lazy loading for below-fold content

### Runtime Performance

- Framer Motion uses GPU acceleration
- CSS animations for simple transitions
- Debounced/throttled event handlers
- Memoized components where needed

## Next Steps

After setup:

1. ✅ Verify design system at /test
2. 📝 Build the actual design workspace
3. 🔌 Connect to backend API
4. 🧪 Add integration tests
5. 🚀 Deploy to Vercel

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [Framer Motion](https://www.framer.com/motion)
- [Radix UI](https://www.radix-ui.com)

## Support

For issues:
1. Check this SETUP.md
2. Review /test page for examples
3. Check main repository README
4. Open GitHub issue

---

**Theo Frontend** - Built with ❤️ using Next.js 14
