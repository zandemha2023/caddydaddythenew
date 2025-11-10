# Design Workspace

The design workspace is the core "magic moment" of Theo where users create CAD designs with AI agents in real-time.

## Architecture

### Layout

**Desktop (3-column grid):**
- Left (30%): Agent Chat Panel
- Center (50%): 3D Viewer
- Right (20%): Specs & Export Panel

**Tablet (2-column):**
- Left (40%): Chat Panel
- Right (60%): 3D Viewer (top 66%) + Specs Panel (bottom 33%)

**Mobile (stacked):**
- Top (66%): 3D Viewer
- Bottom (33%): Chat Panel

## State Management

### Zustand Store (`stores/designStore.ts`)

Manages the entire design workflow state:

```typescript
{
  sessionId: string | null          // Current design session
  messages: AgentMessage[]          // Chat history
  status: 'idle' | 'processing' | 'awaiting_clarification' | 'complete' | 'error'
  modelUrl: string | null           // URL to 3D model file
  isConnected: boolean              // WebSocket connection status
  progress: number                  // 0-100
  currentAgent: string | null       // Active agent name
}
```

## Real-Time Communication

### WebSocket Hook (`hooks/useWebSocket.ts`)

Connects to backend WebSocket for real-time updates:

**Message Types:**
1. `connected` - WebSocket established
2. `agent_thinking` - Agent is processing
3. `progress` - Progress update (0-100%)
4. `code_generated` - CAD code created
5. `complete` - Design finished
6. `error` - Error occurred

**Features:**
- Auto-reconnect on disconnect
- Automatic message routing to store
- Progress tracking
- Error handling

## Components

### 1. Agent Chat Panel (`components/design/AgentChatPanel.tsx`)

**Features:**
- Message history with user and agent messages
- Real-time message streaming
- Suggested prompts
- Input field with submit button
- Auto-scroll to latest message
- Empty state with examples

**User Flow:**
1. User types design prompt
2. Click send or press Enter
3. Session created (first message only)
4. User message added to UI
5. Agent responses stream in
6. Can send follow-up messages anytime

**Suggested Prompts:**
- "Add 5mm mounting holes"
- "Make walls thicker"
- "Optimize for strength"
- "Reduce print time"

### 2. 3D Viewer (`components/design/ThreeViewer.tsx`)

**Features:**
- Three.js canvas with React Three Fiber
- Orbit controls (rotate, zoom, pan)
- Grid with 10mm cells
- Stage lighting
- City environment preset
- Reset view button
- Screenshot capture
- Progress bar overlay

**Controls:**
- Left mouse: Rotate
- Right mouse: Pan
- Scroll: Zoom
- Reset button: Return to default view

**States:**
- **Idle**: Empty state with placeholder
- **Processing**: Loading spinner + progress
- **Complete**: 3D model rendered
- **Error**: Error message

### 3. Specs Panel (`components/design/SpecsPanel.tsx`)

**Features:**
- Design status badge
- Current agent indicator
- Progress indicator
- Design parameters (dimensions, volume, weight)
- Print estimates (time, material, cost)
- Manufacturing notes
- Export buttons (STL, STEP)
- Getting started tips

**Design Parameters:**
- Dimensions (L×W×H)
- Volume (mm³)
- Weight (grams)
- Surface area (mm²)

**Print Estimates:**
- Print time (hours:minutes)
- Material used (grams)
- Cost estimate ($)
- Success rate (%)

**Manufacturing Notes:**
- Support requirements
- Overhang angles
- Wall thickness validation
- Print orientation recommendations

## API Integration

### Client (`lib/api.ts`)

**Functions:**

1. `startDesignSession(prompt, projectId?)`
   - POST `/api/v1/design/start`
   - Creates new design session
   - Returns session_id

2. `sendMessage(sessionId, message)`
   - POST `/api/v1/design/process`
   - Sends user message or clarification
   - Returns process result

3. `getDesignStatus(sessionId)`
   - GET `/api/v1/design/{sessionId}/status`
   - Gets current session status

4. `downloadFile(sessionId)`
   - GET `/api/v1/design/{sessionId}/download`
   - Downloads STL file
   - Triggers browser download

## Workflow

### Complete Design Flow

```
1. User enters prompt
   ↓
2. POST /api/v1/design/start
   ↓
3. Session created, WebSocket connected
   ↓
4. Requirements Agent analyzes prompt
   ↓
5. [Optional] Asks clarifying questions
   ↓
6. User answers questions
   ↓
7. CAD Agent generates CadQuery code
   ↓
8. Code executed, STL generated
   ↓
9. Model URL sent via WebSocket
   ↓
10. 3D viewer loads and displays model
   ↓
11. User can download STL
```

### Message Flow

```
User Message → API → Backend
                ↓
          Requirements Agent
                ↓
          WebSocket → Frontend
                ↓
          Message displayed
                ↓
          CAD Agent starts
                ↓
          Progress updates
                ↓
          Model complete
                ↓
          3D Viewer updates
```

## Testing Locally

### 1. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

### 3. Navigate to Design Page

```
http://localhost:3000/design
```

### 4. Test Complete Flow

**Simple Cube:**
1. Enter: "Create a 50mm cube"
2. Watch agents process
3. See 3D model appear
4. Download STL

**Phone Stand:**
1. Enter: "Design a phone stand at 60 degrees"
2. Agent may ask for dimensions
3. Answer: "Base 80mm, height 100mm"
4. Watch model generate
5. Download STL

**Mounting Bracket:**
1. Enter: "Create a mounting bracket 50mm x 30mm with 4 corner holes"
2. Agent may ask for hole diameter
3. Answer: "5mm holes"
4. See model in 3D viewer
5. Check specs panel for print estimates
6. Download STL

## Customization

### Adding New Agent Types

1. Update `types/index.ts`:
   ```typescript
   export type AgentType = 'requirements' | 'cad' | 'validation' | 'export' | 'your-agent'
   ```

2. Update `lib/utils.ts`:
   ```typescript
   const colors = {
     // ...existing
     'your-agent': '#COLOR',
   }
   ```

3. Update `components/theo/AgentAvatar.tsx`:
   ```typescript
   const agentIcons = {
     // ...existing
     'your-agent': <YourIcon className="h-4 w-4" />,
   }
   ```

### Customizing 3D Viewer

**Change Camera Position:**
```typescript
<PerspectiveCamera makeDefault position={[x, y, z]} fov={50} />
```

**Change Grid:**
```typescript
<Grid
  args={[width, height]}
  cellSize={size}
  cellColor="#color"
/>
```

**Change Lighting:**
```typescript
<ambientLight intensity={0.5} />
<directionalLight position={[x, y, z]} intensity={1} />
```

### Customizing Specs Panel

Edit `components/design/SpecsPanel.tsx`:

```typescript
// Add custom parameters
<div className="flex justify-between">
  <span className="text-text-secondary">Your Param</span>
  <span className="font-mono text-text-primary">{value}</span>
</div>
```

## Troubleshooting

### WebSocket Not Connecting

1. Check API URL in `.env.local`
2. Ensure backend is running
3. Check browser console for errors
4. Verify WebSocket endpoint: `ws://localhost:8000/api/v1/design/ws/{sessionId}`

### 3D Model Not Appearing

1. Check WebSocket received `complete` message
2. Verify `modelUrl` in store
3. Check browser console for Three.js errors
4. Ensure STL file exists at download URL

### Messages Not Appearing

1. Check WebSocket connection status
2. Verify messages in store (use React DevTools)
3. Check message type handling in useWebSocket
4. Ensure AgentMessage component renders correctly

### Download Not Working

1. Check session_id is valid
2. Verify backend file exists
3. Check CORS headers
4. Try direct URL in browser

## Performance Optimization

### Reduce Re-renders

```typescript
// Use React.memo for expensive components
export const AgentMessage = React.memo(AgentMessageComponent)

// Use useCallback for handlers
const handleSubmit = useCallback(async () => {
  // ...
}, [dependencies])
```

### Optimize 3D Rendering

```typescript
// Lower device pixel ratio for slower devices
<Canvas dpr={[1, 1.5]}>

// Reduce geometry complexity
<boxGeometry args={[x, y, z], segments={1, 1, 1}} />

// Use LOD (Level of Detail)
import { Lod } from '@react-three/drei'
```

### Lazy Load Components

```typescript
const ThreeViewer = dynamic(() => import('@/components/design/ThreeViewer'), {
  ssr: false,
  loading: () => <LoadingSpinner />
})
```

## Future Enhancements

- [ ] Multiple file format exports (STEP, OBJ, GLTF)
- [ ] STL file loading and rendering
- [ ] Print preview mode
- [ ] Measurement tools
- [ ] Section view
- [ ] Material selection
- [ ] Multi-part assemblies
- [ ] Design history/versions
- [ ] Collaborative design
- [ ] Voice input
- [ ] AR preview on mobile

---

**Built with React, Three.js, and Zustand**
