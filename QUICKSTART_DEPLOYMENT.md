# Quick Start Deployment Guide

## 🚀 FASTEST WAY: Deploy to Streamlit Cloud (5 minutes)

### 1. Commit your code to GitHub
```bash
git add .
git commit -m "Deployment ready with Streamlit config"
git push origin main
```

### 2. Go to Streamlit Cloud
Visit: https://share.streamlit.io/

### 3. Click "New app"
- Select your GitHub account
- Repository: `aqi_prediction`
- Branch: `main`
- File path: `src/apps/dashboard.py`

### 4. Done! 🎉
Your app will be live in seconds at:
```
https://share.streamlit.io/YOUR-USERNAME/aqi_prediction/main/src/apps/dashboard.py
```

---

## 🐳 Docker Local Test (Before deploying)

### Build and run locally:
```bash
docker build -t aqi-predictor:latest .
docker run -p 8501:8501 aqi-predictor:latest
```

Visit: http://localhost:8501

---

## ☁️ Other Cloud Options (Pick ONE)

### **Google Cloud Run** (Recommended for production)
```bash
gcloud builds submit --tag gcr.io/YOUR-PROJECT/aqi-predictor
gcloud run deploy aqi-predictor \
  --image gcr.io/YOUR-PROJECT/aqi-predictor \
  --platform managed --region us-central1 \
  --memory 1Gi --allow-unauthenticated
```

### **DigitalOcean App Platform**
1. Connect GitHub repo
2. Select Dockerfile
3. Deploy (automatic updates on push)

### **AWS EC2 + Nginx** (Full control)
See DEPLOYMENT_GUIDE.md for complete instructions

### **Heroku** (Simple but paid)
```bash
heroku create aqi-predictor
echo "web: streamlit run src/apps/dashboard.py --server.port=\$PORT" > Procfile
git push heroku main
```

---

## ✅ Checklist Before Deployment

- [ ] Files committed to GitHub
- [ ] `requirements.txt` is complete
- [ ] `.streamlit/config.toml` exists
- [ ] All model files in `models/` directory
- [ ] Data file `data/aqi_data.csv` present
- [ ] Works locally: `streamlit run src/apps/dashboard.py`

---

## 📊 View Your Deployed App

After deployment:
1. Get the public URL
2. Share it with users
3. Monitor usage and logs

---

For detailed instructions, see: **DEPLOYMENT_GUIDE.md**
