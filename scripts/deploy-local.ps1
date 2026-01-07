# Local Kubernetes Deployment Script
# Deploys ChatbotTodoApp to local Minikube cluster using Helm

param(
    [Parameter(Mandatory=$true)]
    [string]$OpenAIApiKey
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Local Kubernetes Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Check Minikube status
Write-Host "`nStep 1: Checking Minikube status..." -ForegroundColor Green
$minikubeStatus = minikube status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Minikube is not running. Starting Minikube..." -ForegroundColor Yellow
    minikube start --cpus=4 --memory=8192 --driver=docker
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to start Minikube!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Minikube is already running!" -ForegroundColor Green
}

# Step 2: Configure Docker environment
Write-Host "`nStep 2: Configuring Docker environment..." -ForegroundColor Green
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
Write-Host "Docker environment configured!" -ForegroundColor Green

# Step 3: Build Docker image
Write-Host "`nStep 3: Building Docker image..." -ForegroundColor Green
Write-Host "Building chatbot-todo-app:1.0..." -ForegroundColor Yellow
docker build -t chatbot-todo-app:1.0 .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build Docker image!" -ForegroundColor Red
    exit 1
}
Write-Host "Docker image built successfully!" -ForegroundColor Green

# Step 4: Verify image
Write-Host "`nStep 4: Verifying Docker image..." -ForegroundColor Green
docker images chatbot-todo-app:1.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "Image not found!" -ForegroundColor Red
    exit 1
}

# Step 5: Deploy with Helm
Write-Host "`nStep 5: Deploying with Helm..." -ForegroundColor Green
$helmRelease = "chatbot-release"

# Check if release already exists
$existingRelease = helm list -q | Select-String -Pattern "^$helmRelease$"
if ($existingRelease) {
    Write-Host "Release '$helmRelease' already exists. Upgrading..." -ForegroundColor Yellow
    helm upgrade $helmRelease ./helm/chatbot-todo-app --set openaiApiKey=$OpenAIApiKey
} else {
    Write-Host "Installing new release '$helmRelease'..." -ForegroundColor Yellow
    helm install $helmRelease ./helm/chatbot-todo-app --set openaiApiKey=$OpenAIApiKey
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Helm deployment failed!" -ForegroundColor Red
    exit 1
}

# Step 6: Wait for pods to be ready
Write-Host "`nStep 6: Waiting for pods to be ready..." -ForegroundColor Green
Write-Host "This may take 2-3 minutes..." -ForegroundColor Yellow
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=chatbot-todo-app --timeout=300s

# Step 7: Get deployment status
Write-Host "`nStep 7: Deployment Status..." -ForegroundColor Green
Write-Host "`nPods:" -ForegroundColor Cyan
kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app

Write-Host "`nServices:" -ForegroundColor Cyan
kubectl get svc -l app.kubernetes.io/name=chatbot-todo-app

Write-Host "`nPersistent Volume Claims:" -ForegroundColor Cyan
kubectl get pvc

# Step 8: Get service URL
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Deployment Successful! ✓" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nAccessing the application..." -ForegroundColor Yellow
Write-Host "Option 1: Run this command to open in browser:" -ForegroundColor Cyan
Write-Host "  minikube service $helmRelease" -ForegroundColor White

Write-Host "`nOption 2: Get URL manually:" -ForegroundColor Cyan
$minikubeIP = minikube ip
Write-Host "  http://${minikubeIP}:30080" -ForegroundColor White

Write-Host "`nOption 3: Port forwarding:" -ForegroundColor Cyan
Write-Host "  kubectl port-forward svc/$helmRelease 8000:8000" -ForegroundColor White
Write-Host "  Then access: http://localhost:8000" -ForegroundColor White

Write-Host "`nUseful Commands:" -ForegroundColor Yellow
Write-Host "  View logs: kubectl logs -l app.kubernetes.io/name=chatbot-todo-app" -ForegroundColor White
Write-Host "  View pods: kubectl get pods" -ForegroundColor White
Write-Host "  Describe pod: kubectl describe pod <pod-name>" -ForegroundColor White
Write-Host "  Delete deployment: helm uninstall $helmRelease" -ForegroundColor White

Write-Host "`nRun test script:" -ForegroundColor Yellow
Write-Host "  .\scripts\test-local-deployment.ps1" -ForegroundColor White
