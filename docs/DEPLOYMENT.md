# Deployment Guide

## Railway Deployment

### Prerequisites
- Railway account (https://railway.app)
- Anthropic API key
- Git repository

### Step-by-Step Deployment

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize Project**:
   ```bash
   cd theo-cad
   railway init
   ```

3. **Add PostgreSQL**:
   ```bash
   railway add
   # Select PostgreSQL from the list
   ```

4. **Add Redis**:
   ```bash
   railway add
   # Select Redis from the list
   ```

5. **Set Environment Variables**:
   ```bash
   railway variables set ANTHROPIC_API_KEY=your-api-key-here
   railway variables set SECRET_KEY=$(openssl rand -hex 32)
   railway variables set ENVIRONMENT=production
   railway variables set LOG_LEVEL=INFO
   ```

6. **Deploy**:
   ```bash
   railway up
   ```

7. **Get Deployment URL**:
   ```bash
   railway domain
   ```

### Railway Configuration Files

The project includes:
- `railway.json` - Build and deploy configuration
- `railway.toml` - Multi-service configuration
- `Procfile` - Process definitions

### Environment Variables on Railway

Set these in Railway dashboard or CLI:

```bash
# Required
ANTHROPIC_API_KEY=your-anthropic-api-key

# Auto-configured by Railway
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Optional (Railway sets PORT automatically)
PORT=8000
SECRET_KEY=auto-generated-or-custom
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

---

## Docker Deployment

### Production Docker Build

1. **Build Image**:
   ```bash
   docker build -t theo-cad:latest .
   ```

2. **Run Container**:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e DATABASE_URL=postgresql://... \
     -e REDIS_URL=redis://... \
     -e ANTHROPIC_API_KEY=your-key \
     --name theo-cad \
     theo-cad:latest
   ```

### Docker Compose (Production)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: theo-cad:latest
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 2G

  worker:
    image: theo-cad:latest
    command: celery -A app.services.queue.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    restart: always
    deploy:
      replicas: 4
```

---

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: theo-cad-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: theo-cad-api
  template:
    metadata:
      labels:
        app: theo-cad-api
    spec:
      containers:
      - name: api
        image: theo-cad:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: theo-secrets
              key: database-url
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: theo-secrets
              key: anthropic-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: theo-cad-service
spec:
  selector:
    app: theo-cad-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## AWS Deployment

### ECS with Fargate

1. **Build and Push to ECR**:
   ```bash
   aws ecr create-repository --repository-name theo-cad
   docker tag theo-cad:latest <account-id>.dkr.ecr.<region>.amazonaws.com/theo-cad:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/theo-cad:latest
   ```

2. **Create Task Definition** (JSON):
   ```json
   {
     "family": "theo-cad",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "theo-cad",
         "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/theo-cad:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "ENVIRONMENT", "value": "production"}
         ],
         "secrets": [
           {
             "name": "ANTHROPIC_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:..."
           }
         ]
       }
     ]
   }
   ```

---

## Database Migrations

### Alembic Setup

1. **Initialize Alembic** (if not done):
   ```bash
   cd backend
   alembic init alembic
   ```

2. **Configure** `alembic.ini`:
   ```ini
   sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/theo_cad
   ```

3. **Create Migration**:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   ```

4. **Apply Migration**:
   ```bash
   alembic upgrade head
   ```

### Migration in Production

```bash
# On Railway
railway run alembic upgrade head

# With Docker
docker-compose exec api alembic upgrade head

# Direct
ANTHROPIC_API_KEY=xxx DATABASE_URL=xxx alembic upgrade head
```

---

## Monitoring

### Health Checks

- Basic: `GET /health`
- Detailed: `GET /health/detailed`

### Logging

Structured JSON logging to stdout. Configure log aggregation:

**CloudWatch (AWS)**:
```bash
aws logs create-log-group --log-group-name /theo-cad/api
```

**Datadog**:
```bash
DD_API_KEY=xxx DD_SITE=datadoghq.com docker run ...
```

### Metrics

Monitor these key metrics:
- API response times
- Job queue length
- Agent processing time
- Database connection pool
- Redis memory usage
- Anthropic API usage

---

## Scaling

### Horizontal Scaling

**API Workers**:
```bash
# Railway
railway scale api=5

# Docker Compose
docker-compose up --scale api=5

# Kubernetes
kubectl scale deployment theo-cad-api --replicas=5
```

**Celery Workers**:
```bash
# Railway
railway scale worker=10

# Docker
docker-compose up --scale worker=10
```

### Vertical Scaling

Increase resources per container:
- CPU: 1-2 cores per API worker
- Memory: 2-4GB per API worker
- Celery workers: 2-4GB each

---

## Security

### Environment Variables

Never commit:
- `ANTHROPIC_API_KEY`
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`

Use secret management:
- Railway: Built-in secrets
- AWS: Secrets Manager
- Kubernetes: Secrets

### HTTPS

Use reverse proxy:
- Railway: Automatic HTTPS
- Custom: Nginx/Traefik/Caddy

```nginx
server {
    listen 443 ssl;
    server_name theo-cad.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Backup

### Database Backups

**Automated (Railway)**:
- Automatic daily backups
- Point-in-time recovery

**Manual**:
```bash
pg_dump -h host -U user -d theo_cad > backup.sql
```

### File Storage

Consider using S3/Cloud Storage for uploads/outputs:
```python
# Update settings
UPLOAD_DIR = "s3://bucket/uploads"
OUTPUT_DIR = "s3://bucket/outputs"
```

---

## Troubleshooting

### Common Issues

**Connection Errors**:
```bash
# Check services
railway status
docker-compose ps

# View logs
railway logs
docker-compose logs
```

**Database Issues**:
```bash
# Check connection
psql $DATABASE_URL -c "SELECT 1"

# Reset database (dev only!)
alembic downgrade base
alembic upgrade head
```

**Redis Issues**:
```bash
# Check Redis
redis-cli -u $REDIS_URL ping

# Clear cache
redis-cli -u $REDIS_URL FLUSHDB
```

### Performance Tuning

1. **Database Connection Pool**:
   ```python
   DATABASE_POOL_SIZE = 20
   DATABASE_MAX_OVERFLOW = 10
   ```

2. **Redis Connection Pool**:
   ```python
   REDIS_MAX_CONNECTIONS = 50
   ```

3. **Celery Concurrency**:
   ```bash
   celery -A app.services.queue.celery_app worker --concurrency=8
   ```

---

## Cost Optimization

### Anthropic API

Monitor token usage:
- Analyzer: ~1K-2K tokens
- Designer: ~2K-4K tokens
- Validator: ~1K-2K tokens
- Exporter: ~1K tokens

Estimated cost per generation: $0.10-$0.30

### Infrastructure

Railway estimate (monthly):
- Starter: $5-10
- Hobby: $20-50
- Pro: $100-200

Consider:
- Caching to reduce API calls
- Batch processing
- Auto-scaling based on demand
