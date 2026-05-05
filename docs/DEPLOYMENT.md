# Deployment Guide

## Development Setup

### Prerequisites
- Python 3.10+
- Conda or venv
- Git

### Local Development
```bash
# Clone repository
git clone <repo-url>
cd sas-rag-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize vector database
python -m src.cli.cli ingest

# Run tests
pytest tests/ -v

# Run API
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Or run Streamlit
streamlit run src/web/streamlit_app.py
```

## Docker Deployment

### Build Image
```bash
docker build -t sas-rag-assistant:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ENVIRONMENT=production \
  sas-rag-assistant:latest
```

### Docker Compose
```bash
docker-compose up -d
```

## Production Deployment

### Environment Variables
Set in production:
```
ENVIRONMENT=production
DEBUG=false
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Security Considerations

1. **API Authentication**
   ```python
   # Add in src/api/app.py
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **Rate Limiting**
   ```bash
   pip install slowapi
   ```

3. **CORS Configuration**
   - Restrict `allow_origins` to specific domains
   - Disable in production if internal only

4. **Data Privacy**
   - Keep .env files secure
   - Don't commit credentials
   - Use secrets management (AWS Secrets, Vault, etc.)

### Scaling Strategies

1. **Vector Database**
   - **Local (development)**: ChromaDB
   - **Production**: Migrate to Pinecone or Weaviate

2. **API Server**
   - Use Gunicorn for production WSGI
   - Run behind Nginx reverse proxy
   - Load balance multiple workers

3. **LLM Calls**
   - Implement request caching
   - Use async/await for concurrency
   - Add retry logic with exponential backoff

### Deployment Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure secrets management
- [ ] Set up logging to file/cloud
- [ ] Configure database backups
- [ ] Add monitoring/alerting
- [ ] Set up CI/CD pipeline
- [ ] Performance testing
- [ ] Security audit
- [ ] Documentation updated

### Example: AWS Deployment

```bash
# 1. Build and push image
docker build -t sas-rag-assistant:latest .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag sas-rag-assistant:latest <account>.dkr.ecr.us-east-1.amazonaws.com/sas-rag-assistant:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/sas-rag-assistant:latest

# 2. Deploy to ECS/Fargate
# Create task definition and service

# 3. Set up CloudFront/ALB for API
# Configure load balancer and auto-scaling

# 4. Monitor with CloudWatch
```

### Example: GCP Deployment

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/<project>/sas-rag-assistant

# Deploy to Cloud Run
gcloud run deploy sas-rag-assistant \
  --image gcr.io/<project>/sas-rag-assistant \
  --platform managed \
  --region us-central1 \
  --set-env-vars ENVIRONMENT=production
```

## Monitoring

### Key Metrics
- API response time
- Vector DB query latency
- LLM API calls/costs
- Error rate
- Corpus size

### Logging
```python
# Logs stored in ./logs/app.log
# Configure cloudwatch/ELK for production
```

## Backup & Recovery

### Vector Database
```bash
# Backup ChromaDB
cp -r ./data/vector_db ./backups/vector_db_$(date +%Y%m%d)

# Restore
cp -r ./backups/vector_db_YYYYMMDD ./data/vector_db
```

### Configuration
- Version control all code
- Document environment variables
- Keep .env backups separately secured

## CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: docker build -t image:latest .
      - run: docker push image:latest
```

## Support & Troubleshooting

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.
See [API_DOCS.md](API_DOCS.md) for API reference.
