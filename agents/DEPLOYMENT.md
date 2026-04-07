# Deployment Guide for Arch-Sense Coaching System

## Overview

This guide covers deploying the FastAPI + CrewAI coaching server to production or cloud environments.

## Local Development

### Quick Start

```bash
# 1. Setup
python setup.py

# 2. Configure
cp .env.example .env
# Edit .env with your settings

# 3. Run
python main.py
```

Server runs on `http://localhost:8000`

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy files
COPY requirements.txt .
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=sqlite:///./data/arch_sense.db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - COACHING_STYLE=balanced
      - DIFFICULTY_LEVEL=1
      - CORS_ORIGIN=https://yourdomain.com
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. Build and Run

```bash
docker-compose build
docker-compose up -d
```

## Cloud Deployment Options

### Google Cloud Run

```bash
# 1. Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/arch-sense

# 2. Deploy
gcloud run deploy arch-sense \
  --image gcr.io/PROJECT_ID/arch-sense \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=xxx,ENVIRONMENT=production

# Service URL: https://arch-sense-XXXXX.run.app
```

### AWS Lambda + API Gateway

Use AWS SAM or Zappa to deploy ASGI (FastAPI) to Lambda.

```bash
# Install Zappa
pip install zappa

# Initialize
zappa init

# Deploy
zappa deploy production
```

### Heroku

```bash
# 1. Create app
heroku create arch-sense

# 2. Set environment
heroku config:set GEMINI_API_KEY=xxx
heroku config:set ENVIRONMENT=production

# 3. Deploy
git push heroku main
```

## Database Considerations

### Development
- SQLite file-based (./data/arch_sense.db)
- Simple, self-contained
- Good for testing

### Production

#### Option 1: SQLite with Persistent Volume
```yaml
volumes:
  - /persistent-storage:/app/data  # Cloud block storage
```

#### Option 2: PostgreSQL
```python
# config.py
DATABASE_URL = "postgresql://user:pass@host/dbname"
```

```bash
docker-compose up -d postgres
# Then run migrations
```

#### Option 3: Managed Database (Cloud SQL, RDS)
```python
# Use connection string from provider
DATABASE_URL = "postgresql+asyncpg://user:pass@cloudsql/dbname"
```

## Environment Configuration

### Production .env
```bash
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

DATABASE_URL=sqlite:///./data/arch_sense.db  # Or postgres URL

GEMINI_API_KEY=your-prod-key-here
GEMINI_MODEL=gemini-3.1-pro-preview

DIFFICULTY_LEVEL=2
COACHING_STYLE=balanced
ENABLE_HINTS=true

CORS_ORIGIN=https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# Optional: Logging
LOG_LEVEL=INFO
```

## Security Best Practices

1. **API Keys**
   - Store GEMINI_API_KEY in secrets manager (not in .env)
   - Use environment variables or secrets vaults

2. **CORS**
   - Set specific CORS_ORIGIN (not wildcard)
   - Update when frontend domain changes

3. **Database**
   - Use strong passwords for PostgreSQL
   - Enable encryption at rest
   - Regular backups

4. **Server**
   - Use HTTPS only (Let's Encrypt)
   - Set rate limits
   - Monitor logs for errors

5. **Dependencies**
   - Regular `pip update` checks
   - Pin versions in requirements.txt
   - Scan for vulnerabilities

## Monitoring & Logging

### Health Endpoint

```bash
curl https://yourdomain.com/health
```

### Log Files

```bash
# Docker
docker logs arch-sense-api

# File-based (if running locally)
tail -f logs/server.log
```

### Metrics to Monitor
- Active sessions count
- Evaluation/minute
- Average response time
- Error rate
- Database size

## Scaling

### Horizontal Scaling (Multiple Instances)

```yaml
# docker-compose.yml
services:
  api-1:
    # ...
  api-2:
    # ...
  load-balancer:
    image: nginx
    ports:
      - "8000:8000"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Session Persistence

Current implementation uses in-memory _session_agents dict. For multiple instances, migrate to:

1. **Redis** (recommended for per-session state)
   ```python
   import redis
   redis_client = redis.Redis(host='redis', port=6379)
   _session_agents = redis_client  # Store agents as serialized objects
   ```

2. **Database**
   ```python
   # Store agent state in sessions table
   # Re-initialize agents on endpoint call
   ```

3. **Kubernetes Session Affinity**
   ```yaml
   sessionAffinity: ClientIP  # Route to same pod
   ```

## Maintenance

### Database Backups

```bash
# SQLite
cp data/arch_sense.db data/arch_sense.db.backup

# PostgreSQL
pg_dump -U user dbname > backup.sql
```

### Cleanup Old Sessions

```bash
# Clean up sessions older than 30 days
DELETE FROM sessions WHERE created_at < datetime('now', '-30 days');
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

## Testing Before Production

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/health
```

### API Testing

```bash
# Run test suite
python test_api.py

# Or use pytest
pytest tests/ -v
```

## Troubleshooting

### 500 Errors
```bash
# Check logs
docker logs arch-sense-api

# Verify database
sqlite3 data/arch_sense.db ".tables"
```

### Connection Refused
- Ensure port 8000 is open
- Check CORS_ORIGIN matches frontend domain
- Verify firewall rules

### Slow Evaluations
- Check coaching_style (aggressive = slower)
- Verify Gemini API rate limits
- Monitor CPU/memory

### Database Lock
- Kill hanging processes: `sqlite3 data/arch_sense.db "PRAGMA integrity_check;"`
- Use PostgreSQL for production

## Rollback Plan

If deployment fails:

```bash
# Docker rollback
docker-compose down
docker-compose pull  # Get previous image
docker-compose up -d

# Or restore from backup
cp data/arch_sense.db.backup data/arch_sense.db
```

## Production Checklist

- [ ] .env configured with production values
- [ ] GEMINI_API_KEY set in secrets manager
- [ ] Database: PostgreSQL or persistent SQLite
- [ ] CORS_ORIGIN matches frontend domain
- [ ] HTTPS enabled (let's Encrypt)
- [ ] Health endpoint returns 200
- [ ] Load test passed (1000+ req/min)
- [ ] Database backups configured
- [ ] Error logging configured
- [ ] Session cleanup scheduled
- [ ] Dependencies updated
- [ ] API tests pass

---

Deployment complete! 🚀
