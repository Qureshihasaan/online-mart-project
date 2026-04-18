# Aiven for Apache Kafka - Production Setup Guide

This guide will help you set up **Aiven for Apache Kafka** for production deployment.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step 1: Create Aiven Kafka Service](#step-1-create-aiven-kafka-service)
- [Step 2: Get Connection Credentials](#step-2-get-connection-credentials)
- [Step 3: Configure Your Application](#step-3-configure-your-application)
- [Step 4: Test the Connection](#step-4-test-the-connection)
- [Troubleshooting](#troubleshooting)

---

## Overview

Your application uses **Aiven Cloud Kafka** for production deployment with:
- **SASL_SSL encryption** for secure communication
- **Automatic configuration** based on environment variables
- **High availability** and managed service benefits

---

## Prerequisites

- [ ] Aiven account (sign up at https://aiven.io/)
- [ ] Aiven project created
- [ ] Docker & Docker Compose installed
- [ ] Your application code ready for deployment

---

## Step 1: Create Aiven Kafka Service

### Option A: Using Aiven Console

1. **Log in to Aiven Console**
   - Go to https://console.aiven.io/

2. **Create a New Service**
   - Click **"Create Service"**
   - Select **"Apache Kafka"**
   - Choose your cloud provider (AWS, GCP, or Azure)
   - Select a region close to your users

3. **Configure the Service**
   - **Service Name**: `online-mart-kafka` (or your preference)
   - **Plan**: Choose based on your needs:
     - `Startup-4`: Development/testing
     - `Business-4`: Production workloads
   - **Enable Kafka Connect**: Optional (if you need data integration)
   - **Enable Kafka REST API**: Optional (for HTTP access)

4. **Advanced Configuration** (if available)
   - Enable **Kafka Authentication**: ✅ Required
   - Enable **SSL/TLS**: ✅ Required (enabled by default)
   - Set retention policies as needed

5. **Click "Create Service"**
   - Wait for the service to start (usually 5-10 minutes)

### Option B: Using Aiven CLI

```bash
# Install Aiven CLI
pip install aiven-client

# Login
avn login

# Create Kafka service
avn service create \
  --service-type kafka \
  --plan startup-4 \
  --cloud google-europe-west3 \
  online-mart-kafka
```

---

## Step 2: Get Connection Credentials

### From Aiven Console

1. **Navigate to Your Kafka Service**
   - Go to your project > `online-mart-kafka`

2. **Find Connection Information**
   - Look for **"Connection Info"** or **"Service URI"** section
   - You'll need these values:

3. **Extract Credentials**
   ```
   Service URI format:
   https://avnadmin:PASSWORD@HOSTNAME:PORT
   ```

   You need:
   - **Bootstrap Server**: `HOSTNAME:PORT` (e.g., `online-mart-kafka-yourproject.aivencloud.com:12345`)
   - **Username**: `avnadmin` (or similar)
   - **Password**: The password from the URI

4. **Download CA Certificate** (Optional but recommended)
   - Go to **Service URI** tab
   - Download `ca.pem` certificate file
   - Save it to your project root: `D:\online-mart-project\ca.pem`

### Using Aiven CLI

```bash
# Get service details
avn service get online-mart-kafka

# Get connection URI
avn service get-connection-info online-mart-kafka
```

---

## Step 3: Configure Your Application

### 1. Copy the Example Environment File

```bash
cd D:\online-mart-project
copy .env.example .env
```

### 2. Edit `.env` File

Open `.env` and fill in the Aiven credentials:

```env
# ============================================
# AIVEN KAFKA CONFIGURATION (Required for Production)
# ============================================

# Aiven Kafka bootstrap server (format: hostname:port)
# Example: online-mart-kafka-yourproject.aivencloud.com:12345
AIVEN_KAFKA_BOOTSTRAP_SERVER=your-actual-bootstrap-server.aivencloud.com:12345

# Aiven Kafka authentication username
AIVEN_KAFKA_USERNAME=avnadmin

# Aiven Kafka authentication password
AIVEN_KAFKA_PASSWORD=your-actual-password

# SSL Certificate file path (optional)
# Only needed if you downloaded ca.pem
# AIVEN_SSL_CA_FILE=ca.pem
```

### 3. Verify Configuration

Ensure all Aiven Kafka credentials are correctly set in your `.env` file before deployment.

---

## Step 4: Test the Connection

### 1. Start the Services

```bash
docker compose up -d
```

### 2. Verify Kafka Connection

Check the service logs for successful connection:

```bash
docker compose logs -f product_services
```

You should see:
```
✓ Aiven Kafka configuration loaded (SASL_SSL)
✓ Kafka producer started successfully
```

### 3. Test with a Sample Request

```bash
# Create a test product to trigger a Kafka event
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Product","price":9.99,"description":"Test"}'
```

### 4. Verify Event Consumption

```bash
# Check inventory service logs for event consumption
docker compose logs -f inventory_services
```

---

## Troubleshooting

### Common Issues

#### 1. SASL Authentication Failed

**Error**: `SASL authentication failed: authentication failed`

**Solution**:
- Verify `AIVEN_KAFKA_USERNAME` and `AIVEN_KAFKA_PASSWORD` are correct
- Check for extra spaces or special characters in `.env`
- Test credentials by logging into Aiven Console

#### 2. SSL Certificate Verification Failed

**Error**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution**:
- Download `ca.pem` from Aiven Console
- Set `AIVEN_SSL_CA_FILE=ca.pem` in `.env`
- Or temporarily disable verification (not recommended for production):
  ```python
  "ssl_check_hostname": False
  ```

#### 3. Connection Timeout

**Error**: `Connection timed out` or `NoBrokersAvailable`

**Solution**:
- Verify `AIVEN_KAFKA_BOOTSTRAP_SERVER` hostname and port are correct
- Check firewall rules allow outbound connection to Aiven
- Test connection manually:
  ```bash
  telnet your-hostname.aivencloud.com 12345
  ```

#### 4. Topic Not Found

**Error**: `UnknownTopicOrPartition`

**Solution**:
- Topics are auto-created on first message by default
- Check Aiven Console > Topics to verify topic exists
- Manually create topics in Aiven Console if needed:
  - `product-topic`
  - `inventory-topic`
  - `order-topic`
  - `payment-topic`
  - `user-topic`
  - `design-topic`

---

## Production Checklist

Before deploying to production:

- [ ] Aiven Kafka service is running
- [ ] All credentials are set in `.env`
- [ ] SSL certificate is configured (optional but recommended)
- [ ] Topics are created (or auto-creation is enabled)
- [ ] Services are started with `docker compose up -d`
- [ ] Logs show successful SASL_SSL connection
- [ ] Test events are produced and consumed successfully
- [ ] Monitoring is set up in Aiven Console

---

## Additional Resources

- **Aiven Documentation**: https://docs.aiven.io/docs/products/kafka
- **Aiven Console**: https://console.aiven.io/
- **Quick Reference**: See `QUICK_REFERENCE.md` in project root
