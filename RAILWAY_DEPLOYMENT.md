# Railway Deployment Guide for GA4 Funnel Analysis

## ✅ Deployment Ready Status

Your GA4 Funnel Analysis is **ready for Railway deployment**! The application has been configured to work seamlessly with Railway's platform.

## 🚀 Quick Deploy to Railway

### Method 1: Deploy via Railway CLI (Recommended)

1. **Install Railway CLI** (if not already installed):
```bash
npm i -g @railway/cli
```

2. **Login to Railway**:
```bash
railway login
```

3. **Initialize and deploy**:
```bash
# Navigate to your project directory
cd /Users/shuqingke/Documents/ga4_analytics_mcp

# Initialize Railway project
railway init

# Deploy
railway up
```

### Method 2: Deploy via Railway Dashboard

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo" (connect your repo) OR "Empty Project"
4. If using empty project:
   - Click "New Service" → "GitHub Repo" → Select your repo
   - OR drag and drop your project folder

## 🔧 Required Environment Variables

Set these in Railway Dashboard → Your Service → Variables:

### **Required:**
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
PORT=8080  # Railway sets this automatically, but you can override
```

### **Optional (for mock data mode - recommended for client demos):**
```bash
USE_MOCK_DATA=true  # Default: true (works without GA4 credentials)
LOG_LEVEL=INFO      # Default: INFO
```

### **Optional (for real GA4 data):**
```bash
USE_MOCK_DATA=false
GA4_PROPERTY_ID=your-ga4-property-id
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-railway-app.up.railway.app/api/ga4/auth/callback
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json  # Or use JSON content as env var
```

### **Optional (for Redis caching):**
```bash
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```

**Note:** Redis is optional. The app will work without it (uses in-memory mock cache).

## 📋 Deployment Checklist

- ✅ **Procfile** exists and uses `$PORT` variable
- ✅ **Dockerfile** configured for production
- ✅ **requirements.txt** includes all dependencies
- ✅ **Environment variables** properly configured
- ✅ **Redis cache** is optional (app works without it)
- ✅ **Mock data mode** enabled by default (no GA4 credentials needed)
- ✅ **Port configuration** uses Railway's `$PORT` variable
- ✅ **Null pointer bugs** fixed (Redis checks added)

## 🔍 Verify Deployment

After deployment, test your endpoints:

1. **Health Check**:
```bash
curl https://your-app.up.railway.app/api/health
```

2. **API Info**:
```bash
curl https://your-app.up.railway.app/api
```

3. **Funnel Report Page** (for client sharing):
```bash
# Open in browser:
https://your-app.up.railway.app/funnel-report
```

4. **Funnel Analysis API** (with mock data):
```bash
curl -X POST https://your-app.up.railway.app/api/funnel-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "123456789",
    "date_range": "last_30_days",
    "funnel_steps": ["view_item", "add_to_cart", "purchase"],
    "dimensions": ["sessionDefaultChannelGroup", "deviceCategory", "browser"]
  }'
```

## 📊 Client Sharing Features

Your deployment includes these client-ready features:

### 1. **Funnel Report Page** (HTML)
- **URL**: `https://your-app.up.railway.app/funnel-report`
- Beautiful HTML report with metrics and tables
- Perfect for sharing with clients
- Works with mock data or real GA4 data

### 2. **API Endpoints** (JSON)
- `/api/funnel-analysis` - Full analysis with AI insights
- `/api/keyword-product-insights` - SEO-to-revenue insights (instant demo)
- `/api/health` - Health check

### 3. **Interactive Demo**
- Mock data enabled by default
- No GA4 credentials required for demos
- Instant responses (no API delays)

## 🎯 Client Demo Workflow

1. **Share the funnel report URL**:
   ```
   https://your-app.up.railway.app/funnel-report
   ```

2. **Or use the API endpoint**:
   ```bash
   curl -X POST https://your-app.up.railway.app/api/funnel-analysis \
     -H "Content-Type: application/json" \
     -d '{"use_mock_data": true}'
   ```

3. **Show keyword insights** (instant demo):
   ```bash
   curl -X POST https://your-app.up.railway.app/api/keyword-product-insights \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

## 🐛 Troubleshooting

### Issue: App not starting
- **Check**: Railway logs (`railway logs` or Dashboard → Logs)
- **Verify**: `ANTHROPIC_API_KEY` is set
- **Verify**: Port is set correctly (Railway auto-sets `$PORT`)

### Issue: Redis connection errors
- **Solution**: This is normal if Redis is not configured
- **Status**: App works without Redis (uses mock cache)
- **To fix**: Add Redis service in Railway or ignore warnings

### Issue: Missing `pre_generated_mock_data.json`
- **Solution**: The file is included in your repo
- **Verify**: File exists in project root
- **Fix**: If missing, the app will generate fresh mock data

### Issue: Module import errors
- **Solution**: Check `requirements.txt` includes all dependencies
- **Fix**: Railway installs from `requirements.txt` automatically

## 📈 Scaling on Railway

### Free Tier Limits:
- 512 MB RAM
- $5 credit/month

### Recommended Settings:
- **Memory**: 512 MB (minimum) - 1 GB (recommended)
- **CPU**: 1 vCPU
- **Workers**: 2 (as configured in Procfile)

### Upgrade for Production:
- More RAM for concurrent requests
- Higher CPU for AI processing
- Add Redis service for caching (optional)

## 🔒 Security Notes

1. **API Keys**: Never commit API keys to git
2. **Environment Variables**: Use Railway's Variables section
3. **CORS**: Currently set to `*` for demos (restrict in production)
4. **Authentication**: Consider adding API keys for production use

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Health Check**: Always check `/api/health` first
- **Logs**: Use `railway logs` for debugging

## ✅ Final Checklist Before Client Demo

- [ ] Deployed to Railway successfully
- [ ] Health check returns 200 OK
- [ ] `/funnel-report` page loads
- [ ] `/api/funnel-analysis` endpoint works
- [ ] Mock data is enabled (`USE_MOCK_DATA=true`)
- [ ] `ANTHROPIC_API_KEY` is set
- [ ] Railway URL is accessible
- [ ] Tested with sample request

---

**Your GA4 Funnel Analysis is deployment-ready! 🚀**

Deploy now and share the URL with your clients.
