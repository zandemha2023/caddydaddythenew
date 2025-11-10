# Theo Frontend

Premium dark-mode AI design tool built with Next.js 14, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **Animations**: Framer Motion
- **State Management**: Zustand
- **Data Fetching**: TanStack Query
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or pnpm package manager

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update to your deployed backend URL.

## Design System

Visit `/test` route to see the complete design system showcase including:

- Color palette
- Buttons (primary, secondary, ghost, success, danger)
- Status badges
- Agent avatars
- Loading spinners
- Progress bars
- Input fields
- Agent messages
- Cards
- Typography

## Component Library

### Theo Components

Located in `/components/theo/`:

- **TheoButton** - Enhanced button with loading states, icons, and glow effects
- **TheoCard** - Glass-morphism cards with optional glow on hover
- **StatusBadge** - Status indicators for different agent states
- **AgentAvatar** - Circular avatars for AI agents with active states
- **LoadingSpinner** - Animated loading indicators
- **ProgressBar** - Gradient progress bars with velocity display
- **TheoInput** - Floating label inputs with icon support
- **AgentMessage** - Message cards showing agent communication

### Animation Components

Located in `/components/animations/`:

- **FadeIn** - Fade in animation with delay
- **SlideIn** - Slide from direction with customizable distance
- **PulsingDot** - Pulsing dot indicators for thinking states

### shadcn/ui Components

Located in `/components/ui/`:

- Button, Card, Input, Badge, Toast, Tooltip, Avatar

## Color System

### Brand Colors

```css
Primary: #00E5FF (Cyan)
Secondary: #9D4EDD (Purple)
Success: #00FF88 (Green)
Warning: #FFB020 (Orange)
Error: #FF4444 (Red)
```

### Agent Colors

```css
Requirements: #00E5FF (Cyan)
CAD: #9D4EDD (Purple)
Validation: #00FF88 (Green)
Export: #FFB020 (Orange)
```

### Background Colors

```css
Background: #0A0E14 (Dark blue-black)
Surface: #1A1F2E (Elevated dark blue)
Surface Elevated: #252B3B (Lighter elevated)
```

## Typography

- **Font Family**: Inter (sans-serif)
- **Mono Font**: JetBrains Mono
- **Font Weights**: 300, 400, 500, 600, 700

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── test/              # Design system showcase
├── components/
│   ├── theo/              # Custom Theo components
│   ├── animations/        # Animation components
│   └── ui/                # shadcn/ui components
├── lib/
│   └── utils.ts           # Utility functions
├── types/
│   └── index.ts           # TypeScript definitions
└── public/                # Static assets
```

## Building for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import repository in Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

### Manual Deployment

```bash
# Build
npm run build

# The .next folder contains the production build
# Deploy the entire project directory
```

## Development Guidelines

### Adding New Components

1. Create component in appropriate directory (`/components/theo/` or `/components/ui/`)
2. Use TypeScript for type safety
3. Follow existing naming conventions
4. Add to test page (`/app/test/page.tsx`) for showcase

### Styling Guidelines

- Use Tailwind utility classes
- Leverage `cn()` utility for conditional classes
- Use CSS variables for theme colors
- Follow dark mode design patterns
- Use glass-morphism for elevated surfaces

### Animation Guidelines

- Use Framer Motion for complex animations
- Keep animations subtle and smooth
- Use 300-500ms duration for most transitions
- Add delay for stagger effects

## API Integration

The frontend connects to the Theo backend API. See `/types/index.ts` for API type definitions.

### WebSocket Connection

```typescript
const ws = new WebSocket(`${process.env.NEXT_PUBLIC_API_URL}/ws/agent/${sessionId}`)

ws.onmessage = (event) => {
  const message = JSON.parse(event.data)
  // Handle real-time updates
}
```

## Performance

- Next.js 14 App Router for optimal performance
- React Server Components by default
- Image optimization with next/image
- Font optimization with next/font
- Code splitting and lazy loading

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT License - Part of Theo CAD Platform

## Support

For issues or questions, refer to the main repository README.
