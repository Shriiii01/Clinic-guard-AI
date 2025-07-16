# Deployment Guide

This guide covers deploying ClinicGuard-AI in various environments, from local development to production.

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/Shriiii01/Clinic-guard-AI.git
cd Clinic-guard-AI

# Set up environment
cp env.example .env
# Edit .env with your credentials

# Install dependencies
pip install -r server/requirements.txt

# Start the server
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker Deployment

### Development with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production with Docker Compose
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale clinicguard=3
```

### Custom Docker Build
```bash
# Build the image
docker build -f server/Dockerfile -t clinicguard-ai .

# Run the container
docker run -p 8000:8000 --env-file .env clinicguard-ai
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name clinicguard-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service --cluster clinicguard-cluster --service-name clinicguard-service --task-definition clinicguard:1
```

#### Using AWS Lambda (Serverless)
```bash
# Package the application
pip install -r server/requirements.txt -t package/
cp -r server/* package/

# Create deployment package
cd package && zip -r ../clinicguard-lambda.zip .

# Deploy to Lambda
aws lambda create-function \
  --function-name clinicguard-ai \
  --runtime python3.9 \
  --handler server.main.handler \
  --zip-file fileb://clinicguard-lambda.zip
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/clinicguard-ai

# Deploy to Cloud Run
gcloud run deploy clinicguard-ai \
  --image gcr.io/PROJECT_ID/clinicguard-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Using App Engine
```bash
# Deploy to App Engine
gcloud app deploy app.yaml
```

### Azure Deployment

#### Using Azure Container Instances
```bash
# Create container group
az container create \
  --resource-group myResourceGroup \
  --name clinicguard-ai \
  --image clinicguard-ai:latest \
  --ports 8000 \
  --environment-variables \
    TWILIO_ACCOUNT_SID=your_sid \
    TWILIO_AUTH_TOKEN=your_token
```

#### Using Azure App Service
```bash
# Create web app
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name clinicguard-ai \
  --deployment-local-git

# Deploy from local git
az webapp deployment source config-local-git \
  --resource-group myResourceGroup \
  --name clinicguard-ai
```

## 🏗️ Kubernetes Deployment

### Basic Kubernetes Deployment
```yaml
# clinicguard-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clinicguard-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: clinicguard-ai
  template:
    metadata:
      labels:
        app: clinicguard-ai
    spec:
      containers:
      - name: clinicguard-ai
        image: clinicguard-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: TWILIO_ACCOUNT_SID
          valueFrom:
            secretKeyRef:
              name: clinicguard-secrets
              key: twilio-account-sid
        - name: TWILIO_AUTH_TOKEN
          valueFrom:
            secretKeyRef:
              name: clinicguard-secrets
              key: twilio-auth-token
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### Apply the deployment
```bash
# Create namespace
kubectl create namespace clinicguard

# Apply deployment
kubectl apply -f clinicguard-deployment.yaml

# Create service
kubectl apply -f clinicguard-service.yaml

# Create ingress
kubectl apply -f clinicguard-ingress.yaml
```

## 🔧 Environment Configuration

### Production Environment Variables
```env
# Required
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
ELEVENLABS_API_KEY=your_api_key
ELEVENLABS_VOICE_ID=your_voice_id
PUBLIC_URL=https://your-domain.com

# Database (Production)
DATABASE_URL=postgresql://user:password@host:port/db

# Security
SECRET_KEY=your_secure_secret_key
ENVIRONMENT=production
LOG_LEVEL=INFO

# Optional
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### SSL/TLS Configuration
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure Nginx with SSL
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring and Logging

### Health Checks
```bash
# Check application health
curl https://your-domain.com/health

# Check Twilio webhook
curl -X POST https://your-domain.com/twilio/voice \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=test&From=+1234567890"
```

### Logging Configuration
```python
# In your application
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clinicguard.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring with Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'clinicguard-ai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## 🔒 Security Considerations

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Implement rate limiting
- Use VPN for internal communications

### Data Security
- Encrypt data at rest and in transit
- Use secure secrets management
- Implement proper access controls
- Regular security audits

### HIPAA Compliance
- Audit logging for all access
- Data encryption
- Access controls
- Regular compliance reviews

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs clinicguard

# Check environment variables
docker-compose exec clinicguard env | grep TWILIO

# Check port availability
netstat -tulpn | grep 8000
```

#### Twilio Webhook Issues
```bash
# Test webhook locally
ngrok http 8000

# Update Twilio webhook URL
# Go to Twilio Console > Phone Numbers > Your Number > Voice Configuration
```

#### Database Connection Issues
```bash
# Test database connection
python -c "from server.db import engine; print(engine.execute('SELECT 1').scalar())"

# Check database logs
docker-compose logs postgres
```

### Performance Optimization
```bash
# Monitor resource usage
docker stats

# Scale services
docker-compose up -d --scale clinicguard=3

# Optimize AI model loading
# Use model caching and lazy loading
```

## 📞 Support

For deployment issues:
- Check the [GitHub Issues](https://github.com/Shriiii01/Clinic-guard-AI/issues)
- Review the [Documentation](https://github.com/Shriiii01/Clinic-guard-AI/wiki)
- Contact the development team

---

**Note**: Always test deployments in a staging environment before going to production. 