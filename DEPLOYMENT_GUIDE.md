# Deployment Guide for AQI Prediction Dashboard

## 🚀 Deployment Options

Your Streamlit app can be deployed on multiple platforms. Here are the best options:

---

## **OPTION 1: Streamlit Cloud (Recommended - FREE & EASIEST)**

### ✅ Best for:
- Free hosting
- Easy deployment
- Automatic updates from GitHub
- No server management

### 📋 Steps:

#### 1️⃣ **Prepare Your Repository**
```bash
# Make sure all changes are committed and pushed
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2️⃣ **Create `requirements.txt`** (if not present)
```bash
# Generate requirements from your environment
pip freeze > requirements.txt
```

#### 3️⃣ **Create `.streamlit/config.toml`** (Configuration file)
```
mkdir -p .streamlit
```

Create file: `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = true
runOnSave = true
```

#### 4️⃣ **Deploy via Streamlit Cloud**
1. Go to: https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub account
4. Select your repository: `aqi_prediction`
5. Select branch: `main`
6. Set main file path: `src/apps/dashboard.py`
7. Click "Deploy"

**Your app will be live at:** `https://share.streamlit.io/[your-username]/aqi_prediction/main/src/apps/dashboard.py`

#### 5️⃣ **Set Secrets** (if needed)
In Streamlit Cloud dashboard:
- Settings → Secrets
- Add any API keys or sensitive data in `secrets.toml` format

---

## **OPTION 2: Docker + Cloud Platform**

### ✅ Best for:
- Production environments
- Full control
- Custom configurations
- Deploying to AWS, Google Cloud, Azure, DigitalOcean

### 📋 Steps:

#### 1️⃣ **Create Dockerfile**

File: `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run Streamlit
CMD ["streamlit", "run", "src/apps/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2️⃣ **Create `.dockerignore`**

File: `.dockerignore`
```
venv/
.git/
.gitignore
*.pyc
__pycache__/
.env
.DS_Store
*.log
node_modules/
.ipynb_checkpoints/
```

#### 3️⃣ **Build & Test Locally**
```bash
docker build -t aqi-predictor:latest .
docker run -p 8501:8501 aqi-predictor:latest
```

Access at: `http://localhost:8501`

#### 4️⃣ **Deploy to Cloud**

**Option A: Google Cloud Run**
```bash
# Authenticate
gcloud auth login

# Build image
gcloud builds submit --tag gcr.io/[YOUR-PROJECT-ID]/aqi-predictor

# Deploy
gcloud run deploy aqi-predictor \
  --image gcr.io/[YOUR-PROJECT-ID]/aqi-predictor \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --allow-unauthenticated
```

**Option B: AWS ECS**
```bash
# Create ECR repository
aws ecr create-repository --repository-name aqi-predictor

# Push image to ECR
docker tag aqi-predictor:latest [YOUR-ACCOUNT-ID].dkr.ecr.us-east-1.amazonaws.com/aqi-predictor:latest
docker push [YOUR-ACCOUNT-ID].dkr.ecr.us-east-1.amazonaws.com/aqi-predictor:latest

# Deploy via Elastic Container Service
# (Configure in AWS Console)
```

**Option C: DigitalOcean App Platform**
1. Go to: https://cloud.digitalocean.com/apps
2. Connect GitHub repository
3. Select branch and Dockerfile
4. Configure resources
5. Deploy

---

## **OPTION 3: Heroku (Free tier discontinued, but still viable)**

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create aqi-predictor

# Create Procfile
echo "web: streamlit run src/apps/dashboard.py --server.port=\$PORT" > Procfile

# Transfer files
git push heroku main

