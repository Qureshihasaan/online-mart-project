# Aiven Kafka - Quick Reference Card

## 🚀 Quick Start Command

### Production (Aiven Cloud)
```bash
# Set Aiven credentials in .env first, then:
docker compose up -d
```

---

## 🔑 Required Environment Variables

### For Aiven (Production - Required)
```env
AIVEN_KAFKA_BOOTSTRAP_SERVER=your-service.aivencloud.com:12345
AIVEN_KAFKA_USERNAME=avnadmin
AIVEN_KAFKA_PASSWORD=your-password
AIVEN_SSL_CA_FILE=ca.pem  # Optional but recommended
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `kafka_config.py` | Shared Kafka configuration |
| `kafka_utils.py` | Helper utilities |
| `.env.example` | Template for environment variables |
| `AIVEN_KAFKA_SETUP.md` | Complete migration guide |
| `AIVEN_IMPLEMENTATION_SUMMARY.md` | Implementation details |
| `update_kafka_services.py` | Auto-update script |

---

## 🔍 Verification

### Check if Aiven Kafka is Configured
```bash
# Look for this in logs:
✓ Aiven Kafka configuration loaded (SASL_SSL)
```

### View Kafka Console
- **Aiven**: Aiven Console > Your Service > Topics

---

## 🛠️ Common Tasks

### Test Kafka Connection
```bash
# Create a product (triggers event)
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","price":9.99}'

# Check logs for event consumption
docker compose logs -f inventory_services
```

---

## 📊 Kafka Topics

| Topic | Purpose | Default Name |
|-------|---------|--------------|
| Products | Product events | `product-topic` |
| Inventory | Stock updates | `inventory-topic` |
| Users | User events | `user-topic` |
| Orders | Order events | `order-topic` |
| Payments | Payment events | `payment-topic` |
| Design | AI design events | `design-topic` |

---

## 🆘 Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Auth failed | Check username/password in .env |
| Connection timeout | Verify bootstrap server hostname:port |
| SSL error | Download ca.pem from Aiven Console |
| Configuration error | Ensure AIVEN_KAFKA_BOOTSTRAP_SERVER is set |

---

## 📚 Full Documentation

- **Setup Guide**: `AIVEN_KAFKA_SETUP.md`
- **Implementation**: `AIVEN_IMPLEMENTATION_SUMMARY.md`
- **Project README**: `README.md`

---

**Need Help?** See `AIVEN_KAFKA_SETUP.md` for comprehensive guide.
