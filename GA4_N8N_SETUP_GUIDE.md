# GA4 + N8N + AI Insights Setup Guide

## 🎯 **Complete Workflow: GA4 → N8N → AI Analysis → Slack**

### **Step 1: Google Cloud Setup**

#### **A. Create Service Account**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create new one)
3. Enable APIs:
   - **Google Analytics Reporting API**
   - **Google Analytics Data API**
4. Go to **IAM & Admin** → **Service Accounts**
5. Create service account: `n8n-ga4-reader`
6. Download JSON key file

#### **B. Grant GA4 Access**
1. Go to your GA4 property
2. **Admin** → **Property access management**
3. Add service account email: `n8n-ga4-reader@your-project.iam.gserviceaccount.com`
4. Role: **Viewer**

### **Step 2: N8N Configuration**

#### **A. Import Workflow**
1. Import `ga4_direct_n8n_workflow.json` into N8N
2. Update these values:
   - `YOUR_GA4_PROPERTY_ID`: Your GA4 Property ID (e.g., `123456789`)
   - `YOUR_SLACK_CHANNEL`: Your Slack channel (e.g., `#analytics`)
   - `YOUR_SLACK_CREDENTIAL_ID`: Your Slack credentials

#### **B. Set up Credentials**
1. **Google Analytics OAuth2 API**:
   - Client ID: From Google Cloud Console
   - Client Secret: From Google Cloud Console
   - Scope: `https://www.googleapis.com/auth/analytics.readonly`

2. **Slack OAuth2 API**:
   - Set up Slack app in [api.slack.com](https://api.slack.com)
   - Add bot token scopes: `chat:write`, `channels:read`

### **Step 3: Test the Workflow**

#### **A. Manual Test**
1. Run the N8N workflow manually
2. Check each node for errors
3. Verify GA4 data is retrieved
4. Confirm AI insights are generated

#### **B. Schedule Automation**
1. Add **Cron** trigger node
2. Set schedule (e.g., daily at 9 AM)
3. Test automated execution

### **Step 4: Customize for Your Needs**

#### **A. Modify Date Range**
```json
"dateRanges": [
  {
    "startDate": "7daysAgo",  // Change to your preferred range
    "endDate": "today"
  }
]
```

#### **B. Add More Dimensions**
```json
"dimensions": [
  {
    "name": "sessionDefaultChannelGroup"
  },
  {
    "name": "deviceCategory"
  },
  {
    "name": "customEventName"  // Add your custom events
  }
]
```

#### **C. Customize Slack Message**
Edit the Slack node text to include:
- Specific metrics you care about
- Links to your dashboard
- Custom formatting

### **Step 5: Advanced Features**

#### **A. Error Handling**
Add **Error Trigger** node to handle:
- GA4 API failures
- AI insights timeout
- Slack delivery issues

#### **B. Conditional Logic**
Add **IF** nodes to:
- Only send reports on weekdays
- Skip if no critical issues found
- Send different messages based on conversion rates

#### **C. Data Filtering**
Add **Set** nodes to:
- Filter out test traffic
- Focus on specific channels
- Exclude internal users

## 🚀 **Ready-to-Use URLs**

- **Demo Report**: `https://ga4-insights-api-671647576749.us-central1.run.app/`
- **API Endpoint**: `https://ga4-insights-api-671647576749.us-central1.run.app/api/funnel-analysis`
- **Health Check**: `https://ga4-insights-api-671647576749.us-central1.run.app/api/health`

## 🔧 **Troubleshooting**

### **Common Issues**
1. **GA4 Permission Denied**: Check service account has GA4 access
2. **Property ID Wrong**: Verify in GA4 Admin → Property Settings
3. **API Quota Exceeded**: Check Google Cloud Console quotas
4. **N8N Credentials**: Re-authenticate OAuth tokens

### **Debug Steps**
1. Test GA4 node individually
2. Check API response format
3. Verify data structure matches expected format
4. Test AI insights endpoint with sample data

## 📊 **Expected Output**

Your workflow will generate:
- **Real GA4 data** from your property
- **AI-powered insights** with critical issues and opportunities
- **Interactive charts** showing funnel performance
- **Slack notification** with report link and key metrics

## 🎯 **Next Steps**

1. Set up the workflow
2. Test with your GA4 data
3. Customize the analysis dimensions
4. Schedule regular reports
5. Add more sophisticated filtering and alerts


