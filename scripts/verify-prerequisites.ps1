# Verify Prerequisites Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verifying Prerequisites" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$allInstalled = $true

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Green
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker --version
    Write-Host "✓ Docker is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Docker is NOT installed" -ForegroundColor Red
    $allInstalled = $false
}

# Check kubectl
Write-Host "`nChecking kubectl..." -ForegroundColor Green
if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    kubectl version --client
    Write-Host "✓ kubectl is installed" -ForegroundColor Green
} else {
    Write-Host "✗ kubectl is NOT installed" -ForegroundColor Red
    $allInstalled = $false
}

# Check Minikube
Write-Host "`nChecking Minikube..." -ForegroundColor Green
if (Get-Command minikube -ErrorAction SilentlyContinue) {
    minikube version
    Write-Host "✓ Minikube is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Minikube is NOT installed" -ForegroundColor Red
    $allInstalled = $false
}

# Check Helm
Write-Host "`nChecking Helm..." -ForegroundColor Green
if (Get-Command helm -ErrorAction SilentlyContinue) {
    helm version
    Write-Host "✓ Helm is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Helm is NOT installed" -ForegroundColor Red
    $allInstalled = $false
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($allInstalled) {
    Write-Host "All prerequisites are installed! ✓" -ForegroundColor Green
    Write-Host "You can now proceed with deployment." -ForegroundColor Green
    Write-Host "`nRun: .\scripts\deploy-local.ps1" -ForegroundColor Yellow
} else {
    Write-Host "Some prerequisites are missing! ✗" -ForegroundColor Red
    Write-Host "Please run: .\scripts\install-prerequisites.ps1" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
