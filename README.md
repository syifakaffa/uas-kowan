# Circle Calculator - Passwordless Authentication

Web application untuk menghitung luas dan keliling lingkaran dengan passwordless authentication menggunakan OTP via email.

## Prerequisites

- Python 3.11+
- Docker (optional)
- Kubernetes cluster (optional)

## Quick Start - Local

```bash
# 1. Clone repository
git clone <your-repo-url>
cd uas

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env dengan email credentials

# 4. Run application
python app.py

# 5. Open browser
# http://localhost:5000
```

## Environment Variables

Create `.env` file:

```env
SECRET_KEY=your-random-secret-key-here
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Gmail App Password:**
1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy 16-character password

## Docker Deployment

```bash
# Build image
docker build -t circle-calculator .

# Run container
docker run -d -p 5000:5000 \
  -e SECRET_KEY="your-secret" \
  -e SMTP_EMAIL="your@email.com" \
  -e SMTP_PASSWORD="your-password" \
  circle-calculator
```

## Kubernetes Deployment

```bash
# 1. Create secret for email
kubectl create secret generic email-secret \
  --from-literal=smtp-email=your@email.com \
  --from-literal=smtp-password=your-password

# 2. Deploy application
kubectl apply -f k8s/

# 3. Get service URL
kubectl get services
```

## AWS EC2 Deployment

### Option 1: Docker

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Clone & Run
git clone <your-repo>
cd uas
docker build -t circle-calculator .
docker run -d -p 80:5000 \
  -e SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -e SMTP_EMAIL="your@email.com" \
  -e SMTP_PASSWORD="your-password" \
  circle-calculator

# Access: http://your-ec2-ip
```

### Option 2: Direct Python

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Python & dependencies
sudo apt update
sudo apt install -y python3 python3-pip
git clone <your-repo>
cd uas
pip3 install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
SMTP_EMAIL=your@email.com
SMTP_PASSWORD=your-password
EOF

# Run with nohup (background)
nohup python3 app.py > app.log 2>&1 &

# Or use screen
screen -S app
python3 app.py
# Ctrl+A, D to detach

# Access: http://your-ec2-ip:5000
```

### Option 3: systemd Service (Production)

```bash
# Create service file
sudo tee /etc/systemd/system/circle-calculator.service > /dev/null <<EOF
[Unit]
Description=Circle Calculator Web App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/uas
Environment="PATH=/usr/bin"
EnvironmentFile=/home/ubuntu/uas/.env
ExecStart=/usr/bin/python3 /home/ubuntu/uas/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable circle-calculator
sudo systemctl start circle-calculator

# Check status
sudo systemctl status circle-calculator

# View logs
sudo journalctl -u circle-calculator -f
```

## Security Groups (AWS EC2)

Add inbound rules:
- **Port 80** (HTTP) - 0.0.0.0/0
- **Port 5000** (Flask) - 0.0.0.0/0
- **Port 22** (SSH) - Your IP only

## Features

- ✅ Passwordless authentication (OTP via email)
- ✅ Session management
- ✅ Circle area & circumference calculator
- ✅ Responsive UI
- ✅ Docker containerized
- ✅ Kubernetes ready

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS
- **Email**: SMTP (Gmail)
- **Container**: Docker
- **Orchestration**: Kubernetes

## License

MIT

---

**Author**: Syifa Kaffa Billah  
**Course**: UAS Komputasi Awan - Universitas Indonesia