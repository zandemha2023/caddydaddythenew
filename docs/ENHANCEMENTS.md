# Theo CAD Platform - Advanced Features

This document details the advanced features added to the Theo CAD platform.

## Overview

Four major enhancements have been implemented:

1. **Enhanced Database Schema** - 6 new tables with comprehensive relationships
2. **Agent Orchestration with Tool Use** - Claude's tool use API for structured agent interactions
3. **Real-Time WebSocket Streaming** - Live agent thinking and progress updates
4. **Printer Profiles System** - Support for 7 printer types (FDM, SLA, Industrial)

---

## 1. Enhanced Database Schema

### New Tables

#### `agent_conversations`
Tracks all agent interactions with full conversation history:
```sql
- id (PK)
- design_id (FK) - Links to design
- job_id (FK) - Links to job
- agent_type - requirements/cad/validation/export
- message_index - Position in conversation
- role - user/assistant/tool
- content - Message content
- tool_calls - JSON of tool calls made
- tool_results - JSON of tool results
- metadata - Additional data
- tokens_used - API token usage
- created_at
```

**Indexes:**
- `idx_conversation_design_agent` on (design_id, agent_type, message_index)
- `idx_conversation_job` on (job_id, created_at)

#### `cad_files`
Manages generated 3D files:
```sql
- id (PK)
- design_version_id (FK)
- print_job_id (FK)
- filename
- file_format - stl/step/obj/dxf/gcode/svg/scad/cq/3mf/amf
- file_path
- file_size (bytes)
- checksum (SHA-256)
- is_primary (bool)
- metadata JSON - bounds, vertex_count, face_count, etc.
- created_at
```

**Indexes:**
- `idx_cad_file_version_format` on (design_version_id, file_format)
- `idx_cad_file_checksum` on (checksum)

#### `print_jobs`
Tracks manufacturing jobs:
```sql
- id (PK)
- design_id (FK)
- printer_profile_id (FK)
- user_id (FK)
- status - queued/preparing/slicing/ready/printing/completed/failed/cancelled
- material
- material_color
- layer_height (decimal)
- infill_density (%)
- support_enabled (bool)
- estimated_time (minutes)
- estimated_material (grams)
- estimated_cost (USD)
- actual_time
- gcode_file_path
- slice_settings JSON
- print_settings JSON
- notes
- started_at, completed_at, created_at, updated_at
```

**Indexes:**
- `idx_print_job_user_status` on (user_id, status)
- `idx_print_job_created` on (created_at)

#### `printer_profiles`
Printer specifications:
```sql
- id (PK)
- name
- manufacturer - prusa/bambu_lab/creality/formlabs/elegoo/stratasys/eos/etc
- model
- technology - fdm/sla/sls/mjf/binder_jet/dmls/polyjet
- build_volume_x/y/z (mm)
- min/max_layer_height (mm)
- xy_resolution (mm)
- dimensional_accuracy (±mm)
- supported_materials JSON
- max_nozzle_temp, max_bed_temp (°C)
- heated_chamber (bool)
- max_print_speed, recommended_print_speed (mm/s)
- auto_bed_leveling (bool)
- filament_runout_detection (bool)
- power_loss_recovery (bool)
- multi_material (bool)
- post_processing JSON
- compatible_slicers JSON array
- default_profile_settings JSON
- is_active, is_industrial (bool)
- created_at, updated_at
```

**Indexes:**
- `idx_printer_profile_tech_mfr` on (technology, manufacturer)
- `idx_printer_profile_active` on (is_active)

#### `manufacturing_parameters`
Printer-specific settings (1-to-1 with printer_profile):
```sql
- id (PK)
- printer_profile_id (FK, unique)
- wall_thickness, wall_line_count
- top_layers, bottom_layers
- default_infill_density, infill_pattern
- support_type, support_density, support_z_distance
- build_plate_adhesion, brim_width
- default_nozzle_temp, default_bed_temp
- print_speed, travel_speed, initial_layer_speed
- retraction_enabled, retraction_distance, retraction_speed
- cooling_enabled, min_fan_speed, max_fan_speed
- adaptive_layer_height, smooth_spiralized_contours
- horizontal_expansion, hole_horizontal_expansion
- material_overrides JSON
- advanced_settings JSON
- created_at, updated_at
```

### Database Relationships

```
User
├── Projects (1:N)
└── PrintJobs (1:N)

Project
└── Designs (1:N)

Design
├── DesignVersions (1:N)
├── Jobs (1:N)
├── AgentConversations (1:N)
└── PrintJobs (1:N)

DesignVersion
└── CADFiles (1:N)

Job
└── AgentConversations (1:N)

PrinterProfile
├── ManufacturingParameters (1:1)
└── PrintJobs (1:N)

PrintJob
└── CADFiles (1:N)
```