# View logs
heroku logs --tail
```

---

## **OPTION 4: Self-Hosted VPS (AWS EC2, DigitalOcean, Linode)**

### ✅ Best for:
- Full control
- Custom requirements
- High performance needs

### 📋 Steps:

#### 1️⃣ **SSH into your server**
```bash
ssh -i your-key.pem ubuntu@your-server-ip
```

#### 2️⃣ **Install dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

#### 3️⃣ **Clone repository**
```bash
cd /var/www
git clone https://github.com/[your-username]/aqi_prediction.git
cd aqi_prediction
```

#### 4️⃣ **Setup virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5️⃣ **Create systemd service**

File: `/etc/systemd/system/aqi-dashboard.service`
```ini
[Unit]
Description=AQI Prediction Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/aqi_prediction
Environment="PATH=/var/www/aqi_prediction/venv/bin"
ExecStart=/var/www/aqi_prediction/venv/bin/streamlit run src/apps/dashboard.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable aqi-dashboard
sudo systemctl start aqi-dashboard
```

#### 6️⃣ **Setup Nginx reverse proxy**

File: `/etc/nginx/sites-available/aqi-predictor`
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/aqi-predictor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7️⃣ **Setup SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## **Quick Comparison**

| Platform | Cost | Setup Time | Best For | Difficulty |
|---|---|---|---|---|
| **Streamlit Cloud** | Free | 5 min | Quick demos, prototypes | ⭐ Very Easy |
| **Google Cloud Run** | $0.00175/req + $11.26/month | 15 min | Production, autoscale | ⭐⭐ Easy |
| **DigitalOcean** | $6-10/month | 20 min | Small production | ⭐⭐ Easy |
| **AWS ECS** | $0.05-1/day | 30 min | Enterprise | ⭐⭐⭐ Medium |
| **Heroku** | $7/month | 10 min | Hobby projects | ⭐ Very Easy |
| **Self-hosted VPS** | $5-20/month | 1 hour | Full control | ⭐⭐⭐ Medium |

---

## **Recommended Deployment Path**

### For Quick Launch:
1. **Use Streamlit Cloud** (takes 5 minutes)
2. Link your GitHub repo
3. Done! ✅

### For Production:
1. **Use Google Cloud Run** or **DigitalOcean**
2. Deploy with Docker
3. Custom domain + SSL
4. Better performance

### For Enterprise:
1. **Use AWS ECS** or **Kubernetes**
2. Full monitoring & logging
3. Auto-scaling
4. Complete infrastructure

---

## **Pre-Deployment Checklist**

- [ ] All files committed to GitHub
- [ ] `requirements.txt` updated
- [ ] `.streamlit/config.toml` created
- [ ] `.gitignore` configured (venv, __pycache__, etc.)
- [ ] Models folder included in repo or externally hosted
- [ ] Environment variables documented
- [ ] Data files (CSV) included or linked
- [ ] Tested locally with `streamlit run src/apps/dashboard.py`

---

## **Post-Deployment**

### Monitor Your App:
- Check logs regularly
- Set up error alerts
- Monitor performance metrics
- Update dependencies monthly

### Keep Data Fresh:
- If using CSV data, consider updating it periodically
- Or connect to a live data API (CPCB, IQAir, etc.)

### Scale if Needed:
- Monitor user load
- Increase server resources if needed
- Add caching for better performance
- Consider database for user data

---

## **Environment Variables Example**

Create `.streamlit/secrets.toml` for Streamlit Cloud:
```toml
[connections]
db_connection = "your-database-url"

[api]
weather_api_key = "your-api-key"
data_api_key = "your-data-api-key"

[settings]
max_users = 100
cache_ttl = 3600
```

---

## **Custom Domain Setup**

If using Streamlit Cloud:
1. Go to app settings
2. Add custom domain (e.g., aqi-predictor.com)
3. Update DNS CNAME record
4. Wait for verification (usually 24 hours)

If using DigitalOcean/self-hosted:
1. Update DNS A record to server IP
2. Point to your domain
3. Setup SSL certificate
4. Test with https://

---

## **Need Help?**

- **Streamlit Docs**: https://docs.streamlit.io
- **Docker Docs**: https://docs.docker.com
- **Google Cloud Run**: https://cloud.google.com/run/docs
- **DigitalOcean**: https://docs.digitalocean.com

---

**Start with Streamlit Cloud for fastest deployment!** 🚀
