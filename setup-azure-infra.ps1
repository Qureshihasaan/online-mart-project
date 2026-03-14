# Azure Infrastructure Setup for Online Mart (PowerShell Version)
# Run this ONCE manually before the GitHub Actions pipeline.

# ── CONFIGURE THESE ──────────────────────────────────────────
$RESOURCE_GROUP = "onlinemart-rg"
$LOCATION = "eastus"
$ACR_NAME = "onlinemartcontainerregistry"  # Must be globally unique, lowercase
$ENVIRONMENT_NAME = "onlinemart-env"
$POSTGRES_ADMIN_USER = "postgres_admin"
$POSTGRES_ADMIN_PASSWORD = "SecurePassword123!"  # Use a strong password in production
# ─────────────────────────────────────────────────────────────

Write-Host "🔐 Logging in to Azure..." -ForegroundColor Green
az login

Write-Host ""
Write-Host "📦 Creating Resource Group: $RESOURCE_GROUP" -ForegroundColor Green
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION

Write-Host ""
Write-Host "🐳 Creating Azure Container Registry: $ACR_NAME" -ForegroundColor Green
az acr create `
  --resource-group $RESOURCE_GROUP `
  --name $ACR_NAME `
  --sku Standard `
  --admin-enabled true

Write-Host ""
Write-Host "🔑 Fetching ACR credentials (save these as GitHub Secrets)..." -ForegroundColor Green
$ACR_USERNAME = $(az acr credential show --name $ACR_NAME --query "username" -o tsv)
$ACR_PASSWORD = $(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
Write-Host "  ACR_USERNAME: $ACR_USERNAME"
Write-Host "  ACR_PASSWORD: $ACR_PASSWORD"

Write-Host ""
Write-Host "🌐 Creating Container Apps Environment: $ENVIRONMENT_NAME" -ForegroundColor Green
az containerapp env create `
  --name $ENVIRONMENT_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION

Write-Host ""
Write-Host "📡 Creating Azure Event Hubs Namespace (Kafka-compatible)" -ForegroundColor Green
$EVENTHUB_NAMESPACE = "onlinemartkafka"
az eventhubs namespace create `
  --name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Standard

Write-Host ""
Write-Host "📡 Creating Event Hub for product topic" -ForegroundColor Green
az eventhubs eventhub create `
  --name product-topic `
  --namespace-name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --partition-count 3 `
  --message-retention 1

Write-Host ""
Write-Host "📡 Creating Event Hub for design topic" -ForegroundColor Green
az eventhubs eventhub create `
  --name design-topic `
  --namespace-name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --partition-count 3 `
  --message-retention 1

Write-Host ""
Write-Host "📡 Creating Event Hub for inventory topic" -ForegroundColor Green
az eventhubs eventhub create `
  --name inventory-topic `
  --namespace-name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --partition-count 3 `
  --message-retention 1

Write-Host ""
Write-Host "📡 Creating Event Hub for user topic" -ForegroundColor Green
az eventhubs eventhub create `
  --name user-topic `
  --namespace-name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --partition-count 3 `
  --message-retention 1

Write-Host ""
Write-Host "📡 Creating Event Hub for order topic" -ForegroundColor Green
az eventhubs eventhub create `
  --name order-topic `
  --namespace-name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --partition-count 3 `
  --message-retention 1

Write-Host ""
Write-Host "📡 Creating Event Hub for notification topic" -ForegroundColor Green
az eventhubs eventhub create `
  --name notification-topic `
  --namespace-name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --partition-count 3 `
  --message-retention 1

Write-Host ""
Write-Host "📡 Creating Event Hub for payment topic" -ForegroundColor Green
az eventhubs eventhub create `
  --name payment-topic `
  --namespace-name $EVENTHUB_NAMESPACE `
  --resource-group $RESOURCE_GROUP `
  --partition-count 3 `
  --message-retention 1

Write-Host ""
Write-Host "🔐 Creating Service Principal for GitHub Actions..." -ForegroundColor Green
$SUBSCRIPTION_ID = $(az account show --query id -o tsv)
$SP_OUTPUT = $(az ad sp create-for-rbac `
  --name "onlinemart-github-actions" `
  --role contributor `
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" `
  --sdk-auth)

Write-Host ""
Write-Host "🐘 Creating PostgreSQL Flexible Server" -ForegroundColor Green
az postgres flexible-server create `
  --name onlinemartpostgres `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --admin-user $POSTGRES_ADMIN_USER `
  --admin-password $POSTGRES_ADMIN_PASSWORD `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --public-access none

Write-Host ""
Write-Host "📋 Retrieving PostgreSQL connection details" -ForegroundColor Green
$POSTGRES_FQDN = $(az postgres flexible-server show --name onlinemartpostgres --resource-group $RESOURCE_GROUP --query fullyQualifiedDomainName -o tsv)
Write-Host "PostgreSQL FQDN: $POSTGRES_FQDN"

Write-Host ""
Write-Host "✅ Done! Add these secrets to your GitHub repository:" -ForegroundColor Green
Write-Host "   (Settings → Secrets and variables → Actions → New repository secret)"
Write-Host ""
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host "Secret Name: AZURE_CREDENTIALS"
Write-Host "Secret Value:"
Write-Host $SP_OUTPUT
Write-Host ""
Write-Host "Secret Name: ACR_USERNAME"
Write-Host "Secret Value: $ACR_USERNAME"
Write-Host ""
Write-Host "Secret Name: ACR_PASSWORD"
Write-Host "Secret Value: $ACR_PASSWORD"
Write-Host ""
Write-Host "Secret Name: POSTGRES_ADMIN_USER"
Write-Host "Secret Value: $POSTGRES_ADMIN_USER"
Write-Host ""
Write-Host "Secret Name: POSTGRES_ADMIN_PASSWORD"
Write-Host "Secret Value: $POSTGRES_ADMIN_PASSWORD"
Write-Host ""
Write-Host "Secret Name: POSTGRES_FQDN"
Write-Host "Secret Value: $POSTGRES_FQDN"
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor Yellow
Write-Host ""
Write-Host "Additional secrets to configure in GitHub:"
Write-Host "  - GEMINI_API_KEY: Your Google Gemini API key"
Write-Host "  - PINECONE_API_KEY: Your Pinecone API key"
Write-Host "  - PINECONE_INDEX_NAME: Your Pinecone index name"
Write-Host "  - OPENROUTER_API_KEY: Your OpenRouter API key (if using)"
Write-Host "  - GOOGLE_CLIENT_ID: Your Google OAuth client ID (if using)"
Write-Host "  - SECRET_KEY: Your JWT secret key"
Write-Host "  - ALGORITHMS: Your JWT algorithms (e.g., HS256)"
Write-Host ""
Write-Host "After deployment, you'll need to set up individual Container App secrets for:"
Write-Host "  - Database connection strings for each service"
Write-Host "  - Kafka bootstrap server (Event Hubs connection string)"
Write-Host "  - API keys for each service"
Write-Host ""
Write-Host "Event Hubs Kafka endpoint will be: $EVENTHUB_NAMESPACE.servicebus.windows.net:9093"