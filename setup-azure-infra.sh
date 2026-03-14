#!/bin/bash
# =============================================================
# Enhanced Azure Infrastructure Setup for Online Mart
# Run this ONCE manually before the GitHub Actions pipeline.
# =============================================================

set -e

# ── CONFIGURE THESE ──────────────────────────────────────────
RESOURCE_GROUP="onlinemart-rg"
LOCATION="eastus"
ACR_NAME="onlinemartcontainerregistry"  # Must be globally unique, lowercase
ENVIRONMENT_NAME="onlinemart-env"
POSTGRES_ADMIN_USER="postgres_admin"
POSTGRES_ADMIN_PASSWORD="SecurePassword123!"  # Use a strong password in production
# ─────────────────────────────────────────────────────────────

echo "🔐 Logging in to Azure..."
az login

echo ""
echo "📦 Creating Resource Group: $RESOURCE_GROUP"
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

echo ""
echo "🐳 Creating Azure Container Registry: $ACR_NAME"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard \
  --admin-enabled true

echo ""
echo "🔑 Fetching ACR credentials (save these as GitHub Secrets)..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
echo "  ACR_USERNAME: $ACR_USERNAME"
echo "  ACR_PASSWORD: $ACR_PASSWORD"

echo ""
echo "🌐 Creating Container Apps Environment: $ENVIRONMENT_NAME"
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

echo ""
echo "📡 Creating Azure Event Hubs Namespace (Kafka-compatible)"
EVENTHUB_NAMESPACE="onlinemartkafka"
az eventhubs namespace create \
  --name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard

echo ""
echo "📡 Creating Event Hub for product topic"
az eventhubs eventhub create \
  --name product-topic \
  --namespace-name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --partition-count 3 \
  --message-retention 1

echo ""
echo "📡 Creating Event Hub for design topic"
az eventhubs eventhub create \
  --name design-topic \
  --namespace-name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --partition-count 3 \
  --message-retention 1

echo ""
echo "📡 Creating Event Hub for inventory topic"
az eventhubs eventhub create \
  --name inventory-topic \
  --namespace-name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --partition-count 3 \
  --message-retention 1

echo ""
echo "📡 Creating Event Hub for user topic"
az eventhubs eventhub create \
  --name user-topic \
  --namespace-name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --partition-count 3 \
  --message-retention 1

echo ""
echo "📡 Creating Event Hub for order topic"
az eventhubs eventhub create \
  --name order-topic \
  --namespace-name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --partition-count 3 \
  --message-retention 1

echo ""
echo "📡 Creating Event Hub for notification topic"
az eventhubs eventhub create \
  --name notification-topic \
  --namespace-name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --partition-count 3 \
  --message-retention 1

echo ""
echo "📡 Creating Event Hub for payment topic"
az eventhubs eventhub create \
  --name payment-topic \
  --namespace-name $EVENTHUB_NAMESPACE \
  --resource-group $RESOURCE_GROUP \
  --partition-count 3 \
  --message-retention 1

echo ""
echo "🔐 Creating Service Principal for GitHub Actions..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SP_OUTPUT=$(az ad sp create-for-rbac \
  --name "onlinemart-github-actions" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth)

echo ""
echo "🐘 Creating PostgreSQL Flexible Server"
az postgres flexible-server create \
  --name onlinemartpostgres \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $POSTGRES_ADMIN_USER \
  --admin-password $POSTGRES_ADMIN_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access none

echo ""
echo "📋 Retrieving PostgreSQL connection details"
POSTGRES_FQDN=$(az postgres flexible-server show --name onlinemartpostgres --resource-group $RESOURCE_GROUP --query fullyQualifiedDomainName -o tsv)
echo "PostgreSQL FQDN: $POSTGRES_FQDN"

echo ""
echo "✅ Done! Add these secrets to your GitHub repository:"
echo "   (Settings → Secrets and variables → Actions → New repository secret)"
echo ""
echo "────────────────────────────────────────────────────────"
echo "Secret Name: AZURE_CREDENTIALS"
echo "Secret Value:"
echo "$SP_OUTPUT"
echo ""
echo "Secret Name: ACR_USERNAME"
echo "Secret Value: $ACR_USERNAME"
echo ""
echo "Secret Name: ACR_PASSWORD"
echo "Secret Value: $ACR_PASSWORD"
echo ""
echo "Secret Name: POSTGRES_ADMIN_USER"
echo "Secret Value: $POSTGRES_ADMIN_USER"
echo ""
echo "Secret Name: POSTGRES_ADMIN_PASSWORD"
echo "Secret Value: $POSTGRES_ADMIN_PASSWORD"
echo ""
echo "Secret Name: POSTGRES_FQDN"
echo "Secret Value: $POSTGRES_FQDN"
echo "────────────────────────────────────────────────────────"
echo ""
echo "Additional secrets to configure in GitHub:"
echo "  - GEMINI_API_KEY: Your Google Gemini API key"
echo "  - PINECONE_API_KEY: Your Pinecone API key"
echo "  - PINECONE_INDEX_NAME: Your Pinecone index name"
echo "  - OPENROUTER_API_KEY: Your OpenRouter API key (if using)"
echo "  - GOOGLE_CLIENT_ID: Your Google OAuth client ID (if using)"
echo "  - SECRET_KEY: Your JWT secret key"
echo "  - ALGORITHMS: Your JWT algorithms (e.g., HS256)"
echo ""
echo "After deployment, you'll need to set up individual Container App secrets for:"
echo "  - Database connection strings for each service"
echo "  - Kafka bootstrap server (Event Hubs connection string)"
echo "  - API keys for each service"
echo ""
echo "Event Hubs Kafka endpoint will be: $EVENTHUB_NAMESPACE.servicebus.windows.net:9093"