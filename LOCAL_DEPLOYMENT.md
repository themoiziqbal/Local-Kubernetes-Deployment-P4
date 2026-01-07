# 🚀 Local Kubernetes Deployment Guide

Complete guide for deploying ChatbotTodoApp locally using Docker + Minikube + Helm

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Method 1: Kubernetes Manifests](#method-1-kubernetes-manifests)
4. [Method 2: Helm Chart](#method-2-helm-chart-recommended)
5. [Accessing the Application](#accessing-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Cleanup](#cleanup)

---

## Prerequisites

Ensure you have the following installed:

- ✅ Docker Desktop
- ✅ Minikube
- ✅ kubectl
- ✅ Helm (for Helm deployment)
- ✅ OpenAI API Key

**Verify installations:**

```bash
docker --version
minikube version
kubectl version --client
helm version
```

---

## Quick Start

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192
```

### 2. Configure Docker Environment

**Linux/macOS:**

```bash
eval $(minikube docker-env)
```

**Windows PowerShell:**

```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

### 3. Build Docker Image

```bash
cd ChatbotTodoApp
docker build -t chatbot-todo-app:1.0 .
```

Verify the image:

```bash
docker images | grep chatbot-todo-app
```

---

## Method 1: Kubernetes Manifests

### Step 1: Create Secret with OpenAI API Key

```bash
kubectl create secret generic chatbot-secrets \
  --from-literal=openai-api-key=YOUR_OPENAI_API_KEY_HERE
```

### Step 2: Deploy Application

```bash
# Deploy PVC for database storage
kubectl apply -f k8s/pvc.yaml

# Deploy the application
kubectl apply -f k8s/deployment.yaml

# Deploy the service
kubectl apply -f k8s/service.yaml
```

### Step 3: Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# Check PVC
kubectl get pvc
```

Wait until pods are in `Running` state:

```bash
kubectl wait --for=condition=Ready pod -l app=chatbot-todo-app --timeout=300s
```

### Step 4: Access Application

```bash
minikube service chatbot-todo-service
```

Or get the URL manually:

```bash
minikube ip
# Then open in browser: http://<MINIKUBE-IP>:30080
```

---

## Method 2: Helm Chart (Recommended)

### Step 1: Configure Values

Edit `helm/chatbot-todo-app/values.yaml` and update:

```yaml
openaiApiKey: "your-actual-openai-api-key-here"
```

**OR** pass it during installation (more secure):

### Step 2: Install with Helm

```bash
helm install chatbot-release ./helm/chatbot-todo-app \
  --set openaiApiKey=YOUR_OPENAI_API_KEY_HERE
```

### Step 3: Verify Installation

```bash
# Check Helm releases
helm list

# Check pods
kubectl get pods

# Check services
kubectl get svc
```

### Step 4: Access Application

```bash
minikube service chatbot-release
```

---

## Accessing the Application

### Option 1: Minikube Service Command

```bash
# For Kubernetes manifests deployment
minikube service chatbot-todo-service

# For Helm deployment
minikube service chatbot-release
```

This will automatically open the application in your default browser.

### Option 2: Manual Access

```bash
# Get Minikube IP
minikube ip

# Access in browser
http://<MINIKUBE-IP>:30080
```

### Option 3: Port Forwarding

```bash
# For Kubernetes manifests
kubectl port-forward svc/chatbot-todo-service 8000:8000

# For Helm
kubectl port-forward svc/chatbot-release 8000:8000

# Access at: http://localhost:8000
```

---

## Viewing Logs

```bash
# Get pod name
kubectl get pods

# View logs
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -f <pod-name>

# View logs for all replicas
kubectl logs -l app=chatbot-todo-app --all-containers=true
```

---

## Updating the Application

### For Kubernetes Manifests:

```bash
# Rebuild image with new tag
docker build -t chatbot-todo-app:1.1 .

# Update deployment
kubectl set image deployment/chatbot-todo-app chatbot-todo-app=chatbot-todo-app:1.1

# Or apply updated manifest
kubectl apply -f k8s/deployment.yaml
```

### For Helm:

```bash
# Rebuild image
docker build -t chatbot-todo-app:1.1 .

# Update values.yaml with new tag
# Then upgrade
helm upgrade chatbot-release ./helm/chatbot-todo-app
```

---

## Scaling the Application

```bash
# Scale to 3 replicas
kubectl scale deployment chatbot-todo-app --replicas=3

# Verify
kubectl get pods
```

---

## Troubleshooting

### Issue 1: ImagePullBackOff

**Cause:** Kubernetes can't find the Docker image

**Solution:**

```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)  # Linux/macOS

# Rebuild image
docker build -t chatbot-todo-app:1.0 .

# Verify imagePullPolicy is set to Never
kubectl get deployment chatbot-todo-app -o yaml | grep imagePullPolicy
```

### Issue 2: CrashLoopBackOff

**Cause:** Application is crashing

**Solution:**

```bash
# Check logs
kubectl logs <pod-name>

# Describe pod for more details
kubectl describe pod <pod-name>

# Common causes:
# - Missing OpenAI API key
# - Port already in use
# - Missing dependencies
```

### Issue 3: Pods Pending

**Cause:** Insufficient resources or PVC not bound

**Solution:**

```bash
# Check PVC status
kubectl get pvc

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check Minikube resources
minikube status
```

### Issue 4: Service Not Accessible

**Solution:**

```bash
# Check service
kubectl get svc chatbot-todo-service

# Check endpoints
kubectl get endpoints chatbot-todo-service

# Restart minikube tunnel
minikube service chatbot-todo-service --url
```

### Issue 5: Database Persistence Not Working

**Solution:**

```bash
# Check PVC
kubectl get pvc chatbot-data-pvc

# Check if volume is mounted
kubectl describe pod <pod-name> | grep -A 5 Volumes

# Recreate PVC if needed
kubectl delete pvc chatbot-data-pvc
kubectl apply -f k8s/pvc.yaml
```

---

## Cleanup

### Remove Helm Deployment:

```bash
helm uninstall chatbot-release
kubectl delete pvc chatbot-release-pvc
```

### Remove Kubernetes Manifests:

```bash
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/pvc.yaml
kubectl delete secret chatbot-secrets
```

### Stop Minikube:

```bash
minikube stop
```

### Delete Minikube Cluster (complete cleanup):

```bash
minikube delete
```

---

## Useful Commands

```bash
# Dashboard
minikube dashboard

# SSH into Minikube
minikube ssh

# Get cluster info
kubectl cluster-info

# Get all resources
kubectl get all

# Describe deployment
kubectl describe deployment chatbot-todo-app

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash

# View resource usage
kubectl top pods
kubectl top nodes
```

---

## Next Steps

1. ✅ Set up monitoring with Prometheus/Grafana
2. ✅ Configure ingress for domain access
3. ✅ Add CI/CD pipeline
4. ✅ Deploy to cloud (see CLOUD_DEPLOYMENT.md)

---

**Happy Local Deployment! 🎉**
