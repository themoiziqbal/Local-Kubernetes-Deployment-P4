# Windows Prerequisites Installation Script
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Prerequisites for Kubernetes Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Install Chocolatey if not installed
Write-Host "`nStep 1: Checking Chocolatey..." -ForegroundColor Green
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
} else {
    Write-Host "Chocolatey already installed!" -ForegroundColor Green
}

# Install Docker Desktop
Write-Host "`nStep 2: Checking Docker Desktop..." -ForegroundColor Green
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
    choco install docker-desktop -y
    Write-Host "Docker Desktop installed. Please restart your computer and run Docker Desktop." -ForegroundColor Yellow
} else {
    Write-Host "Docker already installed!" -ForegroundColor Green
    docker --version
}

# Install kubectl
Write-Host "`nStep 3: Checking kubectl..." -ForegroundColor Green
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "Installing kubectl..." -ForegroundColor Yellow
    choco install kubernetes-cli -y
} else {
    Write-Host "kubectl already installed!" -ForegroundColor Green
    kubectl version --client
}

# Install Minikube
Write-Host "`nStep 4: Checking Minikube..." -ForegroundColor Green
if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Minikube..." -ForegroundColor Yellow
    choco install minikube -y
} else {
    Write-Host "Minikube already installed!" -ForegroundColor Green
    minikube version
}

# Install Helm
Write-Host "`nStep 5: Checking Helm..." -ForegroundColor Green
if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Helm..." -ForegroundColor Yellow
    choco install kubernetes-helm -y
} else {
    Write-Host "Helm already installed!" -ForegroundColor Green
    helm version
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Restart PowerShell/Terminal" -ForegroundColor White
Write-Host "2. Start Docker Desktop application" -ForegroundColor White
Write-Host "3. Run: .\scripts\verify-prerequisites.ps1" -ForegroundColor White
Write-Host "4. Then run: .\scripts\deploy-local.ps1" -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
