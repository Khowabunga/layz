#!/bin/bash
# Deploy Layz to Cloud Run

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-layz}

echo "Deploying Layz to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"

# Build and push container
echo ""
echo "Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --min-instances 1 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo ""
echo "Deployed to: $SERVICE_URL"

# Deploy Cloud Scheduler jobs
echo ""
echo "Deploying Cloud Scheduler jobs..."

# Morning check-in
gcloud scheduler jobs create http layz-morning-checkin \
  --location $REGION \
  --schedule "0 7 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin" \
  --http-method POST \
  --oidc-service-account-email "$PROJECT_ID@appspot.gserviceaccount.com" \
  2>/dev/null || gcloud scheduler jobs update http layz-morning-checkin \
  --location $REGION \
  --schedule "0 7 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin"

# Evening check-in
gcloud scheduler jobs create http layz-evening-checkin \
  --location $REGION \
  --schedule "0 20 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin" \
  --http-method POST \
  --oidc-service-account-email "$PROJECT_ID@appspot.gserviceaccount.com" \
  2>/dev/null || gcloud scheduler jobs update http layz-evening-checkin \
  --location $REGION \
  --schedule "0 20 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin"

# Trigger checker (hourly)
gcloud scheduler jobs create http layz-trigger-check \
  --location $REGION \
  --schedule "0 * * * *" \
  --uri "$SERVICE_URL/cron/check-triggers" \
  --http-method POST \
  --oidc-service-account-email "$PROJECT_ID@appspot.gserviceaccount.com" \
  2>/dev/null || gcloud scheduler jobs update http layz-trigger-check \
  --location $REGION \
  --schedule "0 * * * *" \
  --uri "$SERVICE_URL/cron/check-triggers"

echo ""
echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Configure Twilio webhook: $SERVICE_URL/webhook/sms"
echo "  2. Configure Twilio voice webhook: $SERVICE_URL/webhook/voice/incoming"
