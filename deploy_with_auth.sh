#!/bin/bash

# Deploy GA4 Analytics MCP with Authentication Support
# Usage: ./deploy_with_auth.sh YOUR_ANTHROPIC_API_KEY

set -e

ANTHROPIC_API_KEY=$1
PROJECT_ID="titanium-gadget-451710-i7"
SERVICE_NAME="ga4-ai-insights"
REGION="us-central1"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY is required"
    echo "Usage: ./deploy_with_auth.sh YOUR_ANTHROPIC_API_KEY"
    exit 1
fi

echo "🚀 Deploying GA4 Analytics MCP with Authentication Support"
echo "=========================================================="

# Check if required environment variables are set
echo "📋 Checking environment variables..."

if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo "⚠️  Warning: GOOGLE_CLIENT_ID not set"
    echo "   The service will use mock data only"
    echo "   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET for real GA4 access"
fi

if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "⚠️  Warning: GOOGLE_CLIENT_SECRET not set"
    echo "   The service will use mock data only"
fi

if [ -z "$GA4_PROPERTY_ID" ]; then
    echo "⚠️  Warning: GA4_PROPERTY_ID not set"
    echo "   Using default property ID"
    export GA4_PROPERTY_ID="123456789"
fi

# Set default values for missing variables
export USE_MOCK_DATA=${USE_MOCK_DATA:-"true"}
export GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI:-"https://ga4-ai-insights-671647576749.us-central1.run.app/auth/callback"}

echo "✅ Environment variables configured"

# Build and deploy
echo "🏗️  Building Docker image..."

gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --project=$PROJECT_ID

echo "🚀 Deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --set-env-vars "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
    --set-env-vars "USE_MOCK_DATA=$USE_MOCK_DATA" \
    --set-env-vars "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" \
    --set-env-vars "GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET" \
    --set-env-vars "GA4_PROPERTY_ID=$GA4_PROPERTY_ID" \
    --set-env-vars "GOOGLE_REDIRECT_URI=$GOOGLE_REDIRECT_URI" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --max-instances 10

echo "✅ Deployment complete!"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo ""
echo "🎯 Service deployed successfully!"
echo "   URL: $SERVICE_URL"
echo ""
echo "📋 Next Steps:"
echo "1. Test the service:"
echo "   curl $SERVICE_URL/api/health"
echo ""
echo "2. If using mock data (default):"
echo "   curl -X POST $SERVICE_URL/api/funnel-analysis \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"use_mock_data\": true}'"
echo ""
echo "3. If setting up GA4 authentication:"
echo "   curl $SERVICE_URL/api/ga4/auth/url"
echo "   Follow the OAuth flow to authenticate"
echo ""
echo "4. Test with real GA4 data:"
echo "   curl -X POST $SERVICE_URL/api/funnel-analysis \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"use_mock_data\": false}'"
echo ""
echo "📖 For detailed setup instructions, see GA4_AUTH_SETUP_GUIDE.md"

