# ☁️ Cloud Deployment Guide - DigitalOcean DOKS

Complete guide for deploying ChatbotTodoApp on DigitalOcean Kubernetes with Kafka, Dapr, and production-ready setup.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: DigitalOcean Setup](#part-1-digitalocean-setup)
3. [Part 2: Kafka Installation](#part-2-kafka-installation)
4. [Part 3: Dapr Setup](#part-3-dapr-setup)
5. [Part 4: Application Deployment](#part-4-application-deployment)
6. [Part 5: Monitoring](#part-5-monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- ✅ doctl (DigitalOcean CLI)
- ✅ kubectl
- ✅ helm
- ✅ Dapr CLI
- ✅ Docker

### Required Accounts/Credentials

- DigitalOcean account with billing enabled
- DigitalOcean API token
- DigitalOcean Container Registry (or Docker Hub)
- OpenAI API key

---

## Part 1: DigitalOcean Setup

### 1.1 Install doctl

**macOS:**

```bash
brew install doctl
```

**Linux:**

```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-1.98.1-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
```

**Windows (PowerShell):**

```powershell
choco install doctl
```

### 1.2 Authenticate

```bash
doctl auth init
# Enter your API token when prompted
```

Verify:

```bash
doctl account get
```

### 1.3 Create DOKS Cluster

```bash
doctl kubernetes cluster create chatbot-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5"
```

**Wait for cluster creation** (~5-10 minutes)

### 1.4 Configure kubectl

```bash
# Get cluster ID
doctl kubernetes cluster list

# Configure kubectl
doctl kubernetes cluster kubeconfig save <cluster-id>

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### 1.5 Create Container Registry

```bash
# Create registry
doctl registry create chatbot-registry

# Login to registry
doctl registry login
```

---

## Part 2: Kafka Installation

### 2.1 Add Strimzi Helm Repository

```bash
helm repo add strimzi https://strimzi.io/charts/
helm repo update
```

### 2.2 Create Kafka Namespace

```bash
kubectl create namespace kafka
```

### 2.3 Install Strimzi Operator

```bash
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set watchNamespaces="{kafka}"
```

Verify:

```bash
kubectl get pods -n kafka
```

### 2.4 Deploy Kafka Cluster

Create `kafka-cluster.yaml`:

```yaml
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
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
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
```

Deploy:

```bash
kubectl apply -f kafka-cluster.yaml
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka
```

### 2.5 Create Kafka Topic

```bash
kubectl apply -f - <<EOF
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
```

---

## Part 3: Dapr Setup

### 3.1 Install Dapr CLI

**Linux/macOS:**

```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**Windows:**

```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### 3.2 Initialize Dapr on Kubernetes

```bash
dapr init --kubernetes --wait
```

Verify:

```bash
dapr status -k
kubectl get pods -n dapr-system
```

### 3.3 Install Redis for State Store

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis --namespace default
```

Get Redis password:

```bash
export REDIS_PASSWORD=$(kubectl get secret redis -o jsonpath="{.data.redis-password}" | base64 --decode)
echo $REDIS_PASSWORD
```

### 3.4 Deploy Dapr Components

```bash
# Deploy Kafka pub/sub component
kubectl apply -f cloud/dapr/kafka-pubsub.yaml

# Deploy Redis state store component
kubectl apply -f cloud/dapr/redis-statestore.yaml
```

Verify:

```bash
kubectl get components
```

---

## Part 4: Application Deployment

### 4.1 Build and Push Docker Image

```bash
cd ChatbotTodoApp

# Build image
docker build -t registry.digitalocean.com/chatbot-registry/chatbot-todo-app:1.0 .

# Push to registry
docker push registry.digitalocean.com/chatbot-registry/chatbot-todo-app:1.0
```

### 4.2 Create Secrets

```bash
# Create OpenAI API key secret
kubectl create secret generic chatbot-secrets \
  --from-literal=openai-api-key=YOUR_OPENAI_API_KEY_HERE
```

### 4.3 Update Cloud Manifests

Edit `cloud/deployment-cloud.yaml` and update the image:

```yaml
image: registry.digitalocean.com/chatbot-registry/chatbot-todo-app:1.0
```

### 4.4 Deploy Application

```bash
# Deploy PVC
kubectl apply -f cloud/pvc-cloud.yaml

# Deploy application with Dapr
kubectl apply -f cloud/deployment-cloud.yaml

# Deploy service with Load Balancer
kubectl apply -f cloud/service-cloud.yaml

# Deploy Horizontal Pod Autoscaler
kubectl apply -f cloud/hpa.yaml
```

### 4.5 Verify Deployment

```bash
# Check pods (should see both app and dapr sidecars)
kubectl get pods

# Check services
kubectl get svc

# Check HPA
kubectl get hpa

# View logs
kubectl logs -l app=chatbot-todo-app -c chatbot-todo-app
kubectl logs -l app=chatbot-todo-app -c daprd
```

### 4.6 Get Load Balancer IP

```bash
kubectl get svc chatbot-todo-service

# Wait for EXTERNAL-IP to be assigned
# Access your app at: http://<EXTERNAL-IP>
```

---

## Part 5: Monitoring

### 5.1 Install Prometheus and Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### 5.2 Access Grafana

```bash
# Get Grafana password
kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
echo

# Port forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access at: http://localhost:3000
# Username: admin
# Password: <password from above>
```

### 5.3 Access Dapr Dashboard

```bash
dapr dashboard -k -p 8080

# Access at: http://localhost:8080
```

---

## Optional: Domain and SSL Setup

### 1. Install cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 2. Create ClusterIssuer

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
```

### 3. Install NGINX Ingress

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### 4. Deploy Ingress

Edit `cloud/ingress.yaml` with your domain, then:

```bash
kubectl apply -f cloud/ingress.yaml
```

---

## Troubleshooting

### Check Dapr Sidecar Logs

```bash
kubectl logs <pod-name> -c daprd
```

### Check Kafka Status

```bash
kubectl get kafka -n kafka
kubectl describe kafka my-cluster -n kafka
```

### Test Kafka Connection

```bash
kubectl run kafka-test -ti --rm --restart=Never \
  --image=quay.io/strimzi/kafka:0.38.0-kafka-3.6.0 -n kafka \
  -- bin/kafka-broker-api-versions.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092
```

### Check Application Health

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=chatbot-todo-app -o jsonpath='{.items[0].metadata.name}')

# Check health endpoint
kubectl exec -it $POD_NAME -c chatbot-todo-app -- curl localhost:8000/
```

### View All Events

```bash
kubectl get events --sort-by='.lastTimestamp'
```

---

## Scaling and Performance

### Manual Scaling

```bash
kubectl scale deployment chatbot-todo-app --replicas=5
```

### Check HPA Status

```bash
kubectl get hpa
kubectl describe hpa chatbot-todo-app-hpa
```

### View Resource Usage

```bash
kubectl top nodes
kubectl top pods
```

---

## Backup and Disaster Recovery

### Backup Database

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=chatbot-todo-app -o jsonpath='{.items[0].metadata.name}')

# Copy database
kubectl cp $POD_NAME:/app/data/todos.db ./backup-$(date +%Y%m%d).db -c chatbot-todo-app
```

### Backup Kubernetes Resources

```bash
kubectl get all -o yaml > backup-resources.yaml
```

---

## Cleanup

```bash
# Delete application
kubectl delete -f cloud/

# Delete Dapr
dapr uninstall -k

# Delete Kafka
kubectl delete namespace kafka

# Delete Redis
helm uninstall redis

# Delete monitoring
helm uninstall prometheus -n monitoring

# Delete DOKS cluster
doctl kubernetes cluster delete chatbot-cluster
```

---

## Cost Optimization Tips

1. **Right-size your nodes:** Monitor usage and adjust node sizes
2. **Use autoscaling:** Let HPA manage replicas based on load
3. **Schedule non-critical workloads:** Use node affinity for batch jobs
4. **Clean up unused resources:** Regularly audit and remove
5. **Use DigitalOcean Snapshots:** For disaster recovery instead of always-on backups

---

## Production Checklist

- [ ] SSL/TLS configured
- [ ] Secrets properly managed
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] Autoscaling configured
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Logging aggregation set up
- [ ] Network policies defined
- [ ] RBAC configured
- [ ] CI/CD pipeline created

---

**Happy Cloud Deployment! ☁️🚀**
