# Deploying Online Mart Project to Azure Container Apps

This document provides a comprehensive guide to deploy your microservices-based online mart application to Azure Container Apps.

## Prerequisites

1. Azure CLI installed and configured
2. Docker installed locally
3. GitHub repository with the project code
4. Access to Azure subscription with appropriate permissions

## Architecture Overview

The application consists of multiple microservices:
- Product Services (port 8000)
- Inventory Services (port 8001)
- User Services (port 8002)
- Order Services (port 8003)
- Notification Services (port 8004)
- Payment Services (port 8005)
- AI Chatbot Services (port 8006)
- AI Design Visualization Services (port 8007)
- Apache Kafka broker (for inter-service communication)

## Deployment Steps

### Step 1: Run the Infrastructure Setup Script

The `setup-azure-infra.sh` script has already been created to set up the necessary Azure resources. Run it to create:

1. Resource Group
2. Azure Container Registry (ACR)
3. Container Apps Environment
4. Service Principal for GitHub Actions

```bash
chmod +x setup-azure-infra.sh
./setup-azure-infra.sh
```

### Step 2: Set Up External Dependencies

Before deploying to Azure, you need to set up external dependencies:

1. **Apache Kafka**: For production, use Azure Event Hubs with Kafka compatibility
2. **PostgreSQL Databases**: Use Azure Database for PostgreSQL for each service
3. **Pinecone**: For AI vector embeddings
4. **API Keys**: Store securely in Azure Key Vault or as Container App secrets

### Step 3: Container Images Configuration

Each service needs to be built and pushed to Azure Container Registry. The Dockerfiles are already configured for each service.

### Step 4: GitHub Actions Pipeline

Create a GitHub Actions workflow to build and deploy the services to Azure Container Apps.

---

## Updated Azure Infrastructure Setup Script

The following script enhances the existing setup with proper Kafka replacement for production and database configurations:

```bash
#!/bin/bash
# Enhanced Azure Infrastructure Setup for Online Mart
# Run this ONCE manually before the GitHub Actions pipeline.

set -e

# ── CONFIGURE THESE ──────────────────────────────────────────
RESOURCE_GROUP="onlinemart-rg"
LOCATION="eastus"
ACR_NAME="onlinemartacr"          # Must be globally unique, lowercase
ENVIRONMENT_NAME="onlinemart-env"
POSTGRES_ADMIN_USER="postgres_admin"
POSTGRES_ADMIN_PASSWORD="SecurePassword123!"  # Use a strong password
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
EVENTHUB_NAMESPACE="onlinemart-kafka"
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
  --name onlinemart-postgres \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $POSTGRES_ADMIN_USER \
  --admin-password $POSTGRES_ADMIN_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access none

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
echo "────────────────────────────────────────────────────────"
echo ""
echo "Additional secrets to configure in GitHub:"
echo "  - GEMINI_API_KEY: Your Google Gemini API key"
echo "  - PINECONE_API_KEY: Your Pinecone API key"
echo "  - PINECONE_INDEX_NAME: Your Pinecone index name"
echo "  - OPENROUTER_API_KEY: Your OpenRouter API key (if using)"
echo "  - GOOGLE_CLIENT_ID: Your Google OAuth client ID (if using)"
echo ""
echo "After deployment, you'll need to set up individual Container App secrets for:"
echo "  - Database connection strings for each service"
echo "  - Kafka bootstrap server (Event Hubs connection string)"
echo "  - API keys for each service"
```

## GitHub Actions Workflow

Create `.github/workflows/deploy-to-azure.yml`:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

