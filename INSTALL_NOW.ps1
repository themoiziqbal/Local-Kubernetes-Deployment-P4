# Run this script as Administrator
# Right-click PowerShell -> Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Kubernetes Prerequisites" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`nERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Right-click on PowerShell" -ForegroundColor White
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host "3. Navigate to: cd 'C:\Users\ThinK Pad\ChatbotTodoApp'" -ForegroundColor White
    Write-Host "4. Run: .\INSTALL_NOW.ps1" -ForegroundColor White
    pause
    exit 1
}

Write-Host "`n✓ Running as Administrator" -ForegroundColor Green

# Install Docker Desktop
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 1: Installing Docker Desktop" -ForegroundColor Green
Write-Host "This will take 5-10 minutes..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

choco install docker-desktop -y

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker Desktop installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Docker Desktop installation had issues" -ForegroundColor Red
}

# Install kubectl
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 2: Installing kubectl" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

choco install kubernetes-cli -y

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ kubectl installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ kubectl installation had issues" -ForegroundColor Red
}

# Install Minikube
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 3: Installing Minikube" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

choco install minikube -y

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Minikube installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Minikube installation had issues" -ForegroundColor Red
}

# Install Helm
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 4: Installing Helm" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

choco install kubernetes-helm -y

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Helm installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Helm installation had issues" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nIMPORTANT NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. RESTART YOUR COMPUTER" -ForegroundColor White
Write-Host "2. After restart, start Docker Desktop from Start Menu" -ForegroundColor White
Write-Host "3. Wait for Docker to fully start (whale icon steady in system tray)" -ForegroundColor White
Write-Host "4. Open NEW PowerShell and run:" -ForegroundColor White
Write-Host "   cd 'C:\Users\ThinK Pad\ChatbotTodoApp'" -ForegroundColor Cyan
Write-Host "   .\scripts\verify-prerequisites.ps1" -ForegroundColor Cyan
Write-Host "5. Then deploy with:" -ForegroundColor White
Write-Host "   .\scripts\deploy-local.ps1 -OpenAIApiKey 'sk-YOUR-KEY'" -ForegroundColor Cyan

Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
