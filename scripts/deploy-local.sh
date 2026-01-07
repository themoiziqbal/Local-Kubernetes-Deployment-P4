#!/bin/bash
# Local Kubernetes Deployment Script for Linux/macOS
# Deploys ChatbotTodoApp to local Minikube cluster using Helm

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if OpenAI API key is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: OpenAI API key is required!${NC}"
    echo "Usage: ./scripts/deploy-local.sh YOUR_OPENAI_API_KEY"
    exit 1
fi

OPENAI_API_KEY=$1

echo -e "${CYAN}========================================"
echo "Local Kubernetes Deployment"
echo -e "========================================${NC}"

# Step 1: Check Minikube status
echo -e "\n${GREEN}Step 1: Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo -e "${YELLOW}Minikube is not running. Starting Minikube...${NC}"
    minikube start --cpus=4 --memory=8192 --driver=docker
else
    echo -e "${GREEN}Minikube is already running!${NC}"
fi

# Step 2: Configure Docker environment
echo -e "\n${GREEN}Step 2: Configuring Docker environment...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}Docker environment configured!${NC}"

# Step 3: Build Docker image
echo -e "\n${GREEN}Step 3: Building Docker image...${NC}"
echo -e "${YELLOW}Building chatbot-todo-app:1.0...${NC}"
docker build -t chatbot-todo-app:1.0 .
echo -e "${GREEN}Docker image built successfully!${NC}"

# Step 4: Verify image
echo -e "\n${GREEN}Step 4: Verifying Docker image...${NC}"
docker images chatbot-todo-app:1.0

# Step 5: Deploy with Helm
echo -e "\n${GREEN}Step 5: Deploying with Helm...${NC}"
HELM_RELEASE="chatbot-release"

# Check if release already exists
if helm list -q | grep -q "^${HELM_RELEASE}$"; then
    echo -e "${YELLOW}Release '${HELM_RELEASE}' already exists. Upgrading...${NC}"
    helm upgrade $HELM_RELEASE ./helm/chatbot-todo-app --set openaiApiKey=$OPENAI_API_KEY
else
    echo -e "${YELLOW}Installing new release '${HELM_RELEASE}'...${NC}"
    helm install $HELM_RELEASE ./helm/chatbot-todo-app --set openaiApiKey=$OPENAI_API_KEY
fi

# Step 6: Wait for pods to be ready
echo -e "\n${GREEN}Step 6: Waiting for pods to be ready...${NC}"
echo -e "${YELLOW}This may take 2-3 minutes...${NC}"
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=chatbot-todo-app --timeout=300s

# Step 7: Get deployment status
echo -e "\n${GREEN}Step 7: Deployment Status...${NC}"
echo -e "\n${CYAN}Pods:${NC}"
kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app

echo -e "\n${CYAN}Services:${NC}"
kubectl get svc -l app.kubernetes.io/name=chatbot-todo-app

echo -e "\n${CYAN}Persistent Volume Claims:${NC}"
kubectl get pvc

# Step 8: Get service URL
echo -e "\n${CYAN}========================================"
echo -e "${GREEN}Deployment Successful! ✓${NC}"
echo -e "${CYAN}========================================${NC}"

echo -e "\n${YELLOW}Accessing the application...${NC}"
echo -e "${CYAN}Option 1: Run this command to open in browser:${NC}"
echo -e "  minikube service $HELM_RELEASE"

echo -e "\n${CYAN}Option 2: Get URL manually:${NC}"
MINIKUBE_IP=$(minikube ip)
echo -e "  http://${MINIKUBE_IP}:30080"

echo -e "\n${CYAN}Option 3: Port forwarding:${NC}"
echo -e "  kubectl port-forward svc/$HELM_RELEASE 8000:8000"
echo -e "  Then access: http://localhost:8000"

echo -e "\n${YELLOW}Useful Commands:${NC}"
echo -e "  View logs: kubectl logs -l app.kubernetes.io/name=chatbot-todo-app"
echo -e "  View pods: kubectl get pods"
echo -e "  Describe pod: kubectl describe pod <pod-name>"
echo -e "  Delete deployment: helm uninstall $HELM_RELEASE"

echo -e "\n${YELLOW}Run test script:${NC}"
echo -e "  ./scripts/test-local-deployment.sh"
