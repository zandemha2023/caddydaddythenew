# Theo - Production-Grade Agentic CAD Platform

![Theo CAD](https://img.shields.io/badge/Theo-CAD%20Platform-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Claude](https://img.shields.io/badge/Claude-Sonnet%204.5-purple)

Theo is a production-grade agentic CAD platform that converts natural language descriptions into 3D models and manufacturing files for any printer. Built with a multi-agent architecture powered by Anthropic's Claude Sonnet 4.5.

## Features

- **Natural Language to 3D**: Convert text descriptions directly to manufacturable 3D models
- **Multi-Agent Architecture**: Specialized AI agents for analysis, design, validation, and export
- **Real-Time Updates**: WebSocket support for live agent communication
- **Multiple Export Formats**: STL, STEP, OBJ, DXF, G-code, and SVG
- **Production Ready**: Railway-optimized deployment with PostgreSQL and Redis
- **Printer Support**: Optimized outputs for FDM, SLA, SLS, CNC, and laser cutters

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                  (WebSocket + REST API)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼────┐              ┌──────▼──────┐
    │PostgreSQL│              │    Redis    │
    │ Database │              │Cache/Queue  │
    └─────────┘              └──────┬──────┘
                                    │
                              ┌─────▼─────┐
                              │   Celery  │
                              │  Workers  │
                              └─────┬─────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │    Multi-Agent System         │
                    │    (Claude Sonnet 4.5)        │
                    ├───────────────────────────────┤
                    │ • Orchestrator Agent          │
                    │ • Analyzer Agent              │
                    │ • Designer Agent              │
                    │ • Validator Agent             │
                    │ • Exporter Agent              │
                    └───────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Anthropic API Key

### Local Development with Docker

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd theo-cad
   cp .env.example .env
   ```

2. **Configure environment**:
   Edit `.env` and add your Anthropic API key:
   ```bash
   ANTHROPIC_API_KEY=your-api-key-here
   ```

3. **Start services**:
   ```bash
   make build
   make up
   ```

4. **Access the application**:
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Manual Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis**:
   ```bash
   # PostgreSQL
   createdb theo_cad

   # Redis
   redis-server
   ```

3. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start application**:
   ```bash
   # API Server
   uvicorn app.main:app --reload

   # Celery Worker (separate terminal)
   celery -A app.services.queue.celery_app worker --loglevel=info
   ```

## Usage

### API Example: Generate CAD Model

```python
import httpx
import asyncio

async def generate_model():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/cad/generate",
            json={
                "prompt": "Create a mounting bracket 50mm x 30mm with 4 corner holes",
                "export_formats": ["stl", "step"],
                "printer_type": "fdm",
                "parameters": {
                    "hole_diameter": 3.2,
                    "wall_thickness": 2.5
                }
            }
        )
        return response.json()

result = asyncio.run(generate_model())
print(f"Job ID: {result['job_id']}")
```

### WebSocket Example: Real-Time Updates

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent/{job_id}');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log('Agent update:', update);

    if (update.type === 'agent_update') {
        console.log('Progress:', update.data.progress);
    }
};

ws.send(JSON.stringify({type: 'status_request'}));
```

## API Endpoints

### CAD Generation
- `POST /api/v1/cad/generate` - Generate 3D model from prompt
- `GET /api/v1/cad/formats` - List supported export formats

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project details

### Designs
- `POST /api/v1/designs` - Create design
- `GET /api/v1/designs` - List designs
- `GET /api/v1/designs/{id}` - Get design with versions

### Jobs
- `GET /api/v1/jobs` - List jobs
- `GET /api/v1/jobs/{id}` - Get job status
- `DELETE /api/v1/jobs/{id}` - Cancel job

### WebSocket
- `WS /ws/agent/{job_id}` - Real-time agent updates

## Multi-Agent System

Theo uses a sophisticated multi-agent architecture:

1. **Orchestrator Agent**: Coordinates the entire workflow
2. **Analyzer Agent**: Interprets natural language and extracts design parameters
3. **Designer Agent**: Creates parametric CAD code (CadQuery)
4. **Validator Agent**: Checks manufacturability and design quality
5. **Exporter Agent**: Converts to various file formats

Each agent is powered by Claude Sonnet 4.5 with specialized system prompts.

## Deployment

### Railway

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create project**:
   ```bash
   railway init
   ```

3. **Add services**:
   ```bash
   railway add postgresql
   railway add redis
   ```

4. **Set environment variables**:
   ```bash
   railway variables set ANTHROPIC_API_KEY=your-key
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

### Environment Variables

See `.env.example` for all configuration options:

- `ANTHROPIC_API_KEY` - Required: Your Anthropic API key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key (change in production)
- `CORS_ORIGINS` - Allowed CORS origins

## Project Structure

```
theo-cad/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/      # REST API endpoints
│   │   │   └── websockets/     # WebSocket handlers
│   │   ├── core/               # Configuration & security
│   │   ├── db/                 # Database setup
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/
│   │       ├── agents/         # Multi-agent system
│   │       ├── cad/           # CAD generation logic
│   │       └── queue/         # Celery tasks
│   ├── requirements.txt        # Pinned dependencies
│   └── pyproject.toml
├── infrastructure/
├── docs/
├── docker-compose.yml
├── Dockerfile
├── railway.toml
└── README.md
```

## Development

### Run Tests
```bash
make test
```

### View Logs
```bash
make logs          # All services
make logs-api      # API only
make logs-worker   # Worker only
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
make migrate
```

### Code Quality
```bash
# Format code
black backend/

# Type checking
mypy backend/

# Linting
ruff check backend/
```

## Technology Stack

- **Framework**: FastAPI 0.109.2
- **AI/ML**: Anthropic Claude Sonnet 4.5 (anthropic 0.25.1)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Cache/Queue**: Redis + Celery
- **CAD Libraries**: CadQuery, Trimesh, ezdxf
- **Deployment**: Railway, Docker

## Supported Export Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| STL | Binary/ASCII mesh | 3D printing |
| STEP | Parametric CAD | CAD interchange |
| OBJ | 3D mesh with textures | Rendering |
| DXF | 2D/3D vector | Laser cutting |
| G-code | Machine instructions | Direct printing |
| SVG | 2D vector graphics | Profiles |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Email: support@theo-cad.com

## Roadmap

- [ ] Web-based 3D viewer
- [ ] User authentication & teams
- [ ] Design marketplace
- [ ] Advanced slicing integration
- [ ] Multi-material support
- [ ] Cost estimation
- [ ] Assembly instructions generation

---

Built with ❤️ using Claude Sonnet 4.5
