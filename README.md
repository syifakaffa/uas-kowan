# Circle Calculator - Passwordless Authentication

Web application untuk menghitung luas dan keliling lingkaran dengan passwordless authentication menggunakan OTP via email.

## 🚀 Features

- ✅ Passwordless authentication (OTP via email)
- ✅ Session management with Flask
- ✅ Circle area & circumference calculator
- ✅ Responsive UI design
- ✅ Docker containerized
- ✅ Kubernetes ready (kind cluster)
- ✅ Production-grade deployment

## 📋 Prerequisites

- Python 3.11+
- Docker
- kubectl
- kind (Kubernetes in Docker)
- Gmail account with App Password

## 🏃 Quick Start - Local Development

```bash
# 1. Clone repository
git clone https://github.com/syifakaffa/uas-kowan.git
cd uas-kowan

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env dengan email credentials kamu

# 4. Run application
python app.py

# 5. Open browser
# http://localhost:5000
```

## 🔐 Environment Variables

Create `.env` file:

```env
SECRET_KEY=your-random-secret-key-here
SMTP_EMAIL=syifakaffabillah@gmail.com
SMTP_PASSWORD=your-app-password
```

### Gmail App Password Setup:

1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Select "Mail" application
4. Copy 16-character password (remove spaces)
5. Paste to `SMTP_PASSWORD` in `.env`

## 🐳 Docker Deployment (Standalone)

```bash
# Build image
docker build -t circle-calculator:latest .

# Run container
docker run -d -p 80:5000 \
  --name circle-calc \
  -e SECRET_KEY="suPersecreTrandomMakeItLong12353" \
  -e SMTP_EMAIL="syifakaffabillah@gmail.com" \
  -e SMTP_PASSWORD="mugg dsve rhee lyyn" \
  circle-calculator:latest

# Access: http://localhost
```

## ☸️ Kubernetes Deployment with kind (Recommended)

### Step 1: Install Tools

```bash
# Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install kind
curl -Lo kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x kind
sudo mv kind /usr/local/bin/

# Verify installations
docker --version
kubectl version --client
kind version
```

### Step 2: Create kind Cluster Configuration

```bash
# Create kind-config.yaml
cat > kind-config.yaml << 'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  # Control plane node
  - role: control-plane
    extraPortMappings:
      # Expose NodePort 30080 to host
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP
  
  # Worker node 1
  - role: worker
  
  # Worker node 2
  - role: worker
EOF
```

### Step 3: Create Kubernetes Cluster

```bash
# Create cluster (wait 2-3 minutes)
kind create cluster --name circle-calculator --config kind-config.yaml

# Verify cluster
kubectl get nodes
# Should show 3 nodes: 1 control-plane + 2 workers

# Check cluster info
kubectl cluster-info
```

### Step 4: Build and Load Docker Image

```bash
# Build Docker image
docker build -t circle-calculator:latest .

# Load image to kind cluster
kind load docker-image circle-calculator:latest --name circle-calculator

# Verify image loaded
docker exec -it circle-calculator-control-plane crictl images | grep circle-calculator
```

### Step 5: Create Kubernetes Secret

```bash
# Create secret for email credentials
kubectl create secret generic email-secret \
  --from-literal=secret-key="suPersecreTrandomMakeItLong12353" \
  --from-literal=smtp-email="syifakaffabillah@gmail.com" \
  --from-literal=smtp-password="mugg dsve rhee lyyn"

# Verify secret
kubectl get secrets
kubectl describe secret email-secret
```

### Step 6: Update Deployment YAML

Update `k8s/deployment.yaml` to use Kubernetes Secret:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: circle-calculator
  labels:
    app: circle-calculator
spec:
  replicas: 1  # Single replica to avoid OTP session issues
  selector:
    matchLabels:
      app: circle-calculator
  template:
    metadata:
      labels:
        app: circle-calculator
    spec:
      containers:
      - name: circle-calculator
        image: circle-calculator:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
          name: http
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: email-secret
              key: secret-key
        - name: SMTP_EMAIL
          valueFrom:
            secretKeyRef:
              name: email-secret
              key: smtp-email
        - name: SMTP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: email-secret
              key: smtp-password
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Step 7: Deploy to Kubernetes

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Apply service (NodePort 30080)
kubectl apply -f k8s/service.yaml

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods -l app=circle-calculator --timeout=300s

# Verify deployment
kubectl get all
```

### Step 8: Access Application

```bash
# Check service
kubectl get services

# Access via NodePort
# Local: http://localhost:30080
# EC2: http://YOUR_EC2_PUBLIC_IP:30080
```

## 📊 Kubernetes Management Commands

```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes

# Check all resources
kubectl get all

# Check pods
kubectl get pods
kubectl get pods -o wide

# Check services
kubectl get services

# Check deployments
kubectl get deployments

