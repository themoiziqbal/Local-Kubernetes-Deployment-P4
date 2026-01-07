# 🚀 Complete Deployment Guide - ChatbotTodoApp

**Comprehensive guide from installation to deployment and testing**

---

## 📚 Quick Navigation

| Step | Description | Documentation |
|------|-------------|---------------|
| 1 | Install Prerequisites | [Below](#step-1-install-prerequisites) |
| 2 | Local Deployment | [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md) |
| 3 | Cloud Deployment | [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) |
| 4 | Testing | [TESTING_GUIDE.md](TESTING_GUIDE.md) |

---

## 🎯 Overview

This guide will help you deploy ChatbotTodoApp:

✅ **Locally** - Using Docker + Minikube + Helm (for development/testing)
✅ **Cloud** - Using DigitalOcean DOKS + Kafka + Dapr (for production)

---

## Step 1: Install Prerequisites

### Windows Users

**Option A: Automated Installation (Recommended)**

```powershell
# Run as Administrator
cd ChatbotTodoApp
.\scripts\install-prerequisites.ps1
```

**Option B: Manual Installation**

1. **Install Chocolatey** (Package Manager)

```powershell
# Run as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

2. **Install Docker Desktop**

```powershell
choco install docker-desktop -y
```

**Important:** Restart your computer after Docker Desktop installation

3. **Install kubectl**

```powershell
choco install kubernetes-cli -y
```

4. **Install Minikube**

```powershell
choco install minikube -y
```

5. **Install Helm**

```powershell
choco install kubernetes-helm -y
```

6. **Restart PowerShell**

Close and reopen PowerShell/Terminal

7. **Verify Installations**

```powershell
cd ChatbotTodoApp
.\scripts\verify-prerequisites.ps1
```

### Linux Users (Ubuntu/Debian)

```bash
# Update package list
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Logout and login again (for Docker group)
# Then verify
docker --version
kubectl version --client
minikube version
helm version
```

### macOS Users

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install all prerequisites
brew install docker
brew install kubectl
brew install minikube
brew install helm

# Verify
docker --version
kubectl version --client
minikube version
helm version
```

---

## Step 2: Local Deployment (5-10 Minutes)

### Quick Start

**Windows:**

```powershell
cd ChatbotTodoApp

# Deploy with your OpenAI API key
.\scripts\deploy-local.ps1 -OpenAIApiKey "sk-YOUR-API-KEY-HERE"
```

**Linux/macOS:**

```bash
cd ChatbotTodoApp
chmod +x scripts/*.sh

# Deploy with your OpenAI API key
./scripts/deploy-local.sh sk-YOUR-API-KEY-HERE
```

### What Happens During Deployment

1. ✅ Minikube starts (if not running)
2. ✅ Docker environment configured
3. ✅ Docker image built
4. ✅ Helm chart installed
5. ✅ Pods created and started
6. ✅ Service exposed

### Access Your Application

```bash
# Option 1: Auto-open in browser
minikube service chatbot-release

# Option 2: Get URL
minikube ip
# Then visit: http://<MINIKUBE-IP>:30080

# Option 3: Port forward
kubectl port-forward svc/chatbot-release 8000:8000
# Then visit: http://localhost:8000
```

### Test Local Deployment

**Windows:**

```powershell
.\scripts\test-local-deployment.ps1
```

**Linux/macOS:**

```bash
./scripts/test-local-deployment.sh
```

---

## Step 3: Cloud Deployment (30-45 Minutes)

### Prerequisites for Cloud

1. **DigitalOcean Account**
   - Sign up at https://www.digitalocean.com
   - Add payment method

2. **Create API Token**
   - Go to API section in DigitalOcean dashboard
   - Generate new token
   - Copy and save it securely

3. **Install doctl**

**Windows:**

```powershell
choco install doctl -y
```

**Linux:**

```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-1.98.1-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
```

**macOS:**

```bash
brew install doctl
```

4. **Authenticate doctl**

```bash
doctl auth init
# Enter your API token when prompted
```

5. **Install Dapr CLI**

**Linux/macOS:**

```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**Windows:**

```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### Cloud Deployment Steps

```bash
cd ChatbotTodoApp

# Run deployment script
./scripts/deploy-cloud.sh chatbot-cluster chatbot-registry sk-YOUR-API-KEY
```

**Parameters:**
- `chatbot-cluster` - Name for your Kubernetes cluster
- `chatbot-registry` - Name for your container registry
- `sk-YOUR-API-KEY` - Your OpenAI API key

### What Happens During Cloud Deployment

1. ✅ DOKS cluster created
2. ✅ kubectl configured
3. ✅ Container registry created
4. ✅ Kafka (Strimzi) installed
5. ✅ Dapr installed
6. ✅ Redis installed
7. ✅ Dapr components deployed
8. ✅ Docker image built and pushed
9. ✅ Application deployed
10. ✅ Load Balancer provisioned

### Access Cloud Application

```bash
# Get external IP
kubectl get svc chatbot-todo-service

# Access in browser
http://<EXTERNAL-IP>
```

### Test Cloud Deployment

```bash
./scripts/test-cloud-deployment.sh
```

---

## Step 4: Testing

See comprehensive testing guide: [TESTING_GUIDE.md](TESTING_GUIDE.md)

### Quick Tests

**Local:**

1. Access web interface
2. Create a new todo
3. Test AI chatbot
4. Refresh page (test persistence)
5. Delete a todo

**Cloud:**

All local tests plus:

6. Test autoscaling (generate load)
7. Test Dapr pub/sub
8. Test Dapr state store
9. Monitor with Dapr dashboard
10. Check Kafka messages

---

## 📁 Project Structure

```
ChatbotTodoApp/
├── scripts/                          # Deployment & testing scripts
│   ├── install-prerequisites.ps1     # Install tools (Windows)
│   ├── verify-prerequisites.ps1      # Verify installation
│   ├── deploy-local.ps1              # Local deployment (Windows)
│   ├── deploy-local.sh               # Local deployment (Linux/Mac)
│   ├── test-local-deployment.ps1     # Local tests (Windows)
│   ├── test-local-deployment.sh      # Local tests (Linux/Mac)
│   ├── deploy-cloud.sh               # Cloud deployment
│   ├── test-cloud-deployment.sh      # Cloud tests
│   └── cleanup-local.ps1             # Cleanup local resources
│
├── k8s/                              # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── pvc.yaml
│   └── secret.yaml
│
├── helm/                             # Helm chart
│   └── chatbot-todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── cloud/                            # Cloud-specific configs
│   ├── deployment-cloud.yaml
│   ├── service-cloud.yaml
│   ├── pvc-cloud.yaml
│   ├── hpa.yaml
│   ├── ingress.yaml
│   └── dapr/
│       ├── kafka-pubsub.yaml
│       └── redis-statestore.yaml
│
├── LOCAL_DEPLOYMENT.md               # Detailed local guide
├── CLOUD_DEPLOYMENT.md               # Detailed cloud guide
├── TESTING_GUIDE.md                  # Testing documentation
├── DEPLOYMENT_QUICKSTART.md          # Quick reference
└── COMPLETE_DEPLOYMENT_GUIDE.md      # This file
```

---

## 🔧 Common Commands

### Local Deployment

```bash
# View pods
kubectl get pods

# View logs
kubectl logs -l app.kubernetes.io/name=chatbot-todo-app

# Scale
kubectl scale deployment chatbot-release --replicas=3

# Port forward
kubectl port-forward svc/chatbot-release 8000:8000

# Dashboard
minikube dashboard

# Cleanup
helm uninstall chatbot-release
```

### Cloud Deployment

```bash
# View all resources
kubectl get all

# View Dapr components
kubectl get components

# Dapr dashboard
dapr dashboard -k -p 8080

# View HPA
kubectl get hpa

# Scale manually
kubectl scale deployment chatbot-todo-app --replicas=5

# View metrics
kubectl top pods
kubectl top nodes

# Check Kafka
kubectl get kafka -n kafka
kubectl get kafkatopic -n kafka
```

---

## 🐛 Troubleshooting

### Local Issues

| Issue | Solution |
|-------|----------|
| ImagePullBackOff | Ensure using Minikube's Docker: `eval $(minikube docker-env)` |
| CrashLoopBackOff | Check logs: `kubectl logs <pod-name>` |
| Service not accessible | Try: `minikube service chatbot-release` |
| Minikube won't start | Delete and recreate: `minikube delete && minikube start` |

### Cloud Issues

| Issue | Solution |
|-------|----------|
| Dapr sidecar not injected | Check annotations in deployment.yaml |
| Kafka not ready | Wait 5-10 minutes, check: `kubectl get kafka -n kafka` |
| Load Balancer pending | Normal, wait 2-3 minutes for IP assignment |
| High costs | Check node sizes, use autoscaling, cleanup when not needed |

---

## 💰 Cost Estimates

### Local Deployment

**Free** - Runs on your machine

**Requirements:**
- 4GB RAM
- 2 CPU cores
- 20GB disk space

### Cloud Deployment (DigitalOcean)

**Estimated Monthly Costs:**

| Component | Configuration | Cost/Month |
|-----------|--------------|------------|
| DOKS Nodes | 3x s-2vcpu-4gb | ~$36 |
| Block Storage | 3x 10GB (Kafka) | ~$3 |
| Block Storage | 3x 5GB (Zookeeper) | ~$1.50 |
| Block Storage | 1x 5GB (App) | ~$0.50 |
| Load Balancer | 1 LB | ~$12 |
| Container Registry | Basic | ~$5 |
| **Total** | | **~$58/month** |

**Cost Optimization:**
- Use smaller nodes for testing
- Delete cluster when not needed
- Use autoscaling to reduce idle costs
- Schedule non-critical workloads

---

## 🎓 Learning Path

### Beginner

1. ✅ Install prerequisites
2. ✅ Run local deployment
3. ✅ Access application
4. ✅ Run basic tests
5. ✅ View logs and pods

### Intermediate

1. ✅ Modify Helm values
2. ✅ Scale replicas
3. ✅ Test persistence
4. ✅ Deploy to cloud
5. ✅ Use Dapr dashboard

### Advanced

1. ✅ Configure Kafka topics
2. ✅ Implement custom Dapr components
3. ✅ Set up monitoring (Prometheus/Grafana)
4. ✅ Configure ingress with SSL
5. ✅ Implement CI/CD pipeline
6. ✅ Set up multi-region deployment

---

## 📞 Getting Help

### Check Logs

```bash
# Application logs
kubectl logs <pod-name>

# Dapr sidecar logs (cloud only)
kubectl logs <pod-name> -c daprd

# Previous pod logs (if crashed)
kubectl logs <pod-name> --previous

# Events
kubectl get events --sort-by='.lastTimestamp'
```

### Describe Resources

```bash
kubectl describe pod <pod-name>
kubectl describe deployment <deployment-name>
kubectl describe svc <service-name>
```

### Interactive Debugging

```bash
# Shell into pod
kubectl exec -it <pod-name> -- /bin/bash

# Run commands in pod
kubectl exec <pod-name> -- ls -la /app/data
```

---

## ✅ Pre-Deployment Checklist

### Local Deployment

- [ ] Docker Desktop installed and running
- [ ] Minikube installed
- [ ] kubectl installed
- [ ] Helm installed
- [ ] OpenAI API key ready
- [ ] At least 4GB free RAM
- [ ] At least 20GB free disk space

### Cloud Deployment

All local prerequisites plus:

- [ ] DigitalOcean account created
- [ ] Billing method added
- [ ] API token generated
- [ ] doctl installed and authenticated
- [ ] Dapr CLI installed
- [ ] Container registry access configured
- [ ] Budget allocated (~$60/month)

---

## 🚀 Quick Start Summary

**Fastest way to get started:**

1. **Install prerequisites**

```powershell
# Windows (as Admin)
.\scripts\install-prerequisites.ps1
```

2. **Deploy locally**

```powershell
# Windows
.\scripts\deploy-local.ps1 -OpenAIApiKey "sk-YOUR-KEY"
```

3. **Test**

```powershell
# Windows
.\scripts\test-local-deployment.ps1
```

4. **Access**

```bash
minikube service chatbot-release
```

**That's it! Your app is running locally.**

---

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [DigitalOcean Kubernetes](https://docs.digitalocean.com/products/kubernetes/)
- [Strimzi Kafka](https://strimzi.io/documentation/)

---

**Need more details? Check the specific guides:**

- 📘 [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md) - In-depth local deployment
- ☁️ [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) - Complete cloud setup
- 🧪 [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing
- ⚡ [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) - Quick reference

---

**Happy Deploying! 🎉**