---

## 2. Enhanced Agent Orchestration

### Tool Definitions

Each agent type has specialized tools:

#### Requirements Agent Tools

**extract_dimensions**
- Extracts length, width, height, diameter, thickness
- Supports mm, cm, m, in, ft units

**identify_features**
- Identifies holes, fillets, chamfers, threads, slots, grooves, bosses, ribs
- Captures quantity, diameter, depth, radius, location

**determine_material**
- Suggests PLA, PETG, ABS, TPU, Nylon, Resin, Metal
- Provides reasoning and required properties

**set_tolerances**
- Sets general tolerance (±mm)
- Defines critical tolerances for specific features
- Specifies fit types (clearance/transition/interference)

#### CAD Agent Tools

**generate_cadquery_code**
- Generates complete Python CadQuery code
- Validates presence of required imports
- Captures parameters and description
- Returns line count

**generate_openscad_code**
- Generates OpenSCAD code for simpler geometries
- Alternative to CadQuery

**add_assembly_instructions**
- Defines parts list with quantities and materials
- Provides step-by-step assembly instructions

#### Validation Agent Tools

**check_printability**
- Analyzes for FDM/SLA/SLS/MJF compatibility
- Identifies issues with severity levels
- Estimates support requirements and print time

**validate_dimensions**
- Checks fit within build volume
- Calculates build volume usage percentage
- Reports dimension errors

**check_structural_integrity**
- Identifies weak points with recommendations
- Validates minimum wall thickness
- Finds stress concentration points

#### Export Agent Tools

**configure_stl_export**
- Sets resolution (low/medium/high/ultra)
- Binary vs ASCII format
- Tessellation tolerance

**generate_gcode_settings**
- Printer-specific settings
- Layer height, infill density, supports
- Temperature profiles

**optimize_for_printer**
- Printer model-specific optimizations

### Enhanced Base Agent

`EnhancedBaseAgent` class features:

```python
class EnhancedBaseAgent(ABC):
    def __init__(self, agent_type: str, db_session: Optional[AsyncSession])

    async def send_message_with_tools(...) -> Message
    async def process_tool_calls(...) -> List[Dict[str, Any]]
    async def execute_tool(...) -> Dict[str, Any]
    async def _save_conversation(...) -> None

    # Abstract methods
    def get_system_prompt() -> str
    async def process(...) -> Dict[str, Any]
```

Key features:
- Automatic conversation tracking to database
- Tool call execution with error handling
- Token usage tracking
- Multi-turn conversations with tool results

### Agent Implementations

#### RequirementsAgent
- Analyzes natural language prompts
- Extracts dimensions, features, materials, tolerances
- Uses tools to structure data
- Returns comprehensive requirements dictionary

#### CADAgent
- Takes requirements from RequirementsAgent
- Generates CadQuery or OpenSCAD code
- Validates code structure
- Provides assembly instructions for multi-part designs

System prompt includes:
- CadQuery best practices
- Manufacturing considerations
- Minimum wall thickness guidelines
- Overhang angle limits
- Print orientation advice

---

## 3. WebSocket Real-Time Streaming

### AgentStreamManager

Located in `backend/app/api/websockets/agent_stream.py`

#### Features

**Connection Management**
```python
await agent_stream_manager.connect(websocket, job_id)
agent_stream_manager.disconnect(websocket, job_id)
```

**Streaming Methods**

```python
# Agent thinking/reasoning
await stream_agent_thinking(job_id, agent_type, thinking, metadata)

# Tool usage
await stream_tool_use(job_id, agent_type, tool_name, tool_input, tool_result)

# Progress updates
await stream_progress(job_id, progress, stage, message, metadata)

# Code generation
await stream_code_generation(job_id, code_type, code, line_count)

# Validation results
await stream_validation_results(job_id, valid, score, issues, recommendations)

# Errors
await stream_error(job_id, error, agent, recoverable)

# Completion
await stream_completion(job_id, success, result)
```

#### Message Types

**Connected**
```json
{
  "type": "connected",
  "job_id": "uuid",
  "timestamp": "ISO-8601",
  "message": "Connected to agent stream"
}
```

**Agent Thinking**
```json
{
  "type": "agent_thinking",
  "job_id": "uuid",
  "agent": "requirements",
  "thinking": "Analyzing the bracket design...",
  "metadata": {},
  "timestamp": "ISO-8601"
}
```

**Tool Use**
```json
{
  "type": "tool_use",
  "job_id": "uuid",
  "agent": "requirements",
  "tool": "extract_dimensions",
  "input": {"length": 50, "width": 30, "units": "mm"},
  "result": {"success": true, "dimensions": {...}},
  "timestamp": "ISO-8601"
}
```

**Progress**
```json
{
  "type": "progress",
  "job_id": "uuid",
  "progress": 45,
  "stage": "Generating CAD code",
  "message": "Creating parametric model...",
  "metadata": {},
  "timestamp": "ISO-8601"
}
```

**Code Generated**
```json
{
  "type": "code_generated",
  "job_id": "uuid",
  "code_type": "cadquery",
  "code": "import cadquery as cq\n...",
  "line_count": 42,
  "timestamp": "ISO-8601"
}
```

#### Redis Caching

All messages are cached in Redis with 1-hour expiry:
```
Key: job:{job_id}:stream
Value: Latest message JSON
TTL: 3600 seconds
```

Allows late-joining clients to get current status.

---

## 4. Printer Profiles System

### Pre-Configured Profiles

#### FDM Printers

**Prusa i3 MK3S+**
- Build volume: 250×210×210mm
- Layer height: 0.05-0.35mm
- Materials: PLA, PETG, ABS, TPU
- Features: Auto bed leveling, filament runout, power recovery
- Max nozzle: 300°C, Max bed: 120°C

**Bambu Lab X1 Carbon**
- Build volume: 256×256×256mm
- Layer height: 0.08-0.28mm
- Materials: PLA, PETG, ABS, TPU, Nylon, PC
- Features: Heated chamber, multi-material (AMS), 500mm/s max speed
- Resolution: 0.05mm XY

**Creality Ender 3 V2**
- Build volume: 220×220×250mm
- Layer height: 0.1-0.4mm
- Materials: PLA, PETG, ABS, TPU
- Budget-friendly entry-level printer

#### SLA Printers

**Formlabs Form 3+**
- Build volume: 145×145×185mm
- Layer height: 0.025-0.1mm
- Resolution: 0.025mm XY, ±0.05mm accuracy
- Materials: Standard, Tough, Flexible, Castable, Dental resins
- Post-processing: IPA wash, UV curing

**Elegoo Mars 3 Pro**
- Build volume: 143.43×89.6×175mm
- Layer height: 0.01-0.2mm
- Resolution: 0.035mm XY
- Materials: Standard, ABS-like, Water-washable, Plant-based resins

#### Industrial Printers

**Stratasys F900**
- Build volume: 914×610×914mm (huge!)
- Layer height: 0.127-0.508mm
- Materials: ABS-M30, PC-ABS, ULTEM 9085/1010, Nylon 12, ASA
- Features: Heated chamber, multi-material, soluble supports
- Industrial-grade precision

**EOS P 396 (SLS)**
- Build volume: 340×340×600mm
- Layer height: 0.06-0.15mm
- Technology: Selective Laser Sintering
- Materials: PA 2200, PA 1101, PA 3200 GF, TPU 1301 (powder)
- No supports needed, complex geometries

### Service API

```python
from app.services.printer_profiles import PrinterProfilesService

service = PrinterProfilesService(db)

# Get by name
profile = await service.get_profile_by_name("Prusa i3 MK3S+")

# List with filtering
profiles = await service.list_profiles(
    technology=PrinterTechnology.FDM,
    manufacturer=PrinterManufacturer.PRUSA,
    active_only=True
)

# Seed database
await service.seed_default_profiles()
```

### API Endpoints

```
GET /api/v1/printer-profiles
  ?technology=fdm
  &manufacturer=prusa
  &active_only=true

GET /api/v1/printer-profiles/{id}
GET /api/v1/printer-profiles/by-name/{name}
GET /api/v1/printer-profiles/technologies
GET /api/v1/printer-profiles/manufacturers
POST /api/v1/printer-profiles/seed

POST /api/v1/print-jobs
GET /api/v1/print-jobs?design_id={id}&status={status}
GET /api/v1/print-jobs/{id}
PATCH /api/v1/print-jobs/{id}/status
```

---

## Usage Examples

### 1. Create Design with Agent Tracking

```python
from app.services.agents.requirements_agent import RequirementsAgent
from app.services.agents.cad_agent import CADAgent

async with get_db() as db:
    # Requirements extraction
    req_agent = RequirementsAgent(db_session=db)
    requirements = await req_agent.process(
        input_data={
            "prompt": "Create a mounting bracket 50mm x 30mm with 4 corner holes",
            "parameters": {"hole_diameter": 3.2}
        },
        design_id=design_id,
        job_id=job_id
    )

    # CAD generation
    cad_agent = CADAgent(db_session=db)
    cad_result = await cad_agent.process(
        input_data={
            "requirements": requirements,
            "prompt": "Create a mounting bracket...",
            "parameters": {}
        },
        design_id=design_id,
        job_id=job_id
    )

    # All conversations are automatically saved to agent_conversations table
```

### 2. Stream Agent Progress to Frontend

```python
from app.api.websockets.agent_stream import agent_stream_manager

# During agent processing
await agent_stream_manager.stream_agent_thinking(
    job_id=job_id,
    agent_type="requirements",
    thinking="Analyzing bracket dimensions from prompt...",
    metadata={"step": 1, "total_steps": 4}
)

await agent_stream_manager.stream_tool_use(
    job_id=job_id,
    agent_type="requirements",
    tool_name="extract_dimensions",
    tool_input={"length": 50, "width": 30, "units": "mm"},
    tool_result={"success": True, "dimensions": {...}}
)

await agent_stream_manager.stream_progress(
    job_id=job_id,
    progress=25,
    stage="Requirements Analysis",
    message="Extracted dimensions and features"
)
```

### 3. Create Print Job

```python
from app.schemas.printer_profile import PrintJobCreate

# Create print job
print_job = PrintJobCreate(
    design_id=design_id,
    printer_profile_id=profile_id,
    material="PLA",
    material_color="Red",
    layer_height=0.2,
    infill_density=20,
    support_enabled=True,
    notes="Prototype run"
)

job = await create_print_job(print_job, db)
# Returns job with estimated time, material usage, and cost
```

### 4. Query Printer Profiles

```python
# Get all FDM printers
fdm_printers = await service.list_profiles(
    technology=PrinterTechnology.FDM
)

# Get specific printer with parameters
profile = await service.get_profile_by_name("Bambu Lab X1 Carbon")
print(f"Build volume: {profile.build_volume_x}×{profile.build_volume_y}×{profile.build_volume_z}mm")
print(f"Max speed: {profile.max_print_speed}mm/s")
print(f"Materials: {list(profile.supported_materials.keys())}")
print(f"Parameters: {profile.manufacturing_parameters.print_speed}mm/s default")
```

---

## Database Migrations

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add advanced features"
```

### Apply Migration

```bash
alembic upgrade head
```

### Seed Printer Profiles

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/printer-profiles/seed

# Or via Python
from app.services.printer_profiles import PrinterProfilesService
async with get_db() as db:
    service = PrinterProfilesService(db)
    await service.seed_default_profiles()
```

---

## Testing

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent/{job_id}');

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    switch(msg.type) {
        case 'connected':
            console.log('Connected to agent stream');
            break;
        case 'agent_thinking':
            console.log(`${msg.agent}: ${msg.thinking}`);
            break;
        case 'tool_use':
            console.log(`Tool: ${msg.tool}`, msg.result);
            break;
        case 'progress':
            updateProgressBar(msg.progress, msg.stage);
            break;
        case 'code_generated':
            displayCode(msg.code, msg.code_type);
            break;
    }
};
```

### API Testing

```bash
# List FDM printers
curl http://localhost:8000/api/v1/printer-profiles?technology=fdm

# Get specific printer
curl http://localhost:8000/api/v1/printer-profiles/by-name/Prusa%20i3%20MK3S+

# Create print job
curl -X POST http://localhost:8000/api/v1/print-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "design_id": "uuid",
    "printer_profile_id": "uuid",
    "material": "PLA",
    "layer_height": 0.2,
    "infill_density": 20
  }'
```

---

## Performance Considerations

1. **Database Indexes**: Composite indexes on frequently queried columns
2. **Redis Caching**: WebSocket messages cached for 1 hour
3. **Connection Pooling**: 20 database connections, 50 Redis connections
4. **JSON Storage**: Flexible metadata without schema migrations
5. **Lazy Loading**: Use `selectinload()` for relationships
6. **Pagination**: All list endpoints support skip/limit

---

## Future Enhancements

- [ ] Validation and Export agents with tool use
- [ ] 3D file upload and parsing
- [ ] Cost estimation based on material and time
- [ ] Slicing integration (PrusaSlicer API)
- [ ] G-code preview and analysis
- [ ] Print failure detection
- [ ] Multi-language support for prompts
- [ ] Design library and marketplace
- [ ] Collaborative design sessions
- [ ] AR preview of models

---

## Security Notes

- All file paths stored with checksums (SHA-256)
- Tool inputs validated before execution
- Database transactions for consistency
- Cascade deletes prevent orphaned records
- Enum types prevent invalid status values
- Decimal types for precise measurements

---

## Monitoring

Track these metrics:
- Agent conversation lengths
- Tool call success rates
- Token usage per agent type
- Print job success rates
- WebSocket connection count
- Database query performance

Use structured logging to analyze agent behavior:
```python
logger.info("tool_executed",
    agent="requirements",
    tool="extract_dimensions",
    success=True,
    tokens=156
)
```
