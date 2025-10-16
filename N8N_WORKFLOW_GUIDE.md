# 📊 n8n Workflow Guide - GA4 Funnel Analysis with Visualizations

## 🎯 **The Question: "Will n8n return the HTML report?"**

**Answer:** Not automatically, but you have 3 options:

---

## ✅ **Option 1: API Returns JSON → n8n Formats (Recommended)**

### **Workflow:**
```
┌─────────────────┐
│ 1. Schedule     │  Daily at 9 AM
│    Trigger      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Call API     │  POST /api/funnel-analysis
│                 │  → Returns JSON with data + AI insights
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Format       │  Code node: Create Slack message
│    Message      │  with key metrics & insights
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Send to      │  Slack: #funnel-reports
│    Slack        │  With formatted insights
└─────────────────┘
```

### **What Slack Receives:**
```
🎯 GA4 Funnel Analysis Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Baseline: 1.32% conversion

🔴 Critical Issues (3):
  1. Social: -52% vs baseline
  2. Tablet: -49% vs baseline  
  3. Mobile: -33% vs baseline

🟢 Opportunities (3):
  1. Email: +82% vs baseline
  2. Desktop: +59% vs baseline
  3. Product A: +58% vs baseline

💡 Top Recommendation:
  Fix tablet checkout → +5-6 purchases/month

🔗 View full report: [link to dashboard]
```

---

## ✅ **Option 2: API Returns HTML → n8n Emails It**

### **Workflow:**
```
┌─────────────────┐
│ 1. Schedule     │  Daily at 9 AM
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Call API     │  POST /api/generate-report
│                 │  → Returns complete HTML
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Email        │  Send HTML as email body
│    Report       │  with embedded charts
└─────────────────┘
```

### **New Endpoint Needed:**
```
POST /api/generate-report
→ Returns: Complete HTML with embedded Plotly charts
```

---

## ✅ **Option 3: n8n Generates Visualizations (Advanced)**

### **Workflow:**
```
┌─────────────────┐
│ 1. Call API     │  Get JSON data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Generate     │  Use n8n Code node with Chart.js
│    Charts       │  or call visualization service
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Email/Slack  │  Send with images
└─────────────────┘
```

---

## 🚀 **Recommended Approach (Hybrid)**

### **Daily Automated Report:**

```
┌─────────────────┐
│ Schedule        │  Every day at 9 AM
│ (Cron: 0 9 * * *)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Get Historical  │  Query n8n Data Table
│ Data            │  → Last 30 days of funnel data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Call Cloud Run  │  POST /api/funnel-analysis
│ API             │  Body: { dimensions: [...], historical_data: [...] }
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse Response  │  Extract: insights, outliers, recommendations
└────────┬────────┘
         │
         ├─────────────────────────┬─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Store in        │      │ Format Slack    │      │ Email Full      │
│ Data Table      │      │ Summary         │      │ HTML Report     │
└─────────────────┘      └────────┬────────┘      └────────┬────────┘
                                  │                         │
                                  ▼                         ▼
                         ┌─────────────────┐      ┌─────────────────┐
                         │ Send to Slack   │      │ Email to        │
                         │ #funnel-reports │      │ stakeholders    │
                         └─────────────────┘      └─────────────────┘
```

---

## 📝 **n8n Code Node Example: Format Slack Message**

```javascript
// Input: JSON from API
const data = $input.all()[0].json;

// Format Slack message
const blocks = [
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
        "text": `*Overall Conversion:*\n${(data.data.baseline_rates.overall_conversion * 100).toFixed(2)}%`
      },
      {
        "type": "mrkdwn",
        "text": `*Outliers:*\n${data.summary.total_outliers} detected`
      }
    ]
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*🔴 Critical Issues:*"
    }
  }
];

// Add critical issues
data.insights.critical_issues.slice(0, 3).forEach((issue, i) => {
  blocks.push({
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": `${i+1}. *${issue.value}* (${issue.dimension})\n   ${issue.issue}`
    }
  });
});

// Add opportunities
blocks.push({
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "*🟢 Top Opportunities:*"
  }
});

data.insights.opportunities.slice(0, 3).forEach((opp, i) => {
  blocks.push({
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": `${i+1}. *${opp.value}*: ${opp.opportunity}\n   📈 Lift: ${opp.potential_lift}`
    }
  });
});

// Add top recommendation
blocks.push({
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": `*💡 Priority #1:*\n${data.insights.recommendations[0].action}`
  }
});