env:
  ACR_NAME: ${{ secrets.ACR_NAME || 'onlinemartacr' }}
  RESOURCE_GROUP: ${{ secrets.RESOURCE_GROUP || 'onlinemart-rg' }}
  CONTAINERAPPS_ENVIRONMENT: ${{ secrets.ENVIRONMENT_NAME || 'onlinemart-env' }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Azure Container Registry
      run: |
        az login --service-principal -u ${{ secrets.AZURE_CLIENT_ID }} -p ${{ secrets.AZURE_CLIENT_SECRET }} --tenant ${{ secrets.AZURE_TENANT_ID }}
        az acr login --name ${{ env.ACR_NAME }}

    - name: Build and push Product Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/product-service:${{ github.sha }} ./product_services
        docker push ${{ env.ACR_NAME }}.azurecr.io/product-service:${{ github.sha }}

    - name: Build and push Inventory Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/inventory-service:${{ github.sha }} ./inventory_services
        docker push ${{ env.ACR_NAME }}.azurecr.io/inventory-service:${{ github.sha }}

    - name: Build and push User Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/user-service:${{ github.sha }} ./user_services
        docker push ${{ env.ACR_NAME }}.azurecr.io/user-service:${{ github.sha }}

    - name: Build and push Order Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/order-service:${{ github.sha }} ./order_services
        docker push ${{ env.ACR_NAME }}.azurecr.io/order-service:${{ github.sha }}

    - name: Build and push Notification Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/notification-service:${{ github.sha }} ./notification_services
        docker push ${{ env.ACR_NAME }}.azurecr.io/notification-service:${{ github.sha }}

    - name: Build and push Payment Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/payment-service:${{ github.sha }} ./payment_services
        docker push ${{ env.ACR_NAME }}.azurecr.io/payment-service:${{ github.sha }}

    - name: Build and push AI Chatbot Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/ai-chatbot-service:${{ github.sha }} ./ai_services/ai_chatbot
        docker push ${{ env.ACR_NAME }}.azurecr.io/ai-chatbot-service:${{ github.sha }}

    - name: Build and push AI Design Visualization Service
      run: |
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/ai-design-service:${{ github.sha }} ./ai_services/ai_design_generation_visualization
        docker push ${{ env.ACR_NAME }}.azurecr.io/ai-design-service:${{ github.sha }}

    - name: Deploy Product Service to Container Apps
      run: |
        az containerapp create \
          --name product-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/product-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            PRODUCT_SERVICE_DATABASE_URL="${{ secrets.PRODUCT_SERVICE_DATABASE_URL }}" \
            KAFKA_BOOTSTRAP_SERVER="${{ secrets.KAFKA_BOOTSTRAP_SERVER }}" \
            KAFKA_PRODUCT_TOPIC="product-topic" \
            KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT="product-group" \
            GEMINI_API_KEY="${{ secrets.GEMINI_API_KEY }}" \
            PINECONE_API_KEY="${{ secrets.PINECONE_API_KEY }}" \
            PINECONE_INDEX_NAME="${{ secrets.PINECONE_INDEX_NAME }}" \
            SECRET_KEY="${{ secrets.SECRET_KEY }}" \
            ALGORITHMS="${{ secrets.ALGORITHMS }}"

    - name: Deploy Inventory Service to Container Apps
      run: |
        az containerapp create \
          --name inventory-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/inventory-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            INVENTORY_SERVICE_DATABASE_URL="${{ secrets.INVENTORY_SERVICE_DATABASE_URL }}" \
            KAFKA_BOOTSTRAP_SERVER="${{ secrets.KAFKA_BOOTSTRAP_SERVER }}" \
            KAFKA_INVENTORY_TOPIC="inventory-topic" \
            KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY="inventory-group" \
            SECRET_KEY="${{ secrets.SECRET_KEY }}" \
            ALGORITHMS="${{ secrets.ALGORITHMS }}"

    - name: Deploy User Service to Container Apps
      run: |
        az containerapp create \
          --name user-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/user-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            USER_SERVICE_DATABASE_URL="${{ secrets.USER_SERVICE_DATABASE_URL }}" \
            KAFKA_BOOTSTRAP_SERVER="${{ secrets.KAFKA_BOOTSTRAP_SERVER }}" \
            KAFKA_USER_TOPIC="user-topic" \
            KAFKA_CONSUMER_GROUP_ID_FOR_USER="user-group" \
            SECRET_KEY="${{ secrets.SECRET_KEY }}" \
            ALGORITHMS="${{ secrets.ALGORITHMS }}" \
            GOOGLE_CLIENT_ID="${{ secrets.GOOGLE_CLIENT_ID }}"

    - name: Deploy Order Service to Container Apps
      run: |
        az containerapp create \
          --name order-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/order-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            ORDER_SERVICE_DATABASE_URL="${{ secrets.ORDER_SERVICE_DATABASE_URL }}" \
            KAFKA_BOOTSTRAP_SERVER="${{ secrets.KAFKA_BOOTSTRAP_SERVER }}" \
            KAFKA_ORDER_TOPIC="order-topic" \
            KAFKA_CONSUMER_GROUP_ID_FOR_ORDER="order-group" \
            SECRET_KEY="${{ secrets.SECRET_KEY }}" \
            ALGORITHMS="${{ secrets.ALGORITHMS }}"

    - name: Deploy Notification Service to Container Apps
      run: |
        az containerapp create \
          --name notification-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/notification-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            NOTIFICATION_SERVICE_DATABASE_URL="${{ secrets.NOTIFICATION_SERVICE_DATABASE_URL }}" \
            KAFKA_BOOTSTRAP_SERVER="${{ secrets.KAFKA_BOOTSTRAP_SERVER }}" \
            KAFKA_NOTIFICATION_TOPIC="notification-topic" \
            KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION="notification-group" \
            SECRET_KEY="${{ secrets.SECRET_KEY }}" \
            ALGORITHMS="${{ secrets.ALGORITHMS }}"

    - name: Deploy Payment Service to Container Apps
      run: |
        az containerapp create \
          --name payment-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/payment-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            PAYMENT_SERVICE_DATABASE_URL="${{ secrets.PAYMENT_SERVICE_DATABASE_URL }}" \
            KAFKA_BOOTSTRAP_SERVER="${{ secrets.KAFKA_BOOTSTRAP_SERVER }}" \
            KAFKA_PAYMENT_TOPIC="payment-topic" \
            KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT="payment-group" \
            SECRET_KEY="${{ secrets.SECRET_KEY }}" \
            ALGORITHMS="${{ secrets.ALGORITHMS }}"

    - name: Deploy AI Chatbot Service to Container Apps
      run: |
        az containerapp create \
          --name ai-chatbot-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/ai-chatbot-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            OPENROUTER_API_KEY="${{ secrets.OPENROUTER_API_KEY }}" \
            PINECONE_API_KEY="${{ secrets.PINECONE_API_KEY }}" \
            PINECONE_INDEX_NAME="${{ secrets.PINECONE_INDEX_NAME }}"

    - name: Deploy AI Design Visualization Service to Container Apps
      run: |
        az containerapp create \
          --name ai-design-service \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --environment ${{ env.CONTAINERAPPS_ENVIRONMENT }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/ai-design-service:${{ github.sha }} \
          --target-port 8000 \
          --ingress external \
          --registry-server ${{ env.ACR_NAME }}.azurecr.io \
          --registry-username ${{ secrets.ACR_USERNAME }} \
          --registry-password ${{ secrets.ACR_PASSWORD }} \
          --cpu 1.0 \
          --memory 2Gi \
          --env-vars \
            OPENROUTER_API_KEY="${{ secrets.OPENROUTER_API_KEY }}" \
            OPENROUTER_BASE_URL="${{ secrets.OPENROUTER_BASE_URL }}" \
            OPENROUTER_MODEL="${{ secrets.OPENROUTER_MODEL }}" \
            FLUX_IMAGE_MODEL="${{ secrets.FLUX_IMAGE_MODEL }}" \
            KAFKA_BOOTSTRAP_SERVER="${{ secrets.KAFKA_BOOTSTRAP_SERVER }}" \
            KAFKA_DESIGN_TOPIC="design-topic" \
            KAFKA_PRODUCT_TOPIC="product-topic" \
            KAFKA_CONSUMER_GROUP_ID="ai-design-group" \
            AI_CENTER_DATABASE_URL="${{ secrets.AI_CENTER_DATABASE_URL }}"
```

## Updating Dockerfiles for Production

For Azure Container Apps deployment, you'll need to modify the Dockerfiles to remove the `--reload` flag which is meant for development:

**Updated product_services/Dockerfile:**
```dockerfile
FROM python:3.12-slim

LABEL maintainer="hasaanqureshi"

WORKDIR /code

RUN  apt-get update && apt-get install -y\
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install uv

COPY pyproject.toml ./
COPY . .

RUN uv sync --frozen --no-install-project

EXPOSE 8000

# Production-ready command without --reload
CMD [ "uv", "run", "uvicorn", "product_services.main:app", "--host", "0.0.0.0", "--port", "8000" ]
```

## Configuration Changes Needed

### 1. Update Kafka Connection

Replace the local Kafka broker with Azure Event Hubs Kafka endpoint in your `.env` file:

```
# Replace localhost Kafka with Azure Event Hubs Kafka endpoint
KAFKA_BOOTSTRAP_SERVER=onlinemart-kafka.servicebus.windows.net:9093
```

### 2. Update Database Connections

Update your database connection strings to point to Azure PostgreSQL:

```
PRODUCT_SERVICE_DATABASE_URL=postgresql://username:password@onlinemart-postgres.postgres.database.azure.com:5432/products_db
INVENTORY_SERVICE_DATABASE_URL=postgresql://username:password@onlinemart-postgres.postgres.database.azure.com:5432/inventory_db
USER_SERVICE_DATABASE_URL=postgresql://username:password@onlinemart-postgres.postgres.database.azure.com:5432/users_db
ORDER_SERVICE_DATABASE_URL=postgresql://username:password@onlinemart-postgres.postgres.database.azure.com:5432/orders_db
NOTIFICATION_SERVICE_DATABASE_URL=postgresql://username:password@onlinemart-postgres.postgres.database.azure.com:5432/notifications_db
PAYMENT_SERVICE_DATABASE_URL=postgresql://username:password@onlinemart-postgres.postgres.database.azure.com:5432/payments_db
AI_CENTER_DATABASE_URL=postgresql://username:password@onlinemart-postgres.postgres.database.azure.com:5432/ai_center_db
```

## Deployment Process

1. **Run the infrastructure setup script** to create Azure resources
2. **Configure the secrets** in GitHub as mentioned in the script output
3. **Update your .env file** with production values
4. **Commit and push** your changes to trigger the GitHub Actions pipeline
5. **Monitor the deployment** in the GitHub Actions tab

## Post-Deployment Tasks

After successful deployment:

1. **Verify service connectivity** - Check that all services can connect to the databases and Kafka
2. **Test API endpoints** - Verify that each service is responding correctly
3. **Set up monitoring** - Configure Application Insights for monitoring
4. **Configure custom domains** - If needed, add custom domains to your Container Apps
5. **Set up autoscaling** - Configure scale rules based on demand

## Troubleshooting

- **Service connectivity issues**: Check that the Kafka and database connection strings are correct
- **Secrets not loading**: Verify that all required secrets are properly configured in GitHub
- **Container crashes**: Check the Container Apps logs in Azure portal
- **Network connectivity**: Ensure that your services can communicate with external dependencies