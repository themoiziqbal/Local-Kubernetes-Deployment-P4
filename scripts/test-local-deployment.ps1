# Test Local Deployment Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Local Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$helmRelease = "chatbot-release"
$allTestsPassed = $true

# Test 1: Check if Minikube is running
Write-Host "`nTest 1: Checking Minikube status..." -ForegroundColor Green
$minikubeStatus = minikube status 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Minikube is running" -ForegroundColor Green
} else {
    Write-Host "✗ Minikube is not running" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 2: Check if Helm release exists
Write-Host "`nTest 2: Checking Helm release..." -ForegroundColor Green
$helmList = helm list -q | Select-String -Pattern "^$helmRelease$"
if ($helmList) {
    Write-Host "✓ Helm release '$helmRelease' found" -ForegroundColor Green
} else {
    Write-Host "✗ Helm release '$helmRelease' not found" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 3: Check if pods are running
Write-Host "`nTest 3: Checking pods status..." -ForegroundColor Green
$pods = kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app -o json | ConvertFrom-Json
if ($pods.items.Count -gt 0) {
    $runningPods = 0
    foreach ($pod in $pods.items) {
        $status = $pod.status.phase
        $podName = $pod.metadata.name
        if ($status -eq "Running") {
            Write-Host "  ✓ Pod $podName is Running" -ForegroundColor Green
            $runningPods++
        } else {
            Write-Host "  ✗ Pod $podName is $status" -ForegroundColor Red
            $allTestsPassed = $false
        }
    }
    if ($runningPods -gt 0) {
        Write-Host "✓ $runningPods pod(s) running successfully" -ForegroundColor Green
    }
} else {
    Write-Host "✗ No pods found" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 4: Check if service exists
Write-Host "`nTest 4: Checking service..." -ForegroundColor Green
$service = kubectl get svc $helmRelease -o json 2>&1 | ConvertFrom-Json
if ($service.metadata.name -eq $helmRelease) {
    Write-Host "✓ Service '$helmRelease' exists" -ForegroundColor Green
    Write-Host "  Type: $($service.spec.type)" -ForegroundColor Cyan
    Write-Host "  Port: $($service.spec.ports[0].port)" -ForegroundColor Cyan
    Write-Host "  NodePort: $($service.spec.ports[0].nodePort)" -ForegroundColor Cyan
} else {
    Write-Host "✗ Service not found" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 5: Check if PVC exists and is bound
Write-Host "`nTest 5: Checking Persistent Volume Claim..." -ForegroundColor Green
$pvc = kubectl get pvc -l app.kubernetes.io/name=chatbot-todo-app -o json | ConvertFrom-Json
if ($pvc.items.Count -gt 0) {
    $pvcStatus = $pvc.items[0].status.phase
    $pvcName = $pvc.items[0].metadata.name
    if ($pvcStatus -eq "Bound") {
        Write-Host "✓ PVC '$pvcName' is Bound" -ForegroundColor Green
    } else {
        Write-Host "✗ PVC '$pvcName' is $pvcStatus" -ForegroundColor Red
        $allTestsPassed = $false
    }
} else {
    Write-Host "✗ No PVC found" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 6: Check if secrets exist
Write-Host "`nTest 6: Checking secrets..." -ForegroundColor Green
$secret = kubectl get secret "${helmRelease}-secrets" -o json 2>&1 | ConvertFrom-Json
if ($secret.metadata.name -eq "${helmRelease}-secrets") {
    Write-Host "✓ Secret '${helmRelease}-secrets' exists" -ForegroundColor Green
} else {
    Write-Host "✗ Secret not found" -ForegroundColor Red
    $allTestsPassed = $false
}

# Test 7: Test HTTP endpoint
Write-Host "`nTest 7: Testing HTTP endpoint..." -ForegroundColor Green
$minikubeIP = minikube ip
$servicePort = 30080
$url = "http://${minikubeIP}:${servicePort}"

Write-Host "  Testing URL: $url" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ HTTP endpoint is accessible (Status: 200)" -ForegroundColor Green
    } else {
        Write-Host "✗ HTTP endpoint returned status: $($response.StatusCode)" -ForegroundColor Red
        $allTestsPassed = $false
    }
} catch {
    Write-Host "✗ HTTP endpoint is not accessible" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Yellow
    $allTestsPassed = $false
}

# Test 8: Check pod logs for errors
Write-Host "`nTest 8: Checking pod logs for errors..." -ForegroundColor Green
$podName = kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app -o jsonpath='{.items[0].metadata.name}'
if ($podName) {
    $logs = kubectl logs $podName --tail=50 2>&1
    $errorLines = $logs | Select-String -Pattern "error|exception|fatal" -CaseSensitive:$false
    if ($errorLines) {
        Write-Host "⚠ Found potential errors in logs:" -ForegroundColor Yellow
        $errorLines | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    } else {
        Write-Host "✓ No errors found in recent logs" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allTestsPassed) {
    Write-Host "All Tests Passed! ✓" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nYour application is running at:" -ForegroundColor Green
    Write-Host "  $url" -ForegroundColor White
    Write-Host "`nOr use: minikube service $helmRelease" -ForegroundColor Cyan
} else {
    Write-Host "Some Tests Failed! ✗" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nPlease check the errors above and:" -ForegroundColor Yellow
    Write-Host "  1. View pod status: kubectl get pods" -ForegroundColor White
    Write-Host "  2. View pod logs: kubectl logs <pod-name>" -ForegroundColor White
    Write-Host "  3. Describe pod: kubectl describe pod <pod-name>" -ForegroundColor White
}
Write-Host "========================================" -ForegroundColor Cyan
