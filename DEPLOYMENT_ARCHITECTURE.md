# 🏗️ Deployment Architecture - 2 Cloud Run Services

## 📊 **Complete System Architecture**

```
┌──────────────────────────────────────────────────────────────────────┐
│                           n8n Workflow                                │
│                        (Daily at 9 AM)                                │
└────────┬─────────────────────────────────────┬────────────────────────┘
         │                                     │
         │                                     │
         ▼                                     ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│  Cloud Run Service #1   │         │  Cloud Run Service #2   │
│  "AI Insights API"      │         │  "Report Generator"     │
│                         │         │                         │
│  /api/funnel-analysis   │         │  /api/generate-report   │
│  → Returns JSON         │         │  → Returns HTML         │
│  → Claude AI insights   │         │  → With visualizations  │
│  → Cached (24h)         │         │  → Hosted as web page   │
└─────────────────────────┘         └─────────────────────────┘
         │                                     │
         │                                     │
         ▼                                     ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│   n8n Data Table        │         │   Public URL            │
│   (Store insights)      │         │   (Shareable link)      │
└────────┬────────────────┘         └────────┬────────────────┘
         │                                     │
         │                                     │
         ▼                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     Slack Message                            │
│                                                              │
│  🎯 Daily Funnel Report - Oct 14, 2025                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                     │
│  📈 Overall: 1.32% conversion                                │
│  ⚠️  17 outliers detected                                    │
│                                                              │
│  🔴 Critical Issues:                                         │
│    1. Social: -52% vs baseline                               │
│    2. Mobile: -33% vs baseline                               │
│                                                              │
│  🟢 Opportunities:                                           │
│    1. Email: +82% vs baseline                                │
│    2. Desktop: +59% vs baseline                              │
│                                                              │
│  📊 View Full Report:                                        │
│     https://ga4-report-xxx.run.app/report/abc123           │
│     ↑ Click here for interactive visualizations             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 **Two Deployment URLs:**

### **Service 1: AI Insights API** (Private - n8n only)
```
URL: https://ga4-insights-api-xxx.run.app
Endpoints:
  POST /api/funnel-analysis
  GET /api/health

Purpose:
  - Generate AI insights
  - Return JSON data
  - Used by n8n workflow
  - Requires authentication

Usage in n8n:
  HTTP Request → Store in Data Table → Format Slack
```

### **Service 2: Report Generator** (Public - for clients)
```
URL: https://ga4-reports-xxx.run.app
Endpoints:
  GET /report/{report_id}
  POST /api/generate-report

Purpose:
  - Host interactive HTML reports
  - Shareable public links
  - Beautiful visualizations
  - No authentication (public viewing)

Usage:
  Slack/Email → Client clicks link → Views report in browser
```

---

## 🔗 **How Clients View Visualizations:**

### **Option A: Hosted Report URL (Recommended)**

**Flow:**
```
1. n8n calls AI Insights API → Gets JSON
2. n8n calls Report Generator → Passes JSON, gets report ID
3. n8n sends Slack message with link
4. Client clicks link → Opens interactive report
```

**Slack Message:**
```
🎯 Daily Funnel Report - Oct 14, 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Overall: 1.32% | Outliers: 17

🔴 Top Issue: Social -52%
🟢 Top Opportunity: Email +82%

📊 View Full Report (Interactive):
   https://ga4-reports-xxx.run.app/report/20251014-abc123
   
   ✨ Includes:
   • Performance dashboards
   • Funnel flow visualization
   • AI-generated recommendations
   • A/B test suggestions
```

**What Client Sees:**
1. Clicks link in Slack
2. Browser opens beautiful HTML report
3. Interactive Plotly charts (hover, zoom, download)
4. All AI insights formatted nicely
5. Can share link with team

---

### **Option B: Inline Images in Slack (Alternative)**

**Flow:**
```
1. n8n calls AI Insights API
2. n8n calls Report Generator → Gets PNG images
3. n8n uploads images to Slack
4. Images display inline in message
```

**Slack Message:**
```
🎯 Daily Funnel Report
[Inline image: funnel_dashboard.png]
[Inline image: performance_heatmap.png]

🔴 Critical: Social -52%
🟢 Opportunity: Email +82%
```

---

### **Option C: Embedded in Email (Alternative)**

**Flow:**
```
1. n8n calls Report Generator → Gets full HTML
2. n8n sends email with HTML body
3. Email contains embedded visualizations
```

---

## 🎯 **Recommended Architecture:**

### **Service 1: AI Insights API**
```python
# main_api.py (Current file)
# Endpoints:
#   POST /api/funnel-analysis → JSON with insights
#   GET /api/health → Health check

# Features:
✅ Claude AI integration
✅ Caching (24h)
✅ Batch processing
✅ Rate limiting (50 RPM)
✅ Storage optimization
```

### **Service 2: Report Generator**
```python
# report_server.py (NEW file to create)
# Endpoints:
#   POST /api/generate-report → Create & host report, return URL
#   GET /report/{id} → Serve HTML report
#   GET /api/reports → List all reports

# Features:
✅ Generate Plotly visualizations
✅ Host HTML reports
✅ Public URLs for sharing
✅ No authentication needed
✅ Auto-expire old reports (7 days)
```

---

## 📝 **n8n Workflow (Complete):**

```
┌──────────────────┐
│ 1. Schedule      │ Daily at 9 AM
│    Trigger       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. Get History   │ SELECT from Data Table (last 30 days)
│    from DB       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. Call AI       │ POST https://ga4-insights-api.run.app/api/funnel-analysis
│    Insights API  │ Body: { dimensions, historical_data }
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. Store Results │ INSERT into Data Table (use insights_optimized)
│    in Data Table │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. Generate      │ POST https://ga4-reports.run.app/api/generate-report
│    Report URL    │ Body: Pass JSON from step 3
│                  │ Returns: { "report_url": "https://..." }
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. Format Slack  │ Code node: Create message with insights + link
│    Message       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 7. Send to       │ Slack: #funnel-reports
│    Slack         │ Message includes clickable report link
└──────────────────┘
```

---

## 💬 **Slack Message Format (Code Node):**

```javascript
// n8n Code Node
const insightsResponse = $('Call AI Insights API').first().json;
const reportResponse = $('Generate Report URL').first().json;

const message = {
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🎯 GA4 Funnel Analysis Report"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": `*Overall Conversion:*\n${(insightsResponse.data.baseline_rates.overall_conversion * 100).toFixed(2)}%`
        },
        {
          "type": "mrkdwn",
          "text": `*Outliers Detected:*\n${insightsResponse.summary.total_outliers}`
        }
      ]
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*🔴 Top Critical Issue:*"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": `${insightsResponse.insights.critical_issues[0].value}: ${insightsResponse.insights.critical_issues[0].issue.substring(0, 150)}`
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*🟢 Top Opportunity:*"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": `${insightsResponse.insights.opportunities[0].value}: ${insightsResponse.insights.opportunities[0].opportunity.substring(0, 150)}`
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": `📊 *<${reportResponse.report_url}|View Full Interactive Report>*\n_Includes dashboards, heatmaps, and all AI recommendations_`
      }
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": `Generated by Claude Sonnet 4.5 | Cache: ${insightsResponse.summary.cache_used ? '✅ Used' : '🆕 Fresh'}`
        }
      ]
    }
  ]
};

return [{ json: message }];
```

---

## 🔐 **Authentication Strategy:**

### **Service 1: AI Insights API**
```
✅ Requires authentication (n8n only)
✅ Use Cloud Run IAM or API key
✅ Not public-facing
```

### **Service 2: Report Generator**
```
✅ Public URLs (anyone with link can view)
✅ No auth needed for viewing
✅ Report IDs are random/hard to guess
✅ Auto-expire after 7 days
```

---

## ⚠️ **Claude Rate Limits (Important!):**

```
Model: Claude Sonnet 4.x
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requests per Minute:  50 RPM
Input Tokens/Min:     30,000 TPM
Output Tokens/Min:    8,000 TPM (≤200k context)
```

### **Your Usage (Daily Schedule):**
```
Daily reports: 1 request/day
Actual usage: 
  - RPM: 1/1440 minutes = 0.0007 RPM ✅
  - Input: ~1,500 tokens/request
  - Output: ~2,000 tokens/request

You're using: 0.001% of limits ✅
```

### **With Caching:**
```
Same data requested twice:
  Request 1: Calls Claude (counted)
  Request 2: Returns cache (NOT counted) ✅
  
You can make 50 unique analyses per minute!
```

---

## 🚀 **Deployment Plan:**

### **Step 1: Deploy AI Insights API**
```bash
gcloud run deploy ga4-insights-api \
  --source . \
  --region us-central1 \
  --timeout 600s \
  --memory 1Gi \
  --project titanium-gadget-451710-i7 \
  --set-env-vars="ANTHROPIC_API_KEY=sk-ant-...,USE_MOCK_DATA=true" \
  --no-allow-unauthenticated

# Output: https://ga4-insights-api-xxx.run.app
```

### **Step 2: Deploy Report Generator**
```bash
gcloud run deploy ga4-report-generator \
  --source . \
  --region us-central1 \
  --timeout 300s \
  --memory 512Mi \
  --project titanium-gadget-451710-i7 \
  --allow-unauthenticated