return [{ json: { blocks } }];
```

---

## 📧 **n8n Code Node Example: Generate HTML Email**

```javascript
const data = $input.all()[0].json;

const html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .metric { background: #f0f0f0; padding: 15px; margin: 10px; border-radius: 5px; }
    .issue { background: #fee; border-left: 4px solid #e74c3c; padding: 10px; margin: 10px 0; }
    .opportunity { background: #efe; border-left: 4px solid #27ae60; padding: 10px; margin: 10px 0; }
  </style>
</head>
<body>
  <h1>🎯 GA4 Funnel Analysis Report</h1>
  
  <div class="metrics">
    <div class="metric">
      <h3>Overall Conversion</h3>
      <p>${(data.data.baseline_rates.overall_conversion * 100).toFixed(2)}%</p>
    </div>
  </div>
  
  <h2>🔴 Critical Issues</h2>
  ${data.insights.critical_issues.map(issue => `
    <div class="issue">
      <strong>${issue.value}</strong> (${issue.dimension})<br>
      ${issue.issue}
    </div>
  `).join('')}
  
  <h2>🟢 Opportunities</h2>
  ${data.insights.opportunities.map(opp => `
    <div class="opportunity">
      <strong>${opp.value}</strong><br>
      ${opp.opportunity}<br>
      <em>Potential Lift: ${opp.potential_lift}</em>
    </div>
  `).join('')}
  
  <p><a href="${process.env.DASHBOARD_URL}">View Full Dashboard</a></p>
</body>
</html>
`;

return [{ json: { html } }];
```

---

## 🎯 **Quick Answer to Your Question:**

**"Will n8n return the HTML report?"**

### **Current Setup:**
- ❌ No - API returns JSON only
- ✅ n8n formats the JSON into Slack/Email messages

### **To Get HTML Report in n8n:**

**Option A:** Use `/api/generate-report` endpoint (needs implementation)
```javascript
// n8n HTTP Request node
{
  "method": "POST",
  "url": "https://your-api.run.app/api/generate-report",
  "responseFormat": "text/html"
}
// Returns: Complete HTML report
```

**Option B:** Format in n8n (current approach)
```javascript
// n8n gets JSON → Code node formats it → Sends formatted message
```

---

## 📊 **What Each Approach Gives You:**

| Approach | Slack | Email | Visualizations | Effort |
|----------|-------|-------|----------------|--------|
| **JSON + n8n Format** | ✅ Formatted text | ✅ Simple HTML | ❌ No charts | Low |
| **HTML Endpoint** | ⚠️ Link only | ✅ Full report | ✅ Embedded charts | Medium |
| **n8n Charts** | ✅ Images | ✅ Images | ✅ Chart images | High |

---

## 🚀 **Recommended: Hybrid Approach**

1. **Daily Slack Summary** (JSON → formatted text)
   - Quick insights
   - Key metrics
   - Top 3 issues/opportunities

2. **Weekly Email Report** (HTML endpoint)
   - Complete analysis
   - All visualizations
   - Full recommendations

3. **On-Demand Dashboard** (hosted HTML)
   - Link in Slack/Email
   - Interactive exploration
   - Always up-to-date

---

## 📁 **Files You Have:**

- ✅ `client_report.html` - Complete report with charts
- ✅ `funnel_dashboard.html` - Interactive dashboard
- ✅ `funnel_dashboard.png` - Static image
- ✅ API endpoint - Returns JSON

**Next Step:** Choose which approach you want, and I'll help you set it up! 🎯


