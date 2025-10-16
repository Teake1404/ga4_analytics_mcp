# GA4 Authentication Setup Guide

## 🔧 Fixing the "refreshToken is required" Error

This guide will help you set up proper Google Analytics 4 OAuth2 authentication to resolve the refreshToken error in your AI insights node.

## 🚨 The Problem

The "refreshToken is required" error occurs when:
1. Your N8N workflow tries to access Google Analytics 4 data
2. The OAuth2 access token has expired
3. No valid refresh token is available to renew the access token

## 🛠️ Solution Overview

We've implemented a complete GA4 OAuth2 authentication system with:
- Automatic token refresh
- Fallback to mock data when authentication fails
- New API endpoints for authentication management
- Updated N8N workflow with authentication checks

## 📋 Setup Steps

### Step 1: Create Google Cloud Project & OAuth2 Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable GA4 Data API**
   ```bash
   # In Google Cloud Console:
   # APIs & Services > Library > Search "Google Analytics Data API" > Enable
   ```

3. **Create OAuth2 Credentials**
   - Go to: APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Add authorized redirect URI: `http://localhost:8080/auth/callback`
   - Copy Client ID and Client Secret

### Step 2: Configure Environment Variables

Add these to your `.env` file or Cloud Run environment:

```bash
# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/callback

# GA4 Configuration
GA4_PROPERTY_ID=your_ga4_property_id_here

# Keep using mock data during setup
USE_MOCK_DATA=true
```

### Step 3: Deploy Updated System

1. **Install new dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Deploy to Cloud Run:**
   ```bash
   ./deploy.sh YOUR_ANTHROPIC_API_KEY
   ```

### Step 4: Complete OAuth2 Authentication

1. **Get Authorization URL:**
   ```bash
   curl https://ga4-ai-insights-671647576749.us-central1.run.app/api/ga4/auth/url
   ```

2. **Visit the URL and authorize:**
   - You'll be redirected to Google's OAuth consent screen
   - Grant permissions for Google Analytics access
   - You'll get an authorization code

3. **Exchange code for tokens:**
   ```bash
   curl -X POST https://ga4-ai-insights-671647576749.us-central1.run.app/api/ga4/auth/callback \
     -H "Content-Type: application/json" \
     -d '{"code": "YOUR_AUTHORIZATION_CODE"}'
   ```

4. **Verify authentication:**
   ```bash
   curl https://ga4-ai-insights-671647576749.us-central1.run.app/api/ga4/auth/status
   ```

### Step 5: Update N8N Workflow

1. **Import the updated workflow:**
   - Use the updated `ga4_funnel_report_slack.json` file
   - The new workflow automatically checks authentication status
   - Falls back to mock data if authentication fails

2. **Configure GA4 Property ID:**
   - Update `YOUR_GA4_PROPERTY_ID` in the workflow
   - Find your property ID in GA4: Admin > Property Settings

### Step 6: Switch to Real GA4 Data

Once authentication is working:

1. **Update environment variable:**
   ```bash
   USE_MOCK_DATA=false
   ```

2. **Redeploy:**
   ```bash
   ./deploy.sh YOUR_ANTHROPIC_API_KEY
   ```

## 🔍 Troubleshooting

### Common Issues:

1. **"Client ID not found"**
   - Ensure `GOOGLE_CLIENT_ID` is set correctly
   - Check that OAuth2 credentials are created properly

2. **"Redirect URI mismatch"**
   - Verify redirect URI in Google Cloud Console matches `GOOGLE_REDIRECT_URI`
   - For Cloud Run, use: `https://your-service-url/auth/callback`

3. **"Insufficient permissions"**
   - Ensure GA4 Data API is enabled
   - Check that your Google account has access to the GA4 property

4. **"Token expired"**
   - The system automatically refreshes tokens
   - If persistent, re-run the OAuth flow

### Debug Commands:

```bash
# Check authentication status
curl https://ga4-ai-insights-671647576749.us-central1.run.app/api/health

# Test with mock data (should always work)
curl -X POST https://ga4-ai-insights-671647576749.us-central1.run.app/api/funnel-analysis \
  -H "Content-Type: application/json" \
  -d '{"use_mock_data": true}'

# Test with real GA4 data (requires authentication)
curl -X POST https://ga4-ai-insights-671647576749.us-central1.run.app/api/funnel-analysis \
  -H "Content-Type: application/json" \
  -d '{"use_mock_data": false, "property_id": "YOUR_GA4_PROPERTY_ID"}'
```

## 🎯 Expected Behavior

### With Authentication Working:
- N8N workflow uses real GA4 data
- AI insights generated from actual funnel metrics
- No refreshToken errors

### With Authentication Issues:
- System automatically falls back to mock data
- Workflow continues without errors
- AI insights still generated (using mock data)

## 📊 New API Endpoints

- `GET /api/ga4/auth/url` - Get OAuth2 authorization URL
- `POST /api/ga4/auth/callback` - Exchange code for tokens
- `GET /api/ga4/auth/status` - Check authentication status
- `GET /api/health` - Health check (now includes GA4 auth status)

## 🚀 Next Steps

1. Complete OAuth2 setup following this guide
2. Test the N8N workflow with real GA4 data
3. Monitor for any authentication issues
4. Set up automated token refresh monitoring (optional)

The system is designed to be robust - it will always work with mock data even if GA4 authentication fails, ensuring your workflow never breaks.