# Output: https://ga4-report-generator-xxx.run.app
```

---

## 📧 **How Client Views Visualizations:**

### **Option 1: Click Link in Slack (Best UX)**

**What Happens:**
```
1. n8n generates report → Gets URL
2. Slack message sent with link
3. Client clicks link in Slack
4. Browser opens → Shows interactive dashboard
5. Client can:
   ✅ Interact with charts (hover, zoom)
   ✅ Download as PNG
   ✅ Share link with team
   ✅ Bookmark for later
```

**Slack Message:**
```
🎯 Daily Funnel Report
━━━━━━━━━━━━━━━━━━━━━━
📈 Overall: 1.32%
🔴 Top Issue: Social -52%
🟢 Top Opportunity: Email +82%

📊 View Full Report (Interactive):
   https://ga4-reports.run.app/report/20251014-abc123
   ↑ Click here to view dashboards
```

---

### **Option 2: Embedded Images in Slack**

**What Happens:**
```
1. n8n generates PNG images
2. Uploads to Slack
3. Images display inline
4. No external link needed
```

**Slack Message:**
```
🎯 Daily Funnel Report
[PNG Image displays here]
[PNG Image displays here]
```

**Pros/Cons:**
- ✅ No clicking needed
- ✅ Quick visual overview
- ❌ Not interactive
- ❌ Larger Slack message

---

### **Option 3: Email with Embedded Charts**

**What Happens:**
```
1. n8n gets HTML report
2. Sends as email body
3. Charts render in email client
```

---

## 🎯 **Recommended Flow (Best of Both Worlds):**

```
Daily Automated Report:
├─ Slack Summary (text + key metrics)
├─ Link to interactive report
└─ Optional: 1-2 key charts as inline images

Weekly Deep Dive:
├─ Email with full HTML report
├─ All visualizations embedded
└─ Complete AI recommendations
```

---

## 📝 **Complete n8n Workflow Code:**

### **Node 1: Schedule Trigger**
```
Cron: 0 9 * * *  (Daily at 9 AM)
```

### **Node 2: Get Historical Data**
```javascript
// Data Table - SELECT
SELECT * FROM funnel_insights 
WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY date DESC
```

### **Node 3: Call AI Insights API**
```javascript
// HTTP Request
{
  "method": "POST",
  "url": "https://ga4-insights-api-xxx.run.app/api/funnel-analysis",
  "authentication": "serviceAccount",  // GCP IAM
  "body": {
    "dimensions": [
      "sessionDefaultChannelGroup",
      "deviceCategory", 
      "browser",
      "screenResolution",
      "itemName",
      "itemCategory"
    ],
    "historical_data": {{ $('Get Historical Data').all().map(i => i.json) }}
  }
}
```

### **Node 4: Store Optimized Data**
```javascript
// Code Node - Prepare for Storage
const response = $input.first().json;

// Use optimized insights (smaller size)
return response.insights_optimized.critical_issues.map(issue => ({
  json: {
    date: new Date().toISOString().split('T')[0],
    timestamp: new Date().toISOString(),
    dimension: issue.dimension,
    value: issue.value,
    issue: issue.issue,
    impact: issue.impact,
    cache_used: response.summary.cache_used
  }
}));

// Then → Data Table INSERT
```

### **Node 5: Generate Report URL**
```javascript
// HTTP Request
{
  "method": "POST",
  "url": "https://ga4-report-generator-xxx.run.app/api/generate-report",
  "body": {
    "analysis_data": {{ $('Call AI Insights API').first().json }},
    "expires_in_days": 7
  }
}

// Returns:
{
  "report_id": "20251014-abc123",
  "report_url": "https://ga4-report-generator-xxx.run.app/report/20251014-abc123",
  "expires_at": "2025-10-21T09:00:00Z"
}
```

### **Node 6: Format Slack Message**
```javascript
// Code Node
const insights = $('Call AI Insights API').first().json;
const reportInfo = $('Generate Report URL').first().json;

const message = {
  blocks: [
    {
      type: "header",
      text: {
        type: "plain_text",
        text: `🎯 GA4 Funnel Analysis - ${new Date().toLocaleDateString()}`
      }
    },
    {
      type: "section",
      fields: [
        {
          type: "mrkdwn",
          text: `*Overall Conversion:*\n${(insights.data.baseline_rates.overall_conversion * 100).toFixed(2)}%`
        },
        {
          type: "mrkdwn",
          text: `*Outliers Detected:*\n${insights.summary.total_outliers}`
        }
      ]
    },
    {
      type: "section",
      text: {
        type: "mrkdwn",
        text: `*🔴 Critical Issues (${insights.insights.critical_issues.length}):*`
      }
    }
  ]
};

// Add top 3 critical issues
insights.insights.critical_issues.slice(0, 3).forEach((issue, i) => {
  message.blocks.push({
    type: "section",
    text: {
      type: "mrkdwn",
      text: `${i+1}. *${issue.value}* (${issue.dimension}): ${issue.issue.substring(0, 100)}...`
    }
  });
});

// Add opportunities
message.blocks.push({
  type: "section",
  text: {
    type: "mrkdwn",
    text: `*🟢 Top Opportunities (${insights.insights.opportunities.length}):*`
  }
});

insights.insights.opportunities.slice(0, 2).forEach((opp, i) => {
  message.blocks.push({
    type: "section",
    text: {
      type: "mrkdwn",
      text: `${i+1}. *${opp.value}*: ${opp.opportunity.substring(0, 100)}...\n   📈 Lift: ${opp.potential_lift}`
    }
  });
});

// Add divider
message.blocks.push({ type: "divider" });

// ⭐ ADD THE REPORT LINK
message.blocks.push({
  type: "section",
  text: {
    type: "mrkdwn",
    text: `📊 *<${reportInfo.report_url}|View Full Interactive Report>*\n\n✨ Includes:\n• Performance dashboards across all 6 dimensions\n• Interactive funnel flow visualization\n• Complete AI recommendations\n• Suggested A/B tests\n\n_Report expires: ${new Date(reportInfo.expires_at).toLocaleDateString()}_`
  }
});

// Add footer
message.blocks.push({
  type: "context",
  elements: [
    {
      type: "mrkdwn",
      text: `Generated by Claude Sonnet 4.5 | Cache: ${insights.summary.cache_used ? '✅ Used (saved API call)' : '🆕 Fresh analysis'} | Storage: ${insights.storage_optimization.savings_percent}% optimized`
    }
  ]
});

return [{ json: message }];
```

### **Node 7: Send to Slack**
```javascript
// Slack Node
{
  "channel": "#funnel-reports",
  "text": "Daily GA4 Funnel Analysis Report",
  "blocks": {{ $json.blocks }}
}
```

---

## 🎨 **What Client Sees:**

### **In Slack:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 GA4 Funnel Analysis - Oct 14, 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Conversion: 1.32%  |  Outliers: 17

🔴 Critical Issues (5):
  1. Social (channel): Converts 52% below baseline...
  2. Tablet (device): Cart→Purchase catastrophically low...
  3. Mobile (device): Represents 43% of traffic but...

🟢 Top Opportunities (5):
  1. Email: Massively outperforms (+82%)...
  2. Desktop: Converts 59% above baseline...

📊 View Full Interactive Report
   ↓ Click below for dashboards & visualizations ↓
   
   https://ga4-reports.run.app/report/20251014-abc123
   
   ✨ Includes:
   • Performance dashboards across all 6 dimensions
   • Interactive funnel flow visualization
   • Complete AI recommendations
   • Suggested A/B tests
   
   Report expires: Oct 21, 2025

Generated by Claude Sonnet 4.5 | Cache: ✅ Used | Storage: 58.7% optimized
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### **When Client Clicks Link:**
→ Browser opens: Beautiful interactive dashboard
→ All Plotly charts (hover, zoom, download)
→ Full AI insights formatted nicely
→ Can share link with team

---

## 📊 **Storage Math (54 MB Limit):**

### **Scenario 1: Full Insights (Not Optimized)**
```
Size per day: 45 KB
54 MB / 45 KB = 1,200 days capacity
With 90-day rotation: 4.05 MB used (7.5%)
```

### **Scenario 2: Optimized Insights (✅ What We Built)**
```
Size per day: 12 KB
54 MB / 12 KB = 4,500 days capacity
With 90-day rotation: 1.08 MB used (2%) ✅
```

### **Scenario 3: Summary Only (Maximum Efficiency)**
```
Size per day: 2 KB  
54 MB / 2 KB = 27,000 days capacity
With 90-day rotation: 180 KB used (0.3%) ✅
```

**You're using Option 2 - Perfect balance!** 🎯

---

## 🎯 **Summary:**

**Q: "How will clients view visualizations?"**
- A: Click link in Slack → Opens hosted HTML report in browser

**Q: "How is link included in n8n workflow?"**
- A: Node 5 generates report URL → Node 6 formats Slack message with link

**Q: "Do we need 2 URLs?"**
- A: Yes, recommended:
  - URL 1: AI Insights API (private, for n8n)
  - URL 2: Report Generator (public, for client viewing)

**Q: "What about 54 MB storage?"**
- A: ✅ Optimized! Only uses 2% with 90-day retention

**Q: "What about rate limits?"**
- A: ✅ No problem! 1 call/day << 50 calls/minute limit

---

**Ready to create the Report Generator service (Service #2)?** 🚀


