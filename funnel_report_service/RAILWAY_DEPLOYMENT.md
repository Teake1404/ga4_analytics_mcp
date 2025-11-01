# Railway Deployment Guide

## Option 1: Using Railway UI (Recommended)

1. **Go to Railway Dashboard**: https://railway.app
2. **Create New Project**: Click "New Project"
3. **Connect GitHub**: Select "Deploy from GitHub repo"
4. **Select Repository**: Choose `ga4_analytics_mcp`
5. **Configure Deployment**:
   - Railway will detect the Dockerfile automatically
   - If it doesn't, go to **Settings** → **Root Directory**
   - Set Root Directory to: `funnel_report_service`
   - **OR** if Railway reads from root, the updated Dockerfile will handle it

## Option 2: Using Railway CLI

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

## Environment Variables (Optional)

If you want to use real GA4 data instead of mock data, set these in Railway:

- `GA4_PROPERTY_ID` - Your GA4 Property ID
- `ANTHROPIC_API_KEY` - Your Claude API key (for AI insights)
- `LOG_LEVEL` - Set to `INFO` or `DEBUG`

## Deploy with Root Directory

**In Railway Dashboard:**
1. Go to your service
2. Click **Settings** tab
3. Scroll to **Root Directory**
4. Enter: `funnel_report_service`
5. Click **Save**

The Dockerfile has been updated to work from the repository root as well, so either method works.

## After Deployment

Your service will be available at: `https://[your-service-name].up.railway.app`

Test it:
- Main report: `https://[your-service-name].up.railway.app/`
- Health check: `https://[your-service-name].up.railway.app/api/health`

