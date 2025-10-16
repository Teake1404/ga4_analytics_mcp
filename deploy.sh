#!/bin/bash

# Deployment script for both GA4 Funnel Analysis services
# Service #1: AI Insights API
# Service #2: Report Generator

set -e

PROJECT_ID="titanium-gadget-451710-i7"
REGION="us-central1"
ANTHROPIC_KEY="$1"

if [ -z "$ANTHROPIC_KEY" ]; then
    echo "❌ Error: Anthropic API key required"
    echo "Usage: ./deploy.sh YOUR_ANTHROPIC_API_KEY"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🚀 Deploying GA4 Funnel Analysis Services              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# SERVICE #1: AI Insights API (Private)
# ============================================================================

echo "📝 Deploying Service #1: AI Insights API..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

gcloud run deploy ga4-insights-api \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --timeout 600s \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ANTHROPIC_API_KEY=$ANTHROPIC_KEY,USE_MOCK_DATA=true,LOG_LEVEL=INFO" \
  --no-allow-unauthenticated

INSIGHTS_URL=$(gcloud run services describe ga4-insights-api \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --format='value(status.url)')

echo ""
echo "✅ Service #1 deployed!"
echo "   URL: $INSIGHTS_URL"
echo "   Authentication: Required (n8n only)"
echo ""

# ============================================================================
# SERVICE #2: Report Generator (Public)
# ============================================================================

echo "📝 Deploying Service #2: Report Generator..."
echo ""

gcloud run deploy ga4-report-generator \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --timeout 300s \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars="LOG_LEVEL=INFO" \
  --allow-unauthenticated

REPORTS_URL=$(gcloud run services describe ga4-report-generator \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --format='value(status.url)')

echo ""
echo "✅ Service #2 deployed!"
echo "   URL: $REPORTS_URL"
echo "   Authentication: Public (anyone with link)"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║               ✅ DEPLOYMENT COMPLETE                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🔗 Your Service URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Service #1 (AI Insights API):"
echo "  $INSIGHTS_URL"
echo "  Use in n8n HTTP Request node"
echo ""
echo "Service #2 (Report Generator):"
echo "  $REPORTS_URL"
echo "  Returns shareable report URLs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo "  1. Save these URLs for n8n configuration"
echo "  2. Test: curl $INSIGHTS_URL/api/health"
echo "  3. Test: curl $REPORTS_URL/api/health"
echo "  4. Create n8n workflow using these URLs"
echo ""


