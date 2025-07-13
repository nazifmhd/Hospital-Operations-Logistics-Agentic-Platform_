# Deployment Guide - Hospital Operations Platform

## Overview
This guide provides comprehensive instructions for deploying the Hospital Operations & Logistics Platform in various environments, from development to production.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), Windows 10+, or macOS 10.15+
- **RAM**: Minimum 8GB (16GB recommended for production)
- **Storage**: Minimum 20GB free space
- **Network**: Stable internet connection for package downloads

### Required Software
- **Docker**: Version 20.10+ and Docker Compose
- **Node.js**: Version 16+ (for local development)
- **Python**: Version 3.9+ (for local development)
- **Git**: For source code management

## 🚀 Quick Start Deployment

### Using Docker Compose (Recommended)

1. **Clone the Repository**
```powershell
git clone https://github.com/nazifmhd/Hospital-Operations-Logistics-Agentic-Platform_.git
cd Hospital-Operations-Logistics-Agentic-Platform_
```

2. **Start the Application**
```powershell
docker-compose up -d
```

3. **Verify Deployment**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- Health Check: http://localhost:8001/health

### Manual Installation

#### Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the backend server
cd api
python main.py
```

#### Frontend Setup
```powershell
# Navigate to frontend directory
cd dashboard

# Install dependencies
npm install

# Start the development server
npm start
```

## 🐳 Docker Deployment

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8001
    depends_on:
      - backend
    networks:
      - hospital-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - PYTHONPATH=/app
      - DEBUG=false
    networks:
      - hospital-network
    volumes:
      - ./backend/data:/app/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - hospital-network

networks:
  hospital-network:
    driver: bridge
```

### Building Custom Images
```powershell
# Build frontend image
docker build -t hospital-frontend ./dashboard

# Build backend image
docker build -t hospital-backend ./backend

# Run with custom images
docker-compose -f docker-compose.custom.yml up -d
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name hospital-operations
```

2. **Push Images to ECR**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name hospital-frontend
aws ecr create-repository --repository-name hospital-backend

# Build and push images
docker build -t hospital-frontend ./dashboard
docker tag hospital-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/hospital-frontend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/hospital-frontend:latest
```

3. **Create Task Definition**
```json
{
  "family": "hospital-operations",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/hospital-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ]
    },
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/hospital-backend:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

#### Using AWS Lambda (Serverless Backend)
```python
# lambda_handler.py
from mangum import Mangum
from api.main import app

handler = Mangum(app)
```

### Azure Deployment

#### Using Azure Container Instances
```bash
# Create resource group
az group create --name hospital-operations --location eastus

# Deploy container group
az container create \
  --resource-group hospital-operations \
  --name hospital-app \
  --image hospital-frontend:latest \
  --dns-name-label hospital-ops \
  --ports 3000 8001
```

### Google Cloud Platform

#### Using Google Cloud Run
```bash
# Deploy frontend
gcloud run deploy hospital-frontend \
  --image gcr.io/PROJECT-ID/hospital-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy backend
gcloud run deploy hospital-backend \
  --image gcr.io/PROJECT-ID/hospital-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔧 Environment Configuration

### Environment Variables

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8001
REACT_APP_WS_URL=ws://localhost:8001/ws
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
REACT_APP_ENABLE_ANALYTICS=true
```

#### Backend (.env)
```env
# API Configuration
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8001
API_VERSION=v1

# Database Configuration (if using external DB)
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_ops
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# External Services
EMAIL_SERVER=smtp.hospital.com
EMAIL_PORT=587
EMAIL_USERNAME=notifications@hospital.com
EMAIL_PASSWORD=your-email-password

# Compliance
HIPAA_LOGGING=true
AUDIT_TRAIL=true
ENCRYPTION_KEY=your-encryption-key
```

### Production Configuration

#### Security Settings
```env
# Production Security
HTTPS_ONLY=true
SECURE_COOKIES=true
CORS_ORIGINS=https://hospital-ops.com
SSL_CERT_PATH=/etc/ssl/certs/hospital.crt
SSL_KEY_PATH=/etc/ssl/private/hospital.key

# Database
DATABASE_URL=postgresql://prod_user:secure_password@db.hospital.com:5432/hospital_ops
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

## 🔒 SSL/TLS Configuration

### Nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name hospital-ops.com;

    ssl_certificate /etc/ssl/certs/hospital.crt;
    ssl_certificate_key /etc/ssl/private/hospital.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://backend:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://backend:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Database Setup

### PostgreSQL (Production)
```sql
-- Create database and user
CREATE DATABASE hospital_ops;
CREATE USER hospital_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE hospital_ops TO hospital_user;

-- Connect to database and create schema
\c hospital_ops

-- Create tables (run migration scripts)
\i migrations/001_initial_schema.sql
\i migrations/002_seed_data.sql
```

### Database Migration Script
```python
# migrations/migrate.py
import asyncpg
import asyncio

async def run_migrations():
    conn = await asyncpg.connect(
        user='hospital_user',
        password='secure_password',
        database='hospital_ops',
        host='localhost'
    )
    
    # Run migration files
    with open('001_initial_schema.sql', 'r') as f:
        await conn.execute(f.read())
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migrations())
```

## 🔍 Monitoring Setup

### Application Monitoring
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

  alertmanager:
    image: prom/alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  grafana-storage:
```

### Health Check Endpoints
```python
# Backend health checks
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development")
    }

@app.get("/health/detailed")
async def detailed_health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "external_apis": await check_external_apis()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow()
    }
```

## 🚦 Load Balancing

### Nginx Load Balancer Configuration
```nginx
upstream frontend_servers {
    server frontend1:3000;
    server frontend2:3000;
    server frontend3:3000;
}

upstream backend_servers {
    server backend1:8001;
    server backend2:8001;
    server backend3:8001;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://frontend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Hospital Operations Platform

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          cd dashboard && npm ci
          cd ../backend && pip install -r requirements.txt
          
      - name: Run tests
        run: |
          cd dashboard && npm test
          cd ../backend && python -m pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          # Add deployment commands here
          echo "Deploying to production..."
```

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```powershell
# Windows - Find and kill process using port
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

#### Docker Issues
```powershell
# Reset Docker
docker system prune -a
docker-compose down -v
docker-compose up --build

# Check logs
docker-compose logs frontend
docker-compose logs backend
```

#### Database Connection Issues
```python
# Test database connection
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT 1")
        print(f"Database connection successful: {result}")
        await conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
```

### Performance Optimization

#### Frontend Optimization
```javascript
// Code splitting
const Analytics = lazy(() => import('./components/Analytics'));
const Inventory = lazy(() => import('./components/Inventory'));

// Bundle analysis
npm run build -- --analyze
```

#### Backend Optimization
```python
# Database connection pooling
from asyncpg import create_pool

async def create_db_pool():
    return await create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=20,
        command_timeout=60
    )
```

## 📚 Additional Resources

### Documentation Links
- [Docker Documentation](https://docs.docker.com/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)

### Support
- **Technical Issues**: Create GitHub issue
- **Deployment Help**: Contact DevOps team
- **Security Concerns**: security@hospital.com

---

*Last updated: July 13, 2025*
