# Verification and Deployment Script
# Run this in a NEW PowerShell window (close and reopen)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verifying Prerequisites Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$allInstalled = $true

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Green
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker command failed" -ForegroundColor Red
        Write-Host "  Make sure Docker Desktop is RUNNING!" -ForegroundColor Yellow
        $allInstalled = $false
    }
} catch {
    Write-Host "✗ Docker is NOT accessible" -ForegroundColor Red
    Write-Host "  IMPORTANT: Start Docker Desktop from Start Menu" -ForegroundColor Yellow
    Write-Host "  Wait for Docker whale icon to be steady in system tray" -ForegroundColor Yellow
    $allInstalled = $false
}

# Check kubectl
Write-Host "`nChecking kubectl..." -ForegroundColor Green
try {
    $kubectlVersion = kubectl version --client --short 2>&1
    Write-Host "✓ kubectl is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ kubectl is NOT accessible" -ForegroundColor Red
    $allInstalled = $false
}

# Check Minikube
Write-Host "`nChecking Minikube..." -ForegroundColor Green
try {
    $minikubeVersion = minikube version --short 2>&1
    Write-Host "✓ $minikubeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Minikube is NOT accessible" -ForegroundColor Red
    $allInstalled = $false
}

# Check Helm
Write-Host "`nChecking Helm..." -ForegroundColor Green
try {
    $helmVersion = helm version --short 2>&1
    Write-Host "✓ $helmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Helm is NOT accessible" -ForegroundColor Red
    $allInstalled = $false
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($allInstalled) {
    Write-Host "✓ All Prerequisites Installed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan

    Write-Host "`nReady to Deploy! 🚀" -ForegroundColor Green
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Get your OpenAI API key from: https://platform.openai.com/api-keys" -ForegroundColor White
    Write-Host "2. Run the deployment command:" -ForegroundColor White
    Write-Host "`n   .\scripts\deploy-local.ps1 -OpenAIApiKey 'sk-YOUR-KEY-HERE'" -ForegroundColor Cyan
    Write-Host "`n   (Replace sk-YOUR-KEY-HERE with your actual OpenAI API key)" -ForegroundColor Yellow

} else {
    Write-Host "✗ Some Prerequisites Missing or Not Running!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan

    Write-Host "`nTroubleshooting Steps:" -ForegroundColor Yellow
    Write-Host "1. Make sure you've RESTARTED your computer after installation" -ForegroundColor White
    Write-Host "2. START DOCKER DESKTOP from Start Menu" -ForegroundColor White
    Write-Host "3. Wait for Docker to fully start (whale icon steady)" -ForegroundColor White
    Write-Host "4. Close and reopen PowerShell" -ForegroundColor White
    Write-Host "5. Run this script again" -ForegroundColor White
}

Write-Host "`nPress any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
