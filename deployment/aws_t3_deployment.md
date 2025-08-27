# 🚀 AWS t3 Instance Deployment Guide

This guide provides step-by-step instructions to deploy Habit Rabbit on an AWS t3 instance.

## 📋 Prerequisites

- AWS Account with appropriate permissions
- Basic knowledge of AWS EC2 and SSH
- Domain name (optional, for custom domain setup)

## 🏗️ Deployment Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────────┐
│             AWS t3 Instance             │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │     Nginx       │ │   Streamlit     ││
│  │  (Port 80/443)  │ │  (Port 8501)    ││
│  │   Reverse       │ │    Frontend     ││
│  │     Proxy       │ │                 ││
│  └─────────────────┘ └─────────────────┘│
│           │                             │
│           ▼                             │
│  ┌─────────────────┐ ┌─────────────────┐│
│  │    FastAPI      │ │     SQLite      ││
│  │  (Port 8000)    │ │    Database     ││
│  │    Backend      │ │   (habits.db)   ││
│  └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────┘
```

## 🚀 Step 1: Launch EC2 Instance

### 1.1 Instance Configuration
```bash
# Recommended Instance Type: t3.micro (Free tier eligible) or t3.small
# Operating System: Ubuntu 22.04 LTS
# Storage: 20 GB gp3 (minimum)
# Security Group: Allow HTTP (80), HTTPS (443), SSH (22), Custom (8501, 8000)
```

### 1.2 Security Group Rules
```
Type            Protocol    Port Range    Source
SSH             TCP         22           Your IP
HTTP            TCP         80           0.0.0.0/0
HTTPS           TCP         443          0.0.0.0/0
Custom TCP      TCP         8000         0.0.0.0/0  (FastAPI)
Custom TCP      TCP         8501         0.0.0.0/0  (Streamlit)
```

### 1.3 Launch Instance
1. Go to AWS EC2 Console
2. Click "Launch Instance"
3. Choose Ubuntu 22.04 LTS AMI
4. Select t3.micro or t3.small
5. Configure security group as above
6. Create or select a key pair
7. Launch the instance

## 🔧 Step 2: Connect and Setup Server

### 2.1 Connect to Instance
```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-instance-public-ip

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git nginx
```

### 2.2 Install Python Dependencies
```bash
# Install Python 3.10+ (if needed)
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```

## 📁 Step 3: Deploy Application Code

### 3.1 Clone or Upload Code
```bash
# Option 1: Clone from repository (if you have one)
git clone https://github.com/your-repo/habit-rabbit.git
cd habit-rabbit

# Option 2: Create directory and upload files
mkdir -p /home/ubuntu/habit-rabbit
cd /home/ubuntu/habit-rabbit

# You would then upload your code files via SCP or SFTP
```

### 3.2 Upload Files via SCP (if not using git)
```bash
# From your local machine, upload the project
scp -i your-key.pem -r backend/ ubuntu@your-instance-ip:/home/ubuntu/habit-rabbit/
scp -i your-key.pem -r frontend/ ubuntu@your-instance-ip:/home/ubuntu/habit-rabbit/
```

## 🔧 Step 4: Setup Backend (FastAPI)

### 4.1 Create Backend Service
```bash
cd /home/ubuntu/habit-rabbit/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test backend
python main.py
# Ctrl+C to stop after testing
```

### 4.2 Create Systemd Service for Backend
```bash
sudo nano /etc/systemd/system/habit-rabbit-backend.service
```

Add the following content:
```ini
[Unit]
Description=Habit Rabbit FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/habit-rabbit/backend
Environment=PATH=/home/ubuntu/habit-rabbit/backend/venv/bin
ExecStart=/home/ubuntu/habit-rabbit/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.3 Enable and Start Backend Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable habit-rabbit-backend
sudo systemctl start habit-rabbit-backend
sudo systemctl status habit-rabbit-backend
```

## 🎨 Step 5: Setup Frontend (Streamlit)

### 5.1 Setup Frontend Environment
```bash
cd /home/ubuntu/habit-rabbit/frontend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5.2 Update Frontend Configuration
```bash
nano app.py
```

Update the API_BASE_URL:
```python
# Change from:
API_BASE_URL = "http://localhost:8000"

# To:
API_BASE_URL = "http://localhost:8000"  # Keep localhost since they're on same server
```

### 5.3 Create Systemd Service for Frontend
```bash
sudo nano /etc/systemd/system/habit-rabbit-frontend.service
```

Add the following content:
```ini
[Unit]
Description=Habit Rabbit Streamlit Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/habit-rabbit/frontend
Environment=PATH=/home/ubuntu/habit-rabbit/frontend/venv/bin
ExecStart=/home/ubuntu/habit-rabbit/frontend/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.4 Enable and Start Frontend Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable habit-rabbit-frontend
sudo systemctl start habit-rabbit-frontend
sudo systemctl status habit-rabbit-frontend
```

## 🌐 Step 6: Configure Nginx Reverse Proxy

### 6.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/habit-rabbit
```

Add the following content:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or instance IP

    # Frontend (Streamlit)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for Streamlit
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header X-Accel-Buffering no;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
    }
}
```

