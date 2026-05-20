# Setup & Deployment Guide

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key or Google Gemini API key
- 2GB available disk space

### Steps

```bash
# 1. Navigate to app directory
cd app

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env and add API key
# On macOS/Linux:
nano .env
# Add OPENAI_API_KEY or GEMINI_API_KEY

# 4. Start services
docker-compose up -d

# 5. Wait for startup (20-30 seconds)
docker-compose logs -f app

# 6. Access applications
# - Streamlit: http://localhost:8501
# - FastAPI: http://localhost:8000/docs
# - API: http://localhost:8000
```

---

## 🔧 Local Development Setup

### Requirements
- Python 3.11+
- PostgreSQL 14+ (local install)
- pip or conda

### Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env with your settings

# 4. Start PostgreSQL (if not containerized)
# macOS:
brew services start postgresql
# Ubuntu/Debian:
sudo service postgresql start

# 5. Initialize database
python -c "from db import init_db; init_db()"

# 6. Run Streamlit (in one terminal)
streamlit run streamlit_app.py

# 7. Run FastAPI (in another terminal)
python main.py
```

### Verify Installation

```bash
# Check imports work
python -c "from graph.workflow import Text2SQLWorkflow; print('✓ Setup OK')"

# Check database connection
python -c "from db import get_db_session; db = get_db_session(); print('✓ DB Connected')"

# Check LLM configuration
python -c "from agents.llm import get_llm; llm = get_llm(); print('✓ LLM Ready')"
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

#### Basic Setup
```bash
docker-compose up -d
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
```

#### Check Status
```bash
docker-compose ps
```

#### Stop Services
```bash
docker-compose down
```

#### Stop and Remove Data
```bash
docker-compose down -v
```

### Using Docker Only (Without Compose)

```bash
# Build image
docker build -t text2sql-agent:latest .

# Run app container
docker run -p 8000:8000 -p 8501:8501 \
  -e DATABASE_URL="postgresql://user:password@host:5432/db" \
  -e OPENAI_API_KEY="your-key" \
  text2sql-agent:latest

# Run PostgreSQL container separately
docker run -p 5432:5432 \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=text2sql_db \
  postgres:15-alpine
```

---

## ☁️ Cloud Deployment

### AWS EC2 Deployment

```bash
# 1. SSH into EC2 instance
ssh -i key.pem ubuntu@your-instance-ip

# 2. Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 3. Add user to docker group
sudo usermod -aG docker $USER

# 4. Clone/upload code
git clone <repo> text2sql-agent
cd text2sql-agent/app

# 5. Setup environment
cp .env.example .env
# Edit .env with production values

# 6. Start services
docker-compose up -d

# 7. Setup reverse proxy (nginx)
# See nginx.conf example below
```

### AWS ECS Deployment

```bash
# Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag text2sql-agent:latest <account>.dkr.ecr.us-east-1.amazonaws.com/text2sql-agent:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/text2sql-agent:latest

# Create ECS task definition and service using AWS Console or CLI
```

### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/text2sql-agent

# Deploy to Cloud Run
gcloud run deploy text2sql-agent \
  --image gcr.io/PROJECT_ID/text2sql-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key,DATABASE_URL=your-db-url
```

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create text2sql-agent

# Add buildpacks
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## 🔐 Production Configuration

### Environment Variables - Production

```env
# Database
DATABASE_URL=postgresql://prod_user:strong_password@db-host:5432/text2sql_prod

# LLM
OPENAI_API_KEY=sk-prod-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# Security
DEBUG=False
LOG_LEVEL=INFO

# Performance
POOL_SIZE=20
MAX_OVERFLOW=40
```

### Database Configuration - Production

```sql
-- Create read-only database user
CREATE USER text2sql_readonly WITH PASSWORD 'strong_password';

-- Grant permissions
GRANT CONNECT ON DATABASE text2sql_db TO text2sql_readonly;
GRANT USAGE ON SCHEMA public TO text2sql_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text2sql_readonly;

-- Make default for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO text2sql_readonly;
```

### Nginx Reverse Proxy

```nginx
upstream streamlit {
    server localhost:8501;
}

upstream fastapi {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # FastAPI
    location /api/ {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Streamlit
    location / {
        proxy_pass http://streamlit;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Streamlit WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### SSL/TLS Certificate

```bash
# Using Let's Encrypt (certbot)
sudo apt-get install certbot python3-certbot-nginx

sudo certbot certonly --nginx -d api.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## 📊 Monitoring & Logging

### Logs in Docker

```bash
# Real-time logs
docker-compose logs -f

# Filter by service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail 100 app

# Timestamp format
docker-compose logs --timestamps app
```

### Log Aggregation (ELK Stack)

```bash
# Add to docker-compose.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"

# Access Kibana at http://localhost:5601
```

### Monitoring Queries

```bash
# Check query success rate
docker-compose exec postgres psql -U user -d text2sql_db -c "
  SELECT COUNT(*) as total_queries FROM query_logs;
"

# Check slow queries
docker-compose exec postgres psql -U user -d text2sql_db -c "
  SELECT query, duration FROM query_logs WHERE duration > 5000 ORDER BY duration DESC;
"
```

---

## 🆘 Troubleshooting

### Docker Issues

**Container exits immediately:**
```bash
docker-compose logs app
# Check for errors, usually missing environment variables
```

**Port already in use:**
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
docker-compose -e "STREAMLIT_PORT=8502" up
```

**Database connection refused:**
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Check network
docker network ls
docker inspect <network_name>
```

### Performance Issues

**Slow queries:**
```sql
-- Enable query logging
SET log_statement = 'all';
SET log_duration = true;

-- Check slow queries
SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

**High memory usage:**
```bash
# Check container memory
docker stats text2sql-app

# Reduce POOL_SIZE in .env
POOL_SIZE=10
```

### API Issues

**502 Bad Gateway (Nginx):**
```bash
# Check if FastAPI is running
curl http://localhost:8000/health

# Check Nginx logs
tail -f /var/log/nginx/error.log
```

**LLM timeout:**
```python
# Increase timeout in agents/llm.py
# Or adjust temperature/max_tokens in config
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose-prod.yml with load balancing
version: "3.8"

services:
  app1:
    build: .
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/db
  
  app2:
    build: .
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/db
  
  app3:
    build: .
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/db
  
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app1
      - app2
      - app3
```

### Database Connection Pooling

```python
# Increase pool size in db.py
engine = create_engine(
    settings.database_url,
    pool_size=20,        # Connections to keep open
    max_overflow=40,     # Extra connections for spikes
    pool_pre_ping=True,  # Test connections before using
)
```

### Caching Layer (Redis)

```python
# Add to requirements.txt
redis==4.5.0

# Use in agents
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Cache query results
cache_key = f"query:{query_hash}"
if r.exists(cache_key):
    return r.get(cache_key)
```

---

## ✅ Pre-Production Checklist

- [ ] Environment variables set correctly
- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Monitoring/alerting setup
- [ ] Log aggregation enabled
- [ ] Rate limiting configured
- [ ] API authentication implemented
- [ ] Database indexed for common queries
- [ ] Connection pool sizes tuned
- [ ] Load testing completed
- [ ] Disaster recovery plan documented
- [ ] Security audit completed
- [ ] API documentation deployed
- [ ] Runbook created for operations
- [ ] On-call rotation established

---

## 🚀 Deployment Command Cheat Sheet

```bash
# Local Development
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Docker Development
docker-compose up -d

# Docker Production
docker build -t text2sql-agent:prod .
docker run -p 80:8501 -p 8000:8000 --env-file .env.prod text2sql-agent:prod

# Stop All
docker-compose down

# View Logs
docker-compose logs -f app

# Rebuild
docker-compose up --build -d

# Scale Services (Docker Swarm)
docker service scale app=3

# Health Check
curl http://localhost:8000/health
```

---

## 📞 Support & Resources

- **Documentation**: See README.md and ARCHITECTURE.md
- **Issues**: Check troubleshooting section above
- **Examples**: Run examples.py for usage patterns
- **Logs**: Use `docker-compose logs` for debugging
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

**Last Updated: May 2026**
