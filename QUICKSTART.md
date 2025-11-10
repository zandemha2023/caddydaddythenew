# Theo CAD - Quick Start Guide

Complete guide to get the Theo CAD intelligent design system running locally and in production.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+
- Redis 7+
- Anthropic API key (get from https://console.anthropic.com/)
- Docker (optional, for easier service management)

## Local Development Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd caddydaddythenew

# Copy environment template
cp .env.example .env

# Edit .env and set your API key
nano .env  # Set ANTHROPIC_API_KEY=your-actual-key
```

### 2. Start Services with Docker (Recommended)

```bash
# Start PostgreSQL
docker run -d --name theo-postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=theo_cad \
  -p 5432:5432 \
  postgres:16

# Start Redis
docker run -d --name theo-redis \
  -p 6379:6379 \
  redis:7-alpine

# Verify services are running
docker ps
```

### 3. Install Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify CadQuery installation
python -c "import cadquery as cq; print(f'CadQuery {cq.__version__} installed')"
```

### 4. Run Database Migrations

```bash
# Still in backend/ directory
alembic upgrade head
```

### 5. Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 6. Validate Installation

```bash
# Run import validation
python scripts/validate_imports.py

# Should see:
# ✓ All tests passed! System is ready.
```

## Testing the Workflow

### Quick Test (Interactive)

```bash
# Make sure server is running in another terminal
python scripts/test_design.py
```

This will:
1. Start a design session
2. Submit a design request
3. Handle any clarifying questions
4. Download the generated STL file

### Automated Tests

```bash
cd backend
pytest tests/test_design_workflow.py -v
```

Tests include:
- Simple design (50mm cube)
- Medium complexity (phone stand at 60°)
- Complex design (gear with 20 teeth)
- WebSocket streaming

## Example Usage

### Python Client

```python
import asyncio
import httpx

async def create_bracket():
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        # Start session
        response = await client.post("/api/v1/design/start", json={
            "prompt": "Create a mounting bracket 50mm x 30mm with 4 corner holes"
        })
        session_id = response.json()["session_id"]
        print(f"Session: {session_id}")

        # Process request
        response = await client.post("/api/v1/design/process", json={
            "session_id": session_id,
            "message": "5mm holes, PLA material, needs to support 2kg"
        })
        result = response.json()

        # Handle clarifications
        while result["status"] == "awaiting_clarification":
            print(f"Questions: {result['questions']}")
            answer = input("Your answer: ")

            response = await client.post("/api/v1/design/process", json={
                "session_id": session_id,
                "message": answer
            })
            result = response.json()

        # Download STL
        if result["status"] == "complete":
            response = await client.get(f"/api/v1/design/{session_id}/download")
            with open(f"bracket_{session_id}.stl", "wb") as f:
                f.write(response.content)
            print(f"✓ STL saved: bracket_{session_id}.stl")

asyncio.run(create_bracket())
```

### cURL

```bash
# Start session
SESSION_ID=$(curl -X POST http://localhost:8000/api/v1/design/start \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a 50mm cube"}' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# Process design
curl -X POST http://localhost:8000/api/v1/design/process \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"Create a 50mm cube, PLA material\"}"

# Check status
curl http://localhost:8000/api/v1/design/$SESSION_ID/status

# Download STL (once complete)
curl -O http://localhost:8000/api/v1/design/$SESSION_ID/download
```

## Railway Deployment

### Prerequisites

1. Railway account (https://railway.app)
2. Railway CLI installed: `npm install -g @railway/cli`
3. GitHub repository connected to Railway

### Deploy Steps

```bash
# Login to Railway
railway login

# Link to your project
railway link

# Set environment variables
railway variables set ANTHROPIC_API_KEY=your-api-key
railway variables set DATABASE_URL=<railway-postgres-url>
railway variables set REDIS_URL=<railway-redis-url>
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false

# Deploy
git push origin main  # Railway auto-deploys on push

# Or deploy manually
railway up
```

### Add Services in Railway Dashboard

1. **PostgreSQL**: Add PostgreSQL plugin
2. **Redis**: Add Redis plugin
3. **API Service**: Deploy from GitHub (uses railway.toml)

The configuration in `railway.toml` will:
- Build and deploy the FastAPI application
- Run database migrations automatically
- Start the API server with 4 workers

### Verify Deployment

```bash
# Get deployment URL
railway status

# Test health endpoint
curl https://your-app.railway.app/

# Test design workflow
curl -X POST https://your-app.railway.app/api/v1/design/start \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple bracket"}'
```

## Architecture Overview

### Multi-Agent System

```
User Request
    ↓
Requirements Agent (Claude)
    ├→ Extracts specifications
    ├→ Asks clarifying questions
    └→ Outputs structured requirements
    ↓
CAD Agent (Claude)
    ├→ Generates CadQuery code
    ├→ Executes code
    ├→ Creates 3D model
    └→ Exports to STL
    ↓
Database Storage
    ├→ Design metadata
    ├→ Design versions
    └→ CAD files
```

### Key Components

1. **Requirements Agent V2** (`requirements_agent_v2.py`)
   - Extracts design specifications
   - Confidence-based clarifications
   - Outputs structured JSON

2. **CAD Agent V2** (`cad_agent_v2.py`)
   - Generates CadQuery Python code
   - Retry logic (max 3 attempts)
   - STL export

3. **Design Orchestrator** (`design_orchestrator.py`)
   - Coordinates workflow
   - Session management
   - Database integration

4. **WebSocket Streaming** (`agent_stream.py`)
   - Real-time updates
   - Agent thinking streams
   - Progress tracking

## API Endpoints

### Design Workflow

- `POST /api/v1/design/start` - Start design session
- `POST /api/v1/design/process` - Process message/clarification
- `GET /api/v1/design/{id}/status` - Get session status
- `GET /api/v1/design/{id}/download` - Download STL file
- `WebSocket /api/v1/design/ws/{id}` - Real-time updates

### Other Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Verify CadQuery
python -c "import cadquery; print(cadquery.__version__)"
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql $DATABASE_URL -c "SELECT version();"
```

### Redis Connection Issues

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli -h localhost -p 6379 ping
# Should return: PONG
```

### API Key Issues

```bash
# Verify API key is set
grep ANTHROPIC_API_KEY .env

# Test with curl
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-5-20250929","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

### Design Generation Failures

Check logs for errors:
```bash
# View server logs
tail -f /var/log/theo-cad/app.log

# Check specific session
curl http://localhost:8000/api/v1/design/$SESSION_ID/status
```

Common issues:
- Invalid requirements (too vague)
- Complex geometry exceeding model limits
- CadQuery syntax errors (retry logic handles this)

## Performance

### Expected Timing

- Simple designs (cube, box): **15-30 seconds**
- Medium designs (phone stand, bracket): **30-60 seconds**
- Complex designs (gear, mechanism): **60-120 seconds**

### Optimization Tips

1. **Be specific in prompts** - Reduces clarification rounds
2. **Provide dimensions upfront** - Faster requirements extraction
3. **Use caching** - Redis caches agent responses
4. **Scale workers** - Add more uvicorn workers for concurrency

## Support

- Documentation: `/docs/DESIGN_WORKFLOW.md`
- API Docs: `http://localhost:8000/docs`
- Issues: GitHub Issues
- Logs: Check `structlog` JSON output

## Next Steps

1. ✅ Complete local setup
2. ✅ Run tests successfully
3. ✅ Test simple designs
4. ✅ Deploy to Railway
5. 📝 Build frontend (React/Next.js)
6. 📝 Add user authentication
7. 📝 Implement design history UI
8. 📝 Add slicing integration (G-code generation)

---

**Theo CAD** - Intelligent CAD platform powered by Claude Sonnet 4.5
