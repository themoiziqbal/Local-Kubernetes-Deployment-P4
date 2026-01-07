#!/bin/bash
# Cloud Deployment Script for DigitalOcean DOKS
# Deploys ChatbotTodoApp with Kafka and Dapr

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check required arguments
if [ $# -lt 3 ]; then
    echo -e "${RED}Error: Missing required arguments!${NC}"
    echo "Usage: ./scripts/deploy-cloud.sh CLUSTER_NAME REGISTRY_NAME OPENAI_API_KEY"
    echo "Example: ./scripts/deploy-cloud.sh chatbot-cluster chatbot-registry sk-xxxxx"
    exit 1
fi

CLUSTER_NAME=$1
REGISTRY_NAME=$2
OPENAI_API_KEY=$3
REGION=${4:-nyc1}

echo -e "${CYAN}========================================"
echo "Cloud Deployment to DigitalOcean DOKS"
echo -e "========================================${NC}"

# Prerequisites check
echo -e "\n${GREEN}Checking prerequisites...${NC}"
for cmd in doctl kubectl helm docker; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}✗ $cmd is not installed${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ $cmd is installed${NC}"
    fi
done

# Step 1: Create or connect to DOKS cluster
echo -e "\n${GREEN}Step 1: Setting up DOKS cluster...${NC}"
if doctl kubernetes cluster get $CLUSTER_NAME &> /dev/null; then
    echo -e "${YELLOW}Cluster '$CLUSTER_NAME' already exists. Using existing cluster.${NC}"
else
    echo -e "${YELLOW}Creating new cluster '$CLUSTER_NAME'...${NC}"
    doctl kubernetes cluster create $CLUSTER_NAME \
        --region $REGION \
        --version 1.28.2-do.0 \
        --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5"
fi

# Configure kubectl
echo -e "${GREEN}Configuring kubectl...${NC}"
doctl kubernetes cluster kubeconfig save $CLUSTER_NAME

# Verify connection
echo -e "${GREEN}Verifying cluster connection...${NC}"
kubectl cluster-info
kubectl get nodes

# Step 2: Create Container Registry
echo -e "\n${GREEN}Step 2: Setting up Container Registry...${NC}"
if doctl registry get $REGISTRY_NAME &> /dev/null; then
    echo -e "${YELLOW}Registry '$REGISTRY_NAME' already exists.${NC}"
else
    echo -e "${YELLOW}Creating registry '$REGISTRY_NAME'...${NC}"
    doctl registry create $REGISTRY_NAME
fi

# Login to registry
echo -e "${GREEN}Logging into registry...${NC}"
doctl registry login

# Step 3: Install Kafka with Strimzi
echo -e "\n${GREEN}Step 3: Installing Kafka (Strimzi)...${NC}"
helm repo add strimzi https://strimzi.io/charts/
helm repo update

kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

if helm list -n kafka | grep -q strimzi-kafka-operator; then
    echo -e "${YELLOW}Strimzi operator already installed${NC}"
else
    helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
        --namespace kafka \
        --set watchNamespaces="{kafka}"
fi

# Wait for operator to be ready
echo -e "${YELLOW}Waiting for Strimzi operator...${NC}"
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster
echo -e "${GREEN}Deploying Kafka cluster...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

echo -e "${YELLOW}Waiting for Kafka cluster to be ready (this may take 5-10 minutes)...${NC}"
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=600s -n kafka

# Create Kafka topic
echo -e "${GREEN}Creating Kafka topic...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: chatbot-events
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000
EOF

# Step 4: Install Dapr
echo -e "\n${GREEN}Step 4: Installing Dapr...${NC}"
if kubectl get namespace dapr-system &> /dev/null; then
    echo -e "${YELLOW}Dapr already installed${NC}"
else
    dapr init --kubernetes --wait
fi

dapr status -k

# Step 5: Install Redis for state store
echo -e "\n${GREEN}Step 5: Installing Redis...${NC}"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

if helm list | grep -q "^redis"; then
    echo -e "${YELLOW}Redis already installed${NC}"
else
    helm install redis bitnami/redis --namespace default
fi

# Get Redis password
echo -e "${GREEN}Getting Redis password...${NC}"
export REDIS_PASSWORD=$(kubectl get secret redis -o jsonpath="{.data.redis-password}" | base64 --decode)
echo "Redis password: $REDIS_PASSWORD"

# Step 6: Deploy Dapr components
echo -e "\n${GREEN}Step 6: Deploying Dapr components...${NC}"
kubectl apply -f cloud/dapr/kafka-pubsub.yaml
kubectl apply -f cloud/dapr/redis-statestore.yaml

# Verify components
kubectl get components

# Step 7: Build and push Docker image
echo -e "\n${GREEN}Step 7: Building and pushing Docker image...${NC}"
IMAGE_NAME="registry.digitalocean.com/${REGISTRY_NAME}/chatbot-todo-app:1.0"
echo -e "${YELLOW}Building image: $IMAGE_NAME${NC}"
docker build -t $IMAGE_NAME .
docker push $IMAGE_NAME

# Step 8: Create secrets
echo -e "\n${GREEN}Step 8: Creating secrets...${NC}"
kubectl create secret generic chatbot-secrets \
    --from-literal=openai-api-key=$OPENAI_API_KEY \
    --dry-run=client -o yaml | kubectl apply -f -

# Step 9: Update deployment manifest with image
echo -e "\n${GREEN}Step 9: Updating deployment manifest...${NC}"
sed -i.bak "s|registry.digitalocean.com/your-registry/chatbot-todo-app:1.0|$IMAGE_NAME|g" cloud/deployment-cloud.yaml

# Step 10: Deploy application
echo -e "\n${GREEN}Step 10: Deploying application...${NC}"
kubectl apply -f cloud/pvc-cloud.yaml
kubectl apply -f cloud/deployment-cloud.yaml
kubectl apply -f cloud/service-cloud.yaml
kubectl apply -f cloud/hpa.yaml

# Wait for deployment
echo -e "${YELLOW}Waiting for pods to be ready (this may take 3-5 minutes)...${NC}"
kubectl wait --for=condition=Ready pod -l app=chatbot-todo-app --timeout=300s

# Step 11: Get deployment status
echo -e "\n${GREEN}Step 11: Deployment Status...${NC}"
echo -e "\n${CYAN}Pods:${NC}"
kubectl get pods -l app=chatbot-todo-app

echo -e "\n${CYAN}Services:${NC}"
kubectl get svc chatbot-todo-service

echo -e "\n${CYAN}HPA:${NC}"
kubectl get hpa

echo -e "\n${CYAN}Dapr Components:${NC}"
kubectl get components

# Step 12: Get Load Balancer IP
echo -e "\n${GREEN}Step 12: Getting Load Balancer IP...${NC}"
echo -e "${YELLOW}Waiting for Load Balancer IP assignment...${NC}"
for i in {1..30}; do
    EXTERNAL_IP=$(kubectl get svc chatbot-todo-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ ! -z "$EXTERNAL_IP" ]; then
        break
    fi
    echo -n "."
    sleep 10
done
echo ""

if [ -z "$EXTERNAL_IP" ]; then
    echo -e "${RED}Warning: Load Balancer IP not assigned yet. Check manually with: kubectl get svc${NC}"
else
    echo -e "${GREEN}Load Balancer IP: $EXTERNAL_IP${NC}"
fi

# Summary
echo -e "\n${CYAN}========================================"
echo -e "${GREEN}Cloud Deployment Successful! ✓${NC}"
echo -e "${CYAN}========================================${NC}"

echo -e "\n${YELLOW}Application Access:${NC}"
if [ ! -z "$EXTERNAL_IP" ]; then
    echo -e "  ${GREEN}http://$EXTERNAL_IP${NC}"
else
    echo -e "  Run: ${CYAN}kubectl get svc chatbot-todo-service${NC}"
fi

echo -e "\n${YELLOW}Useful Commands:${NC}"
echo -e "  View pods: ${WHITE}kubectl get pods${NC}"
echo -e "  View logs: ${WHITE}kubectl logs -l app=chatbot-todo-app -c chatbot-todo-app${NC}"
echo -e "  View Dapr logs: ${WHITE}kubectl logs -l app=chatbot-todo-app -c daprd${NC}"
echo -e "  Dapr dashboard: ${WHITE}dapr dashboard -k${NC}"
echo -e "  Scale app: ${WHITE}kubectl scale deployment chatbot-todo-app --replicas=5${NC}"

echo -e "\n${YELLOW}Run test script:${NC}"
echo -e "  ${WHITE}./scripts/test-cloud-deployment.sh${NC}"

echo -e "\n${CYAN}========================================${NC}"