# View logs
kubectl logs -l app=circle-calculator
kubectl logs -l app=circle-calculator --tail=100 -f

# Describe resources
kubectl describe deployment circle-calculator
kubectl describe service circle-calculator-service
kubectl describe pod <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Scale deployment
kubectl scale deployment circle-calculator --replicas=3

# Restart deployment
kubectl rollout restart deployment circle-calculator

# Check rollout status
kubectl rollout status deployment circle-calculator

# Delete resources
kubectl delete -f k8s/
```

## 🔧 Troubleshooting

### OTP Expired Issue

**Problem:** OTP says expired when multiple replicas running.

**Solution:** Set replicas to 1 in deployment.yaml:

```bash
kubectl scale deployment circle-calculator --replicas=1
```

### Email Not Sending

**Check logs:**
```bash
kubectl logs -l app=circle-calculator --tail=50
```

**Verify secret:**
```bash
kubectl get secret email-secret -o jsonpath='{.data.smtp-email}' | base64 -d
echo ""
kubectl get secret email-secret -o jsonpath='{.data.smtp-password}' | base64 -d
```

**Check env in pod:**
```bash
POD_NAME=$(kubectl get pods -l app=circle-calculator -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -- env | grep SMTP
```

### Pod Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name>
```

### Image Pull Issues

```bash
# Rebuild and reload image
docker build -t circle-calculator:latest .
kind load docker-image circle-calculator:latest --name circle-calculator

# Restart deployment
kubectl rollout restart deployment circle-calculator
```

## 🗑️ Cleanup

```bash
# Delete Kubernetes resources
kubectl delete -f k8s/

# Delete secret
kubectl delete secret email-secret

# Delete kind cluster
kind delete cluster --name circle-calculator

# Remove Docker image
docker rmi circle-calculator:latest
```

## 🌐 AWS EC2 Deployment

### Instance Requirements

- **Instance Type:** t2.medium (recommended) or t2.micro
- **OS:** Ubuntu 22.04 LTS
- **Storage:** 20 GB minimum
- **Security Group:**
  - Port 22 (SSH) - Your IP only
  - Port 30080 (NodePort) - 0.0.0.0/0
  - Port 80 (HTTP) - 0.0.0.0/0 (optional)

### Complete Deployment Script

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install kind
curl -Lo kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x kind
sudo mv kind /usr/local/bin/

# Clone repository
git clone https://github.com/syifakaffa/uas-kowan.git
cd uas-kowan

# Create kind cluster
kind create cluster --name circle-calculator --config kind-config.yaml

# Build and load image
docker build -t circle-calculator:latest .
kind load docker-image circle-calculator:latest --name circle-calculator

# Create secret (update with your credentials)
kubectl create secret generic email-secret \
  --from-literal=secret-key="suPersecreTrandomMakeItLong12353" \
  --from-literal=smtp-email="syifakaffabillah@gmail.com" \
  --from-literal=smtp-password="mugg dsve rhee lyyn"

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Wait for pods
kubectl wait --for=condition=Ready pods -l app=circle-calculator --timeout=300s

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Show access URL
echo "Application URL: http://$PUBLIC_IP:30080"
```

### Security Group Configuration

Add inbound rules in AWS Console:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| Custom TCP | TCP | 30080 | 0.0.0.0/0 | Kubernetes NodePort |
| HTTP | TCP | 80 | 0.0.0.0/0 | Optional HTTP |

## 📸 Screenshots for Documentation

Recommended screenshots for UAS report:

1. **kubectl cluster-info** - Show cluster running
2. **kubectl get nodes** - Show 3 nodes (1 control + 2 workers)
3. **kubectl get all** - Show all resources
4. **kubectl get pods -o wide** - Show pods distribution
5. **kubectl get services** - Show NodePort service
6. **kubectl describe deployment** - Show deployment details
7. **kubectl logs <pod>** - Show application logs
8. **kubectl get secrets** - Show secret created
9. **Browser - Login page** - http://EC2_IP:30080
10. **Browser - Calculator working** - After OTP verification

## 📚 Tech Stack

- **Backend:** Flask (Python 3.11)
- **Frontend:** HTML5, CSS3
- **Email:** SMTP (Gmail)
- **Container:** Docker
- **Orchestration:** Kubernetes (kind)
- **Deployment:** AWS EC2 (Ubuntu 22.04)

## 🎓 Project Information

- **Course:** Komputasi Awan (Cloud Computing)
- **Assignment:** UAS (Final Exam)
- **Institution:** Universitas Indonesia
- **Author:** Syifa Kaffa Billah
- **Email:** syifakaffabillah@gmail.com

## 📄 License

MIT License

---

**Note:** For production deployment, use managed Kubernetes (EKS, GKE, AKS) instead of kind, and store secrets in proper secret management systems (AWS Secrets Manager, HashiCorp Vault, etc).