# Theo CAD API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently in development mode. Production will use JWT tokens.

## Endpoints

### Health Check

#### GET /health
Basic health check.

**Response**:
```json
{
  "status": "healthy",
  "service": "theo-cad"
}
```

#### GET /health/detailed
Detailed health check with component status.

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

---

### CAD Generation

#### POST /api/v1/cad/generate
Generate a 3D CAD model from natural language.

**Request Body**:
```json
{
  "prompt": "Create a mounting bracket 50mm x 30mm with 4 corner holes",
  "project_id": "optional-project-id",
  "design_id": "optional-design-id",
  "export_formats": ["stl", "step"],
  "printer_type": "fdm",
  "parameters": {
    "hole_diameter": 3.2,
    "wall_thickness": 2.5
  }
}
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "design_id": "650e8400-e29b-41d4-a716-446655440001",
  "status": "queued",
  "message": "CAD generation job has been queued",
  "estimated_time": 300
}
```

**Export Formats**:
- `stl` - Standard Tessellation Language
- `step` - STEP format
- `obj` - Wavefront OBJ
- `dxf` - Drawing Exchange Format
- `gcode` - G-code
- `svg` - Scalable Vector Graphics

**Printer Types**:
- `fdm` - Fused Deposition Modeling
- `sla` - Stereolithography
- `sls` - Selective Laser Sintering
- `cnc` - CNC Milling
- `laser` - Laser Cutting

#### GET /api/v1/cad/formats
List all supported export formats.

**Response**:
```json
{
  "formats": [
    {
      "name": "STL",
      "extension": "stl",
      "description": "Standard Tessellation Language - for 3D printing",
      "binary": true
    }
  ]
}
```

---

### Projects

#### POST /api/v1/projects
Create a new project.

**Request Body**:
```json
{
  "name": "My CAD Project",
  "description": "Project for mechanical parts"
}
```

**Response**:
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440000",
  "name": "My CAD Project",
  "description": "Project for mechanical parts",
  "owner_id": "user-id",
  "created_at": "2025-01-10T12:00:00Z",
  "updated_at": "2025-01-10T12:00:00Z"
}
```

#### GET /api/v1/projects
List all projects.

**Query Parameters**:
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)

**Response**:
```json
[
  {
    "id": "750e8400-e29b-41d4-a716-446655440000",
    "name": "My CAD Project",
    "description": "Project for mechanical parts",
    "owner_id": "user-id",
    "created_at": "2025-01-10T12:00:00Z",
    "updated_at": "2025-01-10T12:00:00Z"
  }
]
```

#### GET /api/v1/projects/{project_id}
Get project details.

**Response**: Same as POST response.

#### PATCH /api/v1/projects/{project_id}
Update a project.

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

#### DELETE /api/v1/projects/{project_id}
Delete a project.

**Response**: 204 No Content

---

### Designs

#### POST /api/v1/designs
Create a new design.

**Request Body**:
```json
{
  "project_id": "750e8400-e29b-41d4-a716-446655440000",
  "name": "Bracket Design",
  "description": "Mounting bracket",
  "original_prompt": "Create a mounting bracket..."
}
```

**Response**:
```json
{
  "id": "850e8400-e29b-41d4-a716-446655440000",
  "project_id": "750e8400-e29b-41d4-a716-446655440000",
  "name": "Bracket Design",
  "description": "Mounting bracket",
  "original_prompt": "Create a mounting bracket...",
  "current_version": 1,
  "created_at": "2025-01-10T12:00:00Z",
  "updated_at": "2025-01-10T12:00:00Z",
  "versions": []
}
```

#### GET /api/v1/designs
List all designs.

**Query Parameters**:
- `project_id` (string): Filter by project
- `skip` (int): Number to skip
- `limit` (int): Maximum to return

#### GET /api/v1/designs/{design_id}
Get design with all versions.

**Response**:
```json
{
  "id": "850e8400-e29b-41d4-a716-446655440000",
  "name": "Bracket Design",
  "current_version": 2,
  "versions": [
    {
      "id": "version-id",
      "version_number": 2,
      "prompt": "Modified bracket...",
      "parameters": {},
      "cad_data": {},
      "created_at": "2025-01-10T13:00:00Z"
    }
  ]
}
```

---

### Jobs

#### GET /api/v1/jobs
List all jobs.

**Query Parameters**:
- `design_id` (string): Filter by design
- `skip` (int): Number to skip
- `limit` (int): Maximum to return

**Response**:
```json
[
  {
    "id": "950e8400-e29b-41d4-a716-446655440000",
    "design_id": "850e8400-e29b-41d4-a716-446655440000",
    "job_type": "design_generation",
    "status": "completed",
    "progress": 100,
    "result_data": {},
    "created_at": "2025-01-10T12:00:00Z"
  }
]
```

#### GET /api/v1/jobs/{job_id}
Get job status.

**Response**:
```json
{
  "id": "950e8400-e29b-41d4-a716-446655440000",
  "job_type": "design_generation",
  "status": "processing",
  "progress": 45,
  "started_at": "2025-01-10T12:00:00Z",
  "input_data": {},
  "result_data": null
}
```

**Job Statuses**:
- `pending` - Waiting to start
- `processing` - Currently running
- `completed` - Successfully finished
- `failed` - Error occurred
- `cancelled` - Manually cancelled

#### DELETE /api/v1/jobs/{job_id}
Cancel a running job.

**Response**: 204 No Content

---

## WebSocket API

### WS /ws/agent/{job_id}
Real-time agent updates for a job.

**Connect**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent/{job_id}');
```

**Client Messages**:
```json
{
  "type": "ping"
}
```

```json
{
  "type": "status_request"
}
```

**Server Messages**:

Connection established:
```json
{
  "type": "connected",
  "job_id": "job-id",
  "timestamp": "2025-01-10T12:00:00Z",
  "message": "Connected to agent updates"
}
```

Agent update:
```json
{
  "type": "agent_update",
  "job_id": "job-id",
  "data": {
    "status": "processing",
    "progress": 45,
    "current_agent": "designer",
    "message": "Generating CAD code..."
  },
  "timestamp": "2025-01-10T12:00:00Z"
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request**:
```json
{
  "detail": "Invalid input parameters"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting
Currently not implemented. Will be added in production.

## Pagination
List endpoints support `skip` and `limit` parameters for pagination.

## Interactive Documentation
Visit `/docs` for Swagger UI or `/redoc` for ReDoc.
