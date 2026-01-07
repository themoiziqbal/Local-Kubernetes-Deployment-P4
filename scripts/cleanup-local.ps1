# Cleanup Local Deployment Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Local Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$helmRelease = "chatbot-release"

# Confirm cleanup
Write-Host "`nThis will delete all local deployment resources." -ForegroundColor Yellow
$confirmation = Read-Host "Are you sure you want to continue? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit 0
}

# Delete Helm release
Write-Host "`nDeleting Helm release..." -ForegroundColor Green
helm uninstall $helmRelease 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Helm release deleted" -ForegroundColor Green
} else {
    Write-Host "⚠ Helm release not found or already deleted" -ForegroundColor Yellow
}

# Delete PVC
Write-Host "`nDeleting Persistent Volume Claims..." -ForegroundColor Green
kubectl delete pvc -l app.kubernetes.io/name=chatbot-todo-app 2>&1 | Out-Null
Write-Host "✓ PVCs deleted" -ForegroundColor Green

# Delete secrets
Write-Host "`nDeleting secrets..." -ForegroundColor Green
kubectl delete secret "${helmRelease}-secrets" 2>&1 | Out-Null
Write-Host "✓ Secrets deleted" -ForegroundColor Green

# Verify cleanup
Write-Host "`nVerifying cleanup..." -ForegroundColor Green
$remainingPods = kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app 2>&1
if ($remainingPods -like "*No resources found*") {
    Write-Host "✓ All pods deleted" -ForegroundColor Green
} else {
    Write-Host "⚠ Some resources may still be terminating" -ForegroundColor Yellow
}

# Option to stop Minikube
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

$stopMinikube = Read-Host "`nDo you want to stop Minikube? (yes/no)"
if ($stopMinikube -eq "yes") {
    Write-Host "Stopping Minikube..." -ForegroundColor Yellow
    minikube stop
    Write-Host "✓ Minikube stopped" -ForegroundColor Green
}

$deleteMinikube = Read-Host "`nDo you want to DELETE Minikube cluster? (yes/no)"
if ($deleteMinikube -eq "yes") {
    Write-Host "Deleting Minikube cluster..." -ForegroundColor Yellow
    minikube delete
    Write-Host "✓ Minikube cluster deleted" -ForegroundColor Green
}

Write-Host "`nCleanup finished!" -ForegroundColor Green
