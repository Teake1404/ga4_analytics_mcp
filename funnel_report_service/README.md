# GA4 Funnel Report Service

Standalone funnel analysis report service ready for Railway deployment.

## 🚀 Quick Deploy to Railway

### Method 1: Deploy via Railway Dashboard

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo" → Select this folder/repo
4. Railway will auto-detect `Procfile` and deploy

### Method 2: Deploy via Railway CLI

```bash
cd funnel_report_service
railway login
railway init
railway up
```

## 📋 What This Service Provides

- **Single endpoint:** `/` - Beautiful HTML funnel analysis report
- **Health check:** `/api/health`
- **Mock data:** Works immediately without GA4 credentials
- **Railway ready:** Auto-detects Procfile/Dockerfile

## 🔧 Environment Variables

No environment variables required! Uses mock data by default.

Optional:
- `LOG_LEVEL=INFO` (default)
- `PORT=8080` (Railway sets automatically)

## ✅ Features

- ✅ Beautiful HTML report with opportunities and issues
- ✅ Device category breakdown table
- ✅ Top opportunities and critical issues
- ✅ Baseline conversion rates
- ✅ Ready for client sharing
- ✅ No dependencies on external services

## 📊 Report Contents

- **Top Opportunities:** Best performing segments
- **Critical Issues:** Underperforming segments
- **Device Breakdown:** Desktop, mobile, tablet performance
- **Conversion Rates:** View→Cart, Cart→Purchase, Overall

---

**Deploy and share the URL with clients!** 🎯

