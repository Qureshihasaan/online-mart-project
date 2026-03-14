@echo off
REM Azure Infrastructure Setup for Online Mart (Batch Version)
REM Run this ONCE manually before the GitHub Actions pipeline.

echo 🔐 Logging in to Azure...
az login

echo.
echo 📦 Creating Resource Group: onlinemart-rg
az group create --name onlinemart-rg --location eastus

echo.
echo 🐳 Creating Azure Container Registry: onlinemartcontainerregistry
az acr create --resource-group onlinemart-rg --name onlinemartcontainerregistry --sku Standard --admin-enabled true

echo.
echo 🔑 Fetching ACR credentials (save these as GitHub Secrets)...
for /f %%i in ('az acr credential show --name onlinemartcontainerregistry --query "username" -o tsv 2^>nul') do set ACR_USERNAME=%%i
for /f %%i in ('az acr credential show --name onlinemartcontainerregistry --query "passwords[0].value" -o tsv 2^>nul') do set ACR_PASSWORD=%%i
echo   ACR_USERNAME: %ACR_USERNAME%
echo   ACR_PASSWORD: %ACR_PASSWORD%

echo.
echo 🌐 Creating Container Apps Environment: onlinemart-env
az containerapp env create --name onlinemart-env --resource-group onlinemart-rg --location eastus

echo.
echo 📡 Creating Azure Event Hubs Namespace (Kafka-compatible)
az eventhubs namespace create --name onlinemartkafka --resource-group onlinemart-rg --location eastus --sku Standard

echo.
echo 📡 Creating Event Hub for product topic
az eventhubs eventhub create --name product-topic --namespace-name onlinemartkafka --resource-group onlinemart-rg --partition-count 3

echo.
echo 📡 Creating Event Hub for design topic
az eventhubs eventhub create --name design-topic --namespace-name onlinemartkafka --resource-group onlinemart-rg --partition-count 3

echo.
echo 📡 Creating Event Hub for inventory topic
az eventhubs eventhub create --name inventory-topic --namespace-name onlinemartkafka --resource-group onlinemart-rg --partition-count 3

echo.
echo 📡 Creating Event Hub for user topic
az eventhubs eventhub create --name user-topic --namespace-name onlinemartkafka --resource-group onlinemart-rg --partition-count 3

echo.
echo 📡 Creating Event Hub for order topic
az eventhubs eventhub create --name order-topic --namespace-name onlinemartkafka --resource-group onlinemart-rg --partition-count 3

echo.
echo 📡 Creating Event Hub for notification topic
az eventhubs eventhub create --name notification-topic --namespace-name onlinemartkafka --resource-group onlinemart-rg --partition-count 3

echo.
echo 📡 Creating Event Hub for payment topic
az eventhubs eventhub create --name payment-topic --namespace-name onlinemartkafka --resource-group onlinemart-rg --partition-count 3

echo.
echo 🔐 Creating Service Principal for GitHub Actions...
for /f %%i in ('az account show --query id -o tsv 2^>nul') do set SUBSCRIPTION_ID=%%i

REM Create Service Principal
for /f %%i in ('az ad sp create-for-rbac --name "onlinemart-github-actions" --role contributor --scopes "/subscriptions/%%SUBSCRIPTION_ID%%/resourceGroups/onlinemart-rg" --sdk-auth 2^>nul') do set SP_OUTPUT=%%i

echo.
echo 🐘 Creating PostgreSQL Flexible Server
az postgres flexible-server create --name onlinemartpostgres --resource-group onlinemart-rg --location eastus --admin-user postgres_admin --admin-password SecurePassword123! --sku-name Standard_B1ms --tier Burstable --public-access Disabled

echo.
echo 📋 Retrieving PostgreSQL connection details
for /f %%i in ('az postgres flexible-server show --name onlinemartpostgres --resource-group onlinemart-rg --query fullyQualifiedDomainName -o tsv 2^>nul') do set POSTGRES_FQDN=%%i
echo PostgreSQL FQDN: %POSTGRES_FQDN%

echo.
echo ✅ Done! Add these secrets to your GitHub repository:
echo    (Settings ^^^^^^^^^^ Secrets and variables ^^^^^^^^^^ Actions ^^^^^^^^^^ New repository secret)
echo.
echo ────────────────────────────────────────────────────────
echo Secret Name: AZURE_CREDENTIALS
echo Secret Value:
echo %SP_OUTPUT%
echo.
echo Secret Name: ACR_USERNAME
echo Secret Value: %ACR_USERNAME%
echo.
echo Secret Name: ACR_PASSWORD
echo Secret Value: %ACR_PASSWORD%
echo.
echo Secret Name: POSTGRES_ADMIN_USER
echo Secret Value: postgres_admin
echo.
echo Secret Name: POSTGRES_ADMIN_PASSWORD
echo Secret Value: SecurePassword123!
echo.
echo Secret Name: POSTGRES_FQDN
echo Secret Value: %POSTGRES_FQDN%
echo ────────────────────────────────────────────────────────
echo.
echo Additional secrets to configure in GitHub:
echo   - GEMINI_API_KEY: Your Google Gemini API key
echo   - PINECONE_API_KEY: Your Pinecone API key
echo   - PINECONE_INDEX_NAME: Your Pinecone index name
echo   - OPENROUTER_API_KEY: Your OpenRouter API key (if using)
echo   - GOOGLE_CLIENT_ID: Your Google OAuth client ID (if using)
echo   - SECRET_KEY: Your JWT secret key
echo   - ALGORITHMS: Your JWT algorithms (e.g., HS256)
echo.
echo After deployment, you'll need to set up individual Container App secrets for:
echo   - Database connection strings for each service
echo   - Kafka bootstrap server (Event Hubs connection string)
echo   - API keys for each service
echo.
echo Event Hubs Kafka endpoint will be: onlinemartkafka.servicebus.windows.net:9093