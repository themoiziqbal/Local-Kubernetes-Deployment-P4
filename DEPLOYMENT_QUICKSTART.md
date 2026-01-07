# ⚡ Deployment Quickstart Guide

Quick reference for deploying ChatbotTodoApp locally or on cloud.

---

## 📦 What's Included

This repository now includes complete deployment configurations for:

1. **Local Kubernetes** (Minikube + Docker)
2. **Cloud Deployment** (DigitalOcean DOKS + Kafka + Dapr)

---

## 📂 Project Structure

```
ChatbotTodoApp/
├── Dockerfile                      # Application container
├── requirements.txt                # Python dependencies
├── run_server.py                  # Application entry point
│
├── k8s/                           # Local Kubernetes manifests
│   ├── deployment.yaml            # App deployment
│   ├── service.yaml               # NodePort service
│   ├── pvc.yaml                   # Persistent volume claim
│   └── secret.yaml                # API key secret template
│
├── helm/                          # Helm chart for local deployment
│   └── chatbot-todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── pvc.yaml
│           ├── secret.yaml
│           └── _helpers.tpl
│
├── cloud/                         # Cloud deployment manifests
│   ├── deployment-cloud.yaml     # Production deployment with Dapr
│   ├── service-cloud.yaml        # LoadBalancer service
│   ├── pvc-cloud.yaml            # Cloud persistent volume
│   ├── hpa.yaml                  # Horizontal Pod Autoscaler
│   ├── ingress.yaml              # Ingress for domain/SSL
│   └── dapr/
│       ├── kafka-pubsub.yaml     # Kafka pub/sub component
│       └── redis-statestore.yaml # Redis state store
│
├── LOCAL_DEPLOYMENT.md            # Detailed local deployment guide
├── CLOUD_DEPLOYMENT.md            # Detailed cloud deployment guide
└── DEPLOYMENT_QUICKSTART.md       # This file
```

---

## 🚀 Local Deployment (5 Minutes)

### Prerequisites

```bash
docker --version
minikube version
kubectl version --client
helm version
```

### Option 1: Kubernetes Manifests

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Configure Docker environment
eval $(minikube docker-env)  # Linux/macOS
# OR
& minikube -p minikube docker-env --shell powershell | Invoke-Expression  # Windows

# 3. Build image
cd ChatbotTodoApp
docker build -t chatbot-todo-app:1.0 .

# 4. Create secret
kubectl create secret generic chatbot-secrets \
  --from-literal=openai-api-key=YOUR_API_KEY

# 5. Deploy
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 6. Access
minikube service chatbot-todo-service
```

### Option 2: Helm (Recommended)

```bash
# Steps 1-3 same as above

# 4. Install with Helm
helm install chatbot-release ./helm/chatbot-todo-app \
  --set openaiApiKey=YOUR_API_KEY

# 5. Access
minikube service chatbot-release
```

**Access URL:** `http://<MINIKUBE-IP>:30080`

---

## ☁️ Cloud Deployment (DigitalOcean)

### Prerequisites

```bash
doctl version
kubectl version --client
helm version
dapr version
```

### Quick Deploy

```bash
# 1. Create DOKS cluster
doctl kubernetes cluster create chatbot-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3"

# 2. Configure kubectl
doctl kubernetes cluster kubeconfig save <cluster-id>

# 3. Install Kafka (Strimzi)
helm repo add strimzi https://strimzi.io/charts/
kubectl create namespace kafka
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator -n kafka

# 4. Install Dapr
dapr init --kubernetes --wait

# 5. Install Redis
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis

# 6. Deploy Dapr components
kubectl apply -f cloud/dapr/

# 7. Build and push image
docker build -t registry.digitalocean.com/your-registry/chatbot-todo-app:1.0 .
docker push registry.digitalocean.com/your-registry/chatbot-todo-app:1.0

# 8. Create secrets
kubectl create secret generic chatbot-secrets \
  --from-literal=openai-api-key=YOUR_API_KEY

# 9. Deploy application
kubectl apply -f cloud/

# 10. Get Load Balancer IP
kubectl get svc chatbot-todo-service
```

**Access URL:** `http://<EXTERNAL-IP>`

---

## 📖 Detailed Guides

For step-by-step instructions with troubleshooting:

- **Local Deployment:** See [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md)
- **Cloud Deployment:** See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)

---

## 🔧 Common Commands

### Local Development

```bash
# View pods
kubectl get pods

# View logs
kubectl logs -l app=chatbot-todo-app

# Scale replicas
kubectl scale deployment chatbot-todo-app --replicas=3

# Update image
docker build -t chatbot-todo-app:1.1 .
kubectl set image deployment/chatbot-todo-app chatbot-todo-app=chatbot-todo-app:1.1

# Port forward
kubectl port-forward svc/chatbot-todo-service 8000:8000

# Access dashboard
minikube dashboard
```

### Cloud Deployment

```bash
# View Dapr dashboard
dapr dashboard -k

# Check HPA
kubectl get hpa

# View metrics
kubectl top pods
kubectl top nodes

# Check Dapr components
kubectl get components

# View Kafka topics
kubectl get kafkatopic -n kafka

# Scale manually
kubectl scale deployment chatbot-todo-app --replicas=5
```

---

## 🐛 Quick Troubleshooting

### ImagePullBackOff (Local)

```bash
eval $(minikube docker-env)
docker build -t chatbot-todo-app:1.0 .
kubectl delete pod -l app=chatbot-todo-app
```

### CrashLoopBackOff

```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
# Check: Missing API key, port conflicts, dependencies
```

### Service Not Accessible (Local)

```bash
minikube service chatbot-todo-service --url
# Use the provided URL
```

### Dapr Sidecar Not Injected

```bash
# Verify annotations in deployment
kubectl get deployment chatbot-todo-app -o yaml | grep dapr.io
```

---

## 🔑 Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

Optional:
- `PORT` - Application port (default: 8000)
- `ENVIRONMENT` - Environment name (production, staging, development)

---

## 📊 Resource Requirements

### Local (Minikube)

- CPU: 2 cores minimum (4 recommended)
- RAM: 4GB minimum (8GB recommended)
- Disk: 20GB free space

### Cloud (DigitalOcean)

- **Development:** 3x s-2vcpu-4gb nodes ($36/month)
- **Production:** 3-5x s-4vcpu-8gb nodes (auto-scaling)
- **Storage:** 5GB block storage per PVC

---

## 🎯 Next Steps

After deployment:

1. ✅ Configure monitoring (Prometheus/Grafana)
2. ✅ Set up domain and SSL
3. ✅ Configure CI/CD pipeline
4. ✅ Implement backup strategy
5. ✅ Set up alerting
6. ✅ Configure log aggregation

---

## 📞 Support

- **Issues:** Check detailed guides in LOCAL_DEPLOYMENT.md and CLOUD_DEPLOYMENT.md
- **Logs:** `kubectl logs <pod-name>`
- **Events:** `kubectl get events --sort-by='.lastTimestamp'`

---

**Happy Deploying! 🚀**