### 6.2 Enable Site and Restart Nginx
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/habit-rabbit /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔒 Step 7: SSL/HTTPS Setup (Optional but Recommended)

### 7.1 Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 Obtain SSL Certificate
```bash
# Replace your-domain.com with your actual domain
sudo certbot --nginx -d your-domain.com

# Follow the prompts to complete setup
```

### 7.3 Auto-renewal Setup
```bash
# Test auto-renewal
sudo certbot renew --dry-run

# The renewal cron job is automatically created
```

## 🔥 Step 8: Configure Firewall

### 8.1 Setup UFW (Ubuntu Firewall)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (important!)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Check status
sudo ufw status
```

## 📊 Step 9: Monitoring and Maintenance

### 9.1 Service Management Commands
```bash
# Check service status
sudo systemctl status habit-rabbit-backend
sudo systemctl status habit-rabbit-frontend
sudo systemctl status nginx

# View logs
sudo journalctl -u habit-rabbit-backend -f
sudo journalctl -u habit-rabbit-frontend -f
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart habit-rabbit-backend
sudo systemctl restart habit-rabbit-frontend
sudo systemctl restart nginx
```

### 9.2 Database Backup Script
```bash
nano /home/ubuntu/backup-db.sh
```

Add content:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Backup SQLite database
cp /home/ubuntu/habit-rabbit/backend/habits.db $BACKUP_DIR/habits_$DATE.db

# Keep only last 7 days of backups
find $BACKUP_DIR -name "habits_*.db" -mtime +7 -delete

echo "Database backup completed: habits_$DATE.db"
```

Make executable and add to crontab:
```bash
chmod +x /home/ubuntu/backup-db.sh

# Add to crontab for daily backup at 2 AM
crontab -e
# Add line: 0 2 * * * /home/ubuntu/backup-db.sh
```

## 📋 Step 10: Testing Deployment

### 10.1 Test Backend API
```bash
# Test API directly
curl http://localhost:8000/

# Test through nginx
curl http://your-instance-ip/api/
```

### 10.2 Test Frontend
```bash
# Open in browser
http://your-instance-ip  # or your domain name
```

### 10.3 End-to-End Testing
1. Open the web application
2. Add a new habit
3. Mark it as complete
4. Check analytics page
5. Verify data persistence

## 🔧 Troubleshooting

### Common Issues and Solutions

**1. Service won't start:**
```bash
# Check logs
sudo journalctl -u habit-rabbit-backend -n 50
sudo journalctl -u habit-rabbit-frontend -n 50

# Check if ports are in use
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :8501
```

**2. Database permissions:**
```bash
# Fix database permissions
sudo chown ubuntu:ubuntu /home/ubuntu/habit-rabbit/backend/habits.db
chmod 644 /home/ubuntu/habit-rabbit/backend/habits.db
```

**3. Nginx configuration issues:**
```bash
# Test nginx config
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

**4. Frontend not loading:**
```bash
# Check Streamlit is running
ps aux | grep streamlit

# Check if service is active
sudo systemctl status habit-rabbit-frontend

# Restart if needed
sudo systemctl restart habit-rabbit-frontend
```

## 💰 Cost Estimation

### Monthly AWS Costs (t3.micro)
- **t3.micro instance**: ~$8.50/month (Free tier: $0 for first 12 months)
- **20 GB EBS storage**: ~$2.00/month
- **Data transfer**: ~$1-5/month (depending on usage)
- **Total**: ~$11.50/month (after free tier)

### Monthly AWS Costs (t3.small)
- **t3.small instance**: ~$16.79/month
- **20 GB EBS storage**: ~$2.00/month
- **Data transfer**: ~$1-5/month
- **Total**: ~$19.79/month

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest code (if using git)
cd /home/ubuntu/habit-rabbit
git pull origin main

# Restart services
sudo systemctl restart habit-rabbit-backend
sudo systemctl restart habit-rabbit-frontend

# Or update individual files and restart
sudo systemctl restart habit-rabbit-backend
sudo systemctl restart habit-rabbit-frontend
```

### System Updates
```bash
# Regular system updates
sudo apt update && sudo apt upgrade -y

# Reboot if kernel updates
sudo reboot
```

## 📞 Support and Monitoring

### Health Checks
```bash
# Create health check script
nano /home/ubuntu/health-check.sh
```

Add content:
```bash
#!/bin/bash
# Health check script

echo "=== Habit Rabbit Health Check ==="
echo "Date: $(date)"

# Check backend
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend: OK"
else
    echo "❌ Backend: FAILED"
fi

# Check frontend
if curl -s http://localhost:8501/_stcore/health > /dev/null; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAILED"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️  Disk usage: ${DISK_USAGE}% (Warning)"
else
    echo "✅ Disk usage: ${DISK_USAGE}%"
fi

echo "===================="
```

## 🎉 Congratulations!

Your Habit Rabbit application is now deployed on AWS! 🐰

**Access your application at:**
- **Main App**: `http://your-instance-ip` or `https://your-domain.com`
- **API Docs**: `http://your-instance-ip/api/docs`

Remember to:
- 🔐 Set up regular backups
- 📊 Monitor resource usage
- 🔄 Keep the system updated
- 🛡️ Review security settings periodically

---

**Happy habit tracking! 🌟**
