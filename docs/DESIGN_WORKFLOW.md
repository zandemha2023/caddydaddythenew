# Design Workflow Guide

Complete guide for using the Theo CAD intelligent design system to generate 3D models from natural language.

## Overview

The Theo CAD platform uses two specialized AI agents to convert natural language descriptions into production-ready 3D models:

1. **Requirements Agent** - Extracts design specifications and asks clarifying questions
2. **CAD Agent** - Generates executable CadQuery code and creates 3D models

The complete workflow takes you from "Create a phone stand" to a downloadable STL file ready for 3D printing.

---

## Quick Start

### 1. Start Design Session

```bash
POST /api/v1/design/start
```

**Request:**
```json
{
  "prompt": "Create a mounting bracket 50mm x 30mm with 4 corner holes",
  "project_id": "optional-project-uuid"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Design session created. Connect to WebSocket for real-time updates."
}
```

### 2. Connect to WebSocket (Optional but Recommended)

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/design/ws/550e8400-...');

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log(msg.type, msg); // connected, agent_thinking, progress, code_generated, complete
};
```

### 3. Process Design Request

```bash
POST /api/v1/design/process
```

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Create a mounting bracket 50mm x 30mm with 4 corner holes"
}
```

**Response (if clarification needed):**
```json
{
  "session_id": "550e8400-...",
  "status": "awaiting_clarification",
  "questions": [
    "What diameter should the corner holes be?",
    "What material are you planning to use for 3D printing?",
    "What load or weight does this bracket need to support?"
  ],
  "confidence": 0.6,
  "message": "I need more information to proceed with the design."
}
```

### 4. Answer Clarifying Questions

```bash
POST /api/v1/design/process
```

**Request:**
```json
{
  "session_id": "550e8400-...",
  "message": "Holes should be 5mm diameter. Material is PLA. It needs to support 2kg weight."
}
```

**Response (when complete):**
```json
{
  "session_id": "550e8400-...",
  "status": "complete",
  "design_id": "750e8400-...",
  "file_id": "850e8400-...",
  "file_path": "/tmp/theo-cad/outputs/550e8400-....stl",
  "download_url": "/api/v1/design/550e8400-.../download",
  "message": "Design complete! Your 3D model is ready for download."
}
```

### 5. Download STL File

```bash
GET /api/v1/design/550e8400-.../download
```

Returns STL file with `Content-Type: model/stl`

---

## Design Examples

### Example 1: Simple Cube

**Initial Prompt:**
```
"Create a 50mm cube"
```

**Possible Questions:**
- "What material will you be using?"
- "Does it need to be solid or hollow?"
- "What tolerance do you need?"

**Final Requirements:**
```json
{
  "dimensions": {"length": "50mm", "width": "50mm", "height": "50mm"},
  "material": "PLA",
  "manufacturing_method": "FDM",
  "tolerances": "±0.2mm",
  "special_features": []
}
```

**Generated CadQuery Code:**
```python
import cadquery as cq

# Parameters
length = 50
width = 50
height = 50

# Base geometry
result = cq.Workplane("XY").box(length, width, height)

# Fillets for better printability
result = result.edges("|Z").fillet(2)

result
```

---

### Example 2: Phone Stand

**Initial Prompt:**
```
"Create a phone stand that holds phone at 60 degrees"
```

**Possible Questions:**
- "What are the dimensions of the phone (width and thickness)?"
- "How tall should the stand be?"
- "What size base do you want for stability?"
- "What material are you planning to use?"

**Enhanced Prompt:**
```
"Create a phone stand for a phone that's 80mm wide and 10mm thick. The stand should hold it at 60 degrees. Make the base 120mm x 80mm for stability. Use PLA material."
```

**Final Requirements:**
```json
{
  "dimensions": {
    "phone_width": "80mm",
    "phone_thickness": "10mm",
    "base_length": "120mm",
    "base_width": "80mm",
    "height": "100mm"
  },
  "material": "PLA",
  "manufacturing_method": "FDM",
  "functional_description": "Hold phone at 60-degree viewing angle",
  "special_features": ["angled support", "stable base"],
  "load_requirements": {"max_load": "200g", "direction": "vertical"}
}
```

**Generated Code Highlights:**
```python
import cadquery as cq
import math

# Parameters
phone_width = 80
phone_thickness = 10
base_length = 120
base_width = 80
angle = 60  # degrees

# Base
result = cq.Workplane("XY").box(base_length, base_width, 5)

# Angled support at 60 degrees
support = cq.Workplane("XY").transformed(rotate=(0, angle, 0))
support = support.box(phone_width + 20, base_width, 3)

result = result.union(support)

# Add fillets
result = result.edges("|Z").fillet(2)

result
```

---

### Example 3: Parametric Gear

**Initial Prompt:**
```
"Create a gear with 20 teeth, 50mm diameter"
```

**Possible Questions:**
- "What thickness should the gear be?"
- "Do you need a center bore for a shaft? If so, what diameter?"
- "What module (gear tooth size) do you need? Standard is 2.5 for this size."
- "What pressure angle? Standard is 20 degrees."

**Enhanced Prompt:**
```
"Create a gear with 20 teeth, 50mm diameter, 10mm thick, with a 6mm center bore for shaft. Module 2.5, pressure angle 20 degrees."
```

**Final Requirements:**
```json
{
  "dimensions": {
    "diameter": "50mm",
    "teeth_count": 20,
    "thickness": "10mm",
    "bore_diameter": "6mm",
    "module": 2.5
  },
  "material": "PLA",
  "special_features": ["involute teeth", "center bore"],
  "tolerances": "±0.1mm for bore"
}
```

---

## WebSocket Message Types

### Connected
```json
{
  "type": "connected",
  "job_id": "550e8400-...",
  "timestamp": "2025-01-10T12:00:00Z",
  "message": "Connected to agent stream"
}
```

### Agent Thinking
```json
{
  "type": "agent_thinking",
  "job_id": "550e8400-...",
  "agent": "requirements",
  "thinking": "Analyzing dimensions and extracting features...",
  "metadata": {"step": "analysis"},
  "timestamp": "2025-01-10T12:00:01Z"
}
```

### Progress Update
```json
{
  "type": "progress",
  "job_id": "550e8400-...",
  "progress": 50,
  "stage": "CAD Generation",
  "message": "Generating 3D model from requirements...",
  "metadata": {},
  "timestamp": "2025-01-10T12:00:05Z"
}
```

### Code Generated
```json
{
  "type": "code_generated",
  "job_id": "550e8400-...",
  "code_type": "cadquery",
  "code": "import cadquery as cq\n...",
  "line_count": 42,
  "timestamp": "2025-01-10T12:00:10Z"
}
```

### Complete
```json
{
  "type": "complete",
  "job_id": "550e8400-...",
  "success": true,
  "result": {
    "design_id": "750e8400-...",
    "file_id": "850e8400-...",
    "file_path": "/tmp/theo-cad/outputs/550e8400-....stl"
  },
  "timestamp": "2025-01-10T12:00:15Z"
}
```

### Error
```json
{
  "type": "error",
  "job_id": "550e8400-...",
  "error": "CadQuery execution failed: invalid syntax",
  "agent": "cad",
  "recoverable": true,
  "timestamp": "2025-01-10T12:00:08Z"
}
```

---

## Python Client Example

```python
import httpx
import asyncio
import json

async def create_design(prompt: str):
    """Create a design from natural language."""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        # Start session
        response = await client.post("/api/v1/design/start", json={
            "prompt": prompt
        })
        session_id = response.json()["session_id"]
        print(f"Session: {session_id}")

        # Process request
        response = await client.post("/api/v1/design/process", json={
            "session_id": session_id,
            "message": prompt
        })

        result = response.json()

        # Handle clarifications
        while result["status"] == "awaiting_clarification":
            print("\nQuestions:")
            for q in result["questions"]:
                print(f"  - {q}")

            answer = input("\nYour answer: ")

            response = await client.post("/api/v1/design/process", json={
                "session_id": session_id,
                "message": answer
            })
            result = response.json()

        # Download STL
        if result["status"] == "complete":
            print("\n✓ Design complete!")

            response = await client.get(f"/api/v1/design/{session_id}/download")
            with open(f"design_{session_id}.stl", "wb") as f:
                f.write(response.content)

            print(f"✓ STL saved: design_{session_id}.stl")

# Usage
asyncio.run(create_design("Create a 50mm cube with rounded edges"))
```

---

## JavaScript Client Example

```javascript
async function createDesign(prompt) {
    // Start session
    const startResponse = await fetch('http://localhost:8000/api/v1/design/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt})
    });

    const {session_id} = await startResponse.json();
    console.log('Session:', session_id);

    // Connect WebSocket for real-time updates
    const ws = new WebSocket(`ws://localhost:8000/api/v1/design/ws/${session_id}`);

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        switch(msg.type) {
            case 'agent_thinking':
                console.log(`${msg.agent}: ${msg.thinking}`);
                break;

            case 'progress':
                console.log(`${msg.stage}: ${msg.progress}%`);
                break;

            case 'code_generated':
                console.log('Code:', msg.code);
                break;

            case 'complete':
                console.log('✓ Complete!', msg.result);
                downloadSTL(session_id);
                ws.close();
                break;

            case 'error':
                console.error('Error:', msg.error);
                break;
        }
    };

    // Process request
    await fetch('http://localhost:8000/api/v1/design/process', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_id, message: prompt})
    });
}

async function downloadSTL(session_id) {
    const response = await fetch(`http://localhost:8000/api/v1/design/${session_id}/download`);
    const blob = await response.blob();

    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `design_${session_id}.stl`;
    a.click();
}

// Usage
createDesign('Create a phone stand at 60 degree angle');
```

---

## Best Practices for Prompts

### ✅ Good Prompts

**Be Specific About Dimensions:**
```
"Create a mounting bracket 50mm x 30mm x 20mm"
```

**Include Material:**
```
"Create a PLA phone stand for FDM printing"
```

**Mention Load Requirements:**
```
"Create a bracket that can support 5kg vertical load"
```

**Describe Features Clearly:**
```
"Create a box with 4 corner mounting holes (5mm diameter) and a cable slot on one side"
```

### ❌ Avoid Vague Prompts

**Too Vague:**
```
"Make a thing to hold my phone"
```

**Better:**
```
"Create a desk phone stand that holds an 80mm wide phone at 60-degree viewing angle"
```

---

## Troubleshooting

### Design Not Completing

**Problem:** Status stuck at "awaiting_clarification"

**Solution:** Answer all questions thoroughly. Include:
- Exact dimensions with units (mm preferred)
- Material choice (PLA, PETG, ABS, etc.)
- Load requirements if structural
- Any special features needed

### Code Execution Errors

**Problem:** CAD agent fails to generate valid code

**The system will automatically retry up to 3 times**

If still failing:
- Simplify the design
- Break complex designs into multiple parts
- Check requirements are clear and not contradictory

### STL File Not Downloading

**Problem:** 404 error on download

**Check:**
- Design status is "complete" (GET /api/v1/design/{id}/status)
- Session ID is correct
- File path exists in database

---

## Database Schema

Designs are automatically saved to:

**designs table:**
- id, project_id, name, original_prompt, current_version

**design_versions table:**
- id, design_id, version_number, prompt, parameters, cad_data, agent_trace

**cad_files table:**
- id, design_version_id, filename, file_format, file_path, checksum

Query design:
```sql
SELECT * FROM designs WHERE id = 'design-id';
SELECT * FROM cad_files WHERE design_version_id IN (
    SELECT id FROM design_versions WHERE design_id = 'design-id'
);
```

---

## Performance Metrics

Average timing:
- Simple designs (cube, box): 15-30 seconds
- Medium designs (phone stand, bracket): 30-60 seconds
- Complex designs (gear, mechanism): 60-120 seconds

Time breakdown:
- Requirements extraction: 5-15 seconds
- Clarifications (if needed): Variable (user input)
- CAD code generation: 10-30 seconds
- Code execution: 1-5 seconds
- STL export: 1-2 seconds

---

## Limitations

Current version limitations:
1. **Single-part designs only** - Multi-part assemblies not yet supported
2. **FDM/SLA focus** - Complex CNC features limited
3. **Geometric primitives** - Very complex organic shapes may fail
4. **No simulation** - Structural analysis not included
5. **English only** - Natural language processing in English

Planned improvements:
- Multi-part assembly support
- FEA structural analysis integration
- Slicing integration (G-code generation)
- Cost estimation
- Material property database

---

## Support

For issues or questions:
- Check `/docs` endpoint for API docs
- Review WebSocket messages for detailed errors
- Check logs for debugging information
- File issues on GitHub

---

## Next Steps

After getting your STL file:

1. **Slice for 3D Printing:**
   - PrusaSlicer (FDM): Import STL, configure printer, slice
   - Chitubox (SLA): Import STL, add supports, slice
   - Cura: Import STL, configure settings, generate G-code

2. **View/Edit:**
   - FreeCAD: Open STL, edit if needed
   - Blender: Import for visualization
   - MeshLab: Repair mesh if needed

3. **Print:**
   - Transfer G-code to printer
   - Check first layer adhesion
   - Monitor print progress

Enjoy your AI-generated 3D designs! 🎉
