# Online Mart - Azure Container Apps Deployment Guide

This repository contains a microservices-based online mart application that can be deployed to Azure Container Apps.

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

All services communicate via Apache Kafka (replaced by Azure Event Hubs in production).

## Prerequisites

1. Azure CLI installed and configured
2. Docker installed locally
3. GitHub repository with the project code
4. Access to Azure subscription with appropriate permissions

## Deployment Steps

### Step 1: Run the Infrastructure Setup Script

Choose the appropriate script based on your environment:

**For Windows Command Prompt:**
```cmd
setup-azure-infra.bat
```

**For Windows PowerShell:**
```powershell
.\setup-azure-infra.ps1
```

**For Git Bash on Windows:**
```bash
bash setup-azure-infra.sh
```

This will create:
- Resource Group
- Azure Container Registry (ACR)
- Container Apps Environment
- Azure Event Hubs Namespace (for Kafka replacement)
- Event Hub topics for each service
- Azure Database for PostgreSQL Flexible Server
- Service Principal for GitHub Actions

### Step 2: Configure GitHub Secrets

After running the setup script, you'll receive output with values for GitHub secrets. Add these to your GitHub repository under Settings → Secrets and variables → Actions:

- `AZURE_CREDENTIALS`: Service Principal credentials
- `ACR_USERNAME`: Container registry username
- `ACR_PASSWORD`: Container registry password
- `POSTGRES_ADMIN_USER`: PostgreSQL admin username
- `POSTGRES_ADMIN_PASSWORD`: PostgreSQL admin password
- `POSTGRES_FQDN`: PostgreSQL fully qualified domain name
- `EVENTHUB_SHARED_ACCESS_KEY`: Event Hubs shared access key (you'll need to create this manually)
- `GEMINI_API_KEY`: Google Gemini API key
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_INDEX_NAME`: Pinecone index name
- `OPENROUTER_API_KEY`: OpenRouter API key (if using)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (if using)
- `SECRET_KEY`: JWT secret key
- `ALGORITHMS`: JWT algorithms (e.g., HS256)

### Step 3: Create Event Hubs Shared Access Policy

To get the Event Hubs shared access key, run:

```bash
az eventhubs namespace authorization-rule create \
  --resource-group onlinemart-rg \
  --namespace-name onlinemartkafka \
  --name RootManageSharedAccessKey \
  --rights Listen Send Manage
```

Then get the key:

```bash
az eventhubs namespace authorization-rule keys list \
  --resource-group onlinemart-rg \
  --namespace-name onlinemartkafka \
  --name RootManageSharedAccessKey
```

### Step 4: Push Code to GitHub

Push your code to the main branch to trigger the GitHub Actions pipeline:

```bash
git add .
git commit -m "Prepare for Azure deployment"
git push origin main
```

### Step 5: Monitor Deployment

Check the GitHub Actions tab in your repository to monitor the deployment progress.

## Post-Deployment

After successful deployment:

1. **Verify service connectivity** - Check that all services can connect to the databases and Kafka
2. **Test API endpoints** - Verify that each service is responding correctly
3. **Set up monitoring** - Configure Application Insights for monitoring
4. **Configure custom domains** - If needed, add custom domains to your Container Apps
5. **Set up autoscaling** - Configure scale rules based on demand

## Service URLs

Once deployed, each service will be accessible at:
- Product Service: `https://product-service.[region].azurecontainerapps.io`
- Inventory Service: `https://inventory-service.[region].azurecontainerapps.io`
- User Service: `https://user-service.[region].azurecontainerapps.io`
- Order Service: `https://order-service.[region].azurecontainerapps.io`
- Notification Service: `https://notification-service.[region].azurecontainerapps.io`
- Payment Service: `https://payment-service.[region].azurecontainerapps.io`
- AI Chatbot Service: `https://ai-chatbot-service.[region].azurecontainerapps.io`
- AI Design Service: `https://ai-design-service.[region].azurecontainerapps.io`

## Troubleshooting

- **Service connectivity issues**: Check that the Kafka and database connection strings are correct
- **Secrets not loading**: Verify that all required secrets are properly configured in GitHub
- **Container crashes**: Check the Container Apps logs in Azure portal
- **Network connectivity**: Ensure that your services can communicate with external dependencies

## Local Development vs. Production Differences

- **Kafka**: Local uses Apache Kafka, production uses Azure Event Hubs with Kafka compatibility
- **Databases**: Local uses local PostgreSQL instances, production uses Azure Database for PostgreSQL
- **Authentication**: Local development may use different authentication methods than production
- **Reload**: Local Dockerfiles include `--reload` for development, production Dockerfiles do not

## Scaling

Azure Container Apps provides automatic scaling based on demand. You can configure scale rules using the Azure CLI or portal:

```bash
az containerapp scale rule add \
  --name <service-name> \
  --resource-group onlinemart-rg \
  --trigger-type http \
  --rule-name http-scaling-rule \
  --http-concurrency 10
```