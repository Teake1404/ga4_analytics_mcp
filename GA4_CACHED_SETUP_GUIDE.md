# GA4 Cached System Setup Guide

## 🎯 **What We Built**

A fast GA4 data analysis system that mimics GoMarble's speed by implementing cached data access and background syncing, then provides AI-powered insights through Claude.

## 🏗️ **Architecture**

```
Background Sync (every 15 mins) → Redis Cache → Fast API → n8n/Claude
```

### **Components:**
1. **GA4 Client** (`ga4_client.py`) - Service account authentication
2. **Redis Cache** (`redis_cache.py`) - Fast data storage with TTL
3. **Background Sync** (`background_sync.py`) - Scheduled cache refresh
4. **API Endpoints** - Fast cached data access
5. **N8N Workflow** - Automated reporting

## 🚀 **Setup Steps**

### **1. GA4 Service Account Setup**

1. **Add service account to GA4:**
   - Go to GA4 Admin → Property Access Management
   - Add: `n8n-ga4-reader@titanium-gadget-451710-i7.iam.gserviceaccount.com`
   - Role: Analyst (or higher)

2. **Set environment variable:**
   ```bash
   export GA4_SA_JSON='{"type":"service_account","project_id":"titanium-gadget-451710-i7",...}'
   ```

### **2. Redis Setup**

**Option A: Local Redis (Development)**
```bash
# Install Redis
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Start Redis
redis-server

# Test connection
redis-cli ping  # Should return PONG
```

**Option B: Redis Cloud (Production)**
1. Sign up at [Redis Cloud](https://redis.com/cloud/)
2. Create a free database
3. Get connection details

**Option C: Google Memorystore (Cloud Run)**
1. Create Memorystore Redis instance in GCP
2. Configure VPC access for Cloud Run

### **3. Environment Variables**

```bash
# GA4 Authentication
GA4_SA_JSON='{"type":"service_account",...}'

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Optional
REDIS_DB=0

# API Configuration
API_BASE_URL=https://your-api-url.com
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional
LOG_LEVEL=INFO
```

### **4. Deploy to Cloud Run**

```bash
# Deploy with Redis and GA4 credentials
gcloud run deploy ga4-insights-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --project titanium-gadget-451710-i7 \
  --timeout 600s \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars="GA4_SA_JSON=YOUR_JSON_HERE,ANTHROPIC_API_KEY=YOUR_KEY_HERE,REDIS_HOST=YOUR_REDIS_HOST,REDIS_PORT=6379" \
  --allow-unauthenticated
```

## 📊 **API Endpoints**

### **Fast Endpoints (2-3 seconds)**
- `GET /api/ga4/cached?property_id=476872592&report_type=funnel` - Get cached data
- `POST /api/ga4/instant-analysis` - Cached data + AI insights

### **Background Endpoints**
- `POST /api/ga4/refresh-cache` - Refresh cache (run every 15 mins)

### **Debug Endpoints**
- `POST /api/ga4/run-report` - Direct GA4 call (slow, 30-60s)

## 🔄 **N8N Workflow Setup**

1. **Import workflow:** `ga4_cached_n8n_workflow.json`

2. **Configure:**
   - Update URLs to your deployed API
   - Set Slack channel and credentials
   - Adjust schedule intervals

3. **Two schedules:**
   - **Cache Refresh:** Every 15 minutes
   - **Report Generation:** Every hour

## 🧪 **Testing**

### **1. Test Cache Refresh**
```bash
curl -X POST https://your-api.com/api/ga4/refresh-cache \
  -H "Content-Type: application/json" \
  -d '{"property_id": "476872592"}'
```

### **2. Test Cached Data**
```bash
curl "https://your-api.com/api/ga4/cached?property_id=476872592&report_type=funnel"
```

### **3. Test Instant Analysis**
```bash
curl -X POST https://your-api.com/api/ga4/instant-analysis \
  -H "Content-Type: application/json" \
  -d '{"property_id": "476872592", "use_mock_data": false}'
```

## 📈 **Performance Comparison**

| Method | Response Time | Data Freshness |
|--------|---------------|----------------|
| Direct GA4 API | 30-60 seconds | Real-time |
| Cached System | 2-3 seconds | 15 minutes old |
| Mock Data | 1-2 seconds | Static |

## 🔧 **Troubleshooting**

### **Redis Connection Issues**
```bash
# Test Redis connection
redis-cli ping

# Check Redis logs
redis-cli monitor
```

### **GA4 Authentication Issues**
```bash
# Test service account
python -c "from ga4_client import GA4Client; print(GA4Client().get_overview_metrics('476872592'))"
```

### **Cache Not Found**
- Run `/api/ga4/refresh-cache` first
- Check Redis is running
- Verify environment variables

## 🎯 **Expected Results**

- ✅ API response time < 3 seconds
- ✅ Data freshness < 15 minutes old  
- ✅ Claude insights generated in real-time
- ✅ N8N workflow completes in < 10 seconds
- ✅ No more 30-60 second waits

## 📁 **Files Created**

- `ga4_client.py` - GA4 API integration
- `redis_cache.py` - Redis caching layer  
- `background_sync.py` - Data refresh service
- `ga4_cached_n8n_workflow.json` - N8N workflow
- `GA4_CACHED_SETUP_GUIDE.md` - This guide

## 🚀 **Next Steps**

1. **Deploy the system** with your service account JSON
2. **Set up Redis** (local or cloud)
3. **Import N8N workflow** and configure
4. **Test the endpoints** to verify speed
5. **Enjoy 2-3 second GA4 insights!**

This architecture delivers GoMarble-speed GA4 insights while maintaining your customization advantage!

