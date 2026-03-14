#!/bin/bash

# Script to prepare the project for Docker builds
# This ensures all necessary files are in place before building

set -e  # Exit on any error

echo "Preparing project for Docker builds..."

# Check if we're in the right directory
if [[ ! -f "compose.yaml" ]]; then
    echo "Error: This script must be run from the project root directory."
    exit 1
fi

# Validate that essential files exist in each service directory
SERVICES=("product_services" "inventory_services" "user_services" "order_services" "notification_services" "payment_services")

for service in "${SERVICES[@]}"; do
    if [[ ! -d "$service" ]]; then
        echo "Error: Service directory '$service' does not exist."
        exit 1
    fi

    if [[ ! -f "$service/Dockerfile" ]]; then
        echo "Error: Dockerfile does not exist in '$service' directory."
        exit 1
    fi

    if [[ ! -f "$service/pyproject.toml" ]]; then
        echo "Error: pyproject.toml does not exist in '$service' directory."
        exit 1
    fi

    echo "✓ Verified $service directory"
done

# Check AI services
AI_SERVICES=(
    "ai_services/ai_chatbot"
    "ai_services/ai_design_generation_visualization"
)

for service in "${AI_SERVICES[@]}"; do
    if [[ ! -d "$service" ]]; then
        echo "Error: Service directory '$service' does not exist."
        exit 1
    fi

    if [[ ! -f "$service/Dockerfile" ]]; then
        echo "Error: Dockerfile does not exist in '$service' directory."
        exit 1
    fi

    if [[ ! -f "$service/pyproject.toml" ]]; then
        echo "Error: pyproject.toml does not exist in '$service' directory."
        exit 1
    fi

    echo "✓ Verified $service directory"
done

echo "All service directories validated successfully!"
echo "Ready for Docker builds."