# 🚀 Step-by-Step Installation & Deployment Guide

**Follow these exact steps to deploy ChatbotTodoApp locally**

---

## Part 1: Install Prerequisites (One-time Setup)

### Step 1: Install Chocolatey (Package Manager)

1. **Right-click on PowerShell** and select **"Run as Administrator"**

2. **Run this command:**

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

3. **Wait for installation to complete** (1-2 minutes)

4. **Verify Chocolatey:**

```powershell
choco --version
```

Expected output: Version number (e.g., 2.2.2)

---

### Step 2: Install Docker Desktop

1. **Run this command:**

```powershell
choco install docker-desktop -y
```

2. **Wait for installation** (5-10 minutes)

3. **IMPORTANT: Restart your computer**

4. **After restart:**
   - Start Docker Desktop from Start Menu
   - Wait for Docker to fully start (whale icon in system tray should be steady)

5. **Verify Docker:**

```powershell
docker --version
```

Expected output: `Docker version 24.x.x`

---

### Step 3: Install kubectl

1. **Run this command:**

```powershell
choco install kubernetes-cli -y
```

2. **Wait for installation** (1-2 minutes)

3. **Close and reopen PowerShell**

4. **Verify kubectl:**

```powershell
kubectl version --client
```

Expected output: Client Version information

---

### Step 4: Install Minikube

1. **Run this command:**

```powershell
choco install minikube -y
```

2. **Wait for installation** (2-3 minutes)

3. **Close and reopen PowerShell**

4. **Verify Minikube:**

```powershell
minikube version
```

Expected output: `minikube version: v1.x.x`

---

### Step 5: Install Helm

1. **Run this command:**

```powershell
choco install kubernetes-helm -y
```

2. **Wait for installation** (1-2 minutes)

3. **Close and reopen PowerShell**

4. **Verify Helm:**

```powershell
helm version
```

Expected output: `version.BuildInfo{Version:"v3.x.x"...}`

---

### Step 6: Verify All Tools

**Run verification script:**

```powershell
cd ChatbotTodoApp
.\scripts\verify-prerequisites.ps1
```

**Expected output:**
```
✓ Docker is installed
✓ kubectl is installed
✓ Minikube is installed
✓ Helm is installed
All prerequisites are installed! ✓
```

---

## Part 2: Deploy Application

### Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

---

### Step 2: Deploy

**Open PowerShell in ChatbotTodoApp directory:**

```powershell
cd ChatbotTodoApp
.\scripts\deploy-local.ps1 -OpenAIApiKey "sk-YOUR-ACTUAL-KEY-HERE"
```

**Replace `sk-YOUR-ACTUAL-KEY-HERE` with your actual OpenAI API key**

---

### Step 3: Wait for Deployment

The script will:
1. ✅ Start Minikube (2-3 minutes)
2. ✅ Configure Docker environment
3. ✅ Build Docker image (2-3 minutes)
4. ✅ Deploy with Helm
5. ✅ Wait for pods to be ready (1-2 minutes)

**Total time: 5-10 minutes**

---

### Step 4: Access Application

**The script will show you the URL. Or run:**

```powershell
minikube service chatbot-release
```

This will automatically open your browser to the application!

**Alternative access methods:**

```powershell
# Get the URL
minikube ip
# Then visit: http://<IP>:30080

# Or use port forwarding
kubectl port-forward svc/chatbot-release 8000:8000
# Then visit: http://localhost:8000
```

---

## Part 3: Test Deployment

**Run the test script:**

```powershell
.\scripts\test-local-deployment.ps1
```

**Expected output:**
```
✓ Minikube is running
✓ Helm release found
✓ Pods running successfully
✓ Service exists
✓ PVC is Bound
✓ Secret exists
✓ HTTP endpoint is accessible
All Tests Passed! ✓
```

---

## Part 4: Use the Application

1. **Open the application URL** (from Step 4 above)

2. **Test creating a todo:**
   - Add a new task
   - Verify it appears in the list

3. **Test AI chatbot:**
   - Send a message
   - Verify AI responds

4. **Test persistence:**
   - Refresh the page
   - Todos should still be there

---

## Troubleshooting

### Issue 1: "Docker is not running"

**Solution:**
1. Start Docker Desktop application
2. Wait for it to fully start
3. Try deployment again

---

### Issue 2: "Minikube won't start"

**Solution:**

```powershell
# Delete and recreate
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker
```

---

### Issue 3: "ImagePullBackOff" error

**Solution:**

```powershell
# Reconfigure Docker environment
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Rebuild image
docker build -t chatbot-todo-app:1.0 .

# Delete failed pods (they'll recreate)
kubectl delete pod -l app.kubernetes.io/name=chatbot-todo-app
```

---

### Issue 4: "Can't access application"

**Solution:**

```powershell
# Check pod status
kubectl get pods

# If pods are running, try:
minikube service chatbot-release --url

# Use the URL shown
```

---

### Issue 5: "OpenAI API error"

**Solution:**
1. Check your API key is correct
2. Check you have credits in OpenAI account
3. Redeploy with correct key:

```powershell
helm upgrade chatbot-release ./helm/chatbot-todo-app --set openaiApiKey="sk-CORRECT-KEY"
```

---

## Useful Commands

```powershell
# View pods
kubectl get pods

# View logs
kubectl logs -l app.kubernetes.io/name=chatbot-todo-app

# View all resources
kubectl get all

# Open Kubernetes dashboard
minikube dashboard

# Stop Minikube (when done)
minikube stop

# Delete everything (cleanup)
.\scripts\cleanup-local.ps1
```

---

## Quick Command Reference

```powershell
# Deploy
.\scripts\deploy-local.ps1 -OpenAIApiKey "sk-xxx"

# Test
.\scripts\test-local-deployment.ps1

# Access
minikube service chatbot-release

# View logs
kubectl logs -l app.kubernetes.io/name=chatbot-todo-app

# Cleanup
.\scripts\cleanup-local.ps1
```

---

## Next Steps After Successful Deployment

1. ✅ Experiment with scaling:
   ```powershell
   kubectl scale deployment chatbot-release --replicas=3
   ```

2. ✅ Monitor resources:
   ```powershell
   kubectl top pods
   ```

3. ✅ View Kubernetes dashboard:
   ```powershell
   minikube dashboard
   ```

4. ✅ Try cloud deployment (see CLOUD_DEPLOYMENT.md)

---

**You're all set! 🎉**

If you encounter any issues, check the troubleshooting section above or refer to the detailed documentation files.
