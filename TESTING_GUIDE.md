# 🧪 Testing Guide for ChatbotTodoApp Deployments

Complete guide for testing both local and cloud deployments.

---

## 📋 Table of Contents

1. [Prerequisites Testing](#prerequisites-testing)
2. [Local Deployment Testing](#local-deployment-testing)
3. [Cloud Deployment Testing](#cloud-deployment-testing)
4. [Manual Testing Steps](#manual-testing-steps)
5. [Performance Testing](#performance-testing)
6. [Troubleshooting Tests](#troubleshooting-tests)

---

## Prerequisites Testing

### Windows

```powershell
# Run prerequisite verification
.\scripts\verify-prerequisites.ps1
```

### Linux/macOS

```bash
# Check all tools
docker --version
minikube version
kubectl version --client
helm version
```

Expected output: All tools should show version numbers without errors.

---

## Local Deployment Testing

### Automated Testing (Recommended)

**Windows:**

```powershell
# After deployment, run test script
.\scripts\test-local-deployment.ps1
```

**Linux/macOS:**

```bash
chmod +x scripts/test-local-deployment.sh
./scripts/test-local-deployment.sh
```

### What the Test Script Checks

1. ✅ Minikube is running
2. ✅ Helm release exists
3. ✅ Pods are in Running state
4. ✅ Service is accessible
5. ✅ PVC is bound
6. ✅ Secrets exist
7. ✅ HTTP endpoint responds (200 OK)
8. ✅ No critical errors in logs

### Manual Testing Steps

#### 1. Check Cluster Status

```bash
minikube status
kubectl cluster-info
kubectl get nodes
```

Expected:
- Minikube: `Running`
- Node status: `Ready`

#### 2. Check Pods

```bash
kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app
```

Expected output:
```
NAME                               READY   STATUS    RESTARTS   AGE
chatbot-release-xxxxx-xxxxx        1/1     Running   0          5m
chatbot-release-xxxxx-xxxxx        1/1     Running   0          5m
```

#### 3. Check Pod Details

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app -o jsonpath='{.items[0].metadata.name}')

# Describe pod
kubectl describe pod $POD_NAME

# Check logs
kubectl logs $POD_NAME
```

Look for:
- ✅ "Starting AI Chatbot Server..."
- ✅ "Application startup complete"
- ❌ No ERROR or EXCEPTION messages

#### 4. Check Service

```bash
kubectl get svc chatbot-release
```

Expected:
```
NAME              TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
chatbot-release   NodePort   10.96.xxx.xxx   <none>        8000:30080/TCP   5m
```

#### 5. Check PVC

```bash
kubectl get pvc
```

Expected:
```
NAME                      STATUS   VOLUME                                     CAPACITY   ACCESS MODES
chatbot-release-pvc       Bound    pvc-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx          1Gi        RWO
```

#### 6. Test HTTP Endpoint

**Get Minikube IP:**

```bash
minikube ip
# Output: 192.168.49.2 (example)
```

**Test with curl:**

```bash
curl http://$(minikube ip):30080
```

Expected: HTML response with status 200

**Test in browser:**

```bash
# Open automatically
minikube service chatbot-release

# Or manually visit
http://<MINIKUBE-IP>:30080
```

#### 7. Test Application Functionality

1. **Access the web interface**
2. **Create a new todo:**
   - Click "Add Todo" or similar
   - Enter task name
   - Verify it appears in the list

3. **Test AI chatbot:**
   - Send a message to the chatbot
   - Verify AI response (requires valid OpenAI API key)

4. **Test persistence:**
   - Refresh the page
   - Verify todos are still there (SQLite database)

5. **Delete a todo:**
   - Remove a task
   - Verify it's deleted

#### 8. Test Pod Restart (Persistence)

```bash
# Delete a pod
kubectl delete pod $POD_NAME

# Wait for new pod
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=chatbot-todo-app --timeout=60s

# Access app again - data should persist
```

#### 9. Test Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment chatbot-release --replicas=3

# Check pods
kubectl get pods

# Scale back to 2
kubectl scale deployment chatbot-release --replicas=2
```

---

## Cloud Deployment Testing

### Automated Testing

```bash
chmod +x scripts/test-cloud-deployment.sh
./scripts/test-cloud-deployment.sh
```

### What the Cloud Test Script Checks

1. ✅ Kafka cluster is Ready
2. ✅ Kafka topics exist
3. ✅ Dapr system is running
4. ✅ Dapr components configured
5. ✅ Redis is running
6. ✅ Application pods running with Dapr sidecars
7. ✅ Load Balancer has external IP
8. ✅ PVC is bound
9. ✅ HPA is configured
10. ✅ HTTP endpoint accessible
11. ✅ No critical errors in logs
12. ✅ Dapr sidecar is healthy

### Manual Cloud Testing

#### 1. Check Kafka

```bash
# Check Kafka cluster
kubectl get kafka -n kafka

# Check topics
kubectl get kafkatopic -n kafka

# Test Kafka connectivity
kubectl run kafka-test -ti --rm --restart=Never \
  --image=quay.io/strimzi/kafka:0.38.0-kafka-3.6.0 -n kafka \
  -- bin/kafka-broker-api-versions.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092
```

#### 2. Check Dapr

```bash
# Check Dapr system
dapr status -k

# Check Dapr components
kubectl get components

# Describe components
kubectl describe component chatbot-kafka-pubsub
kubectl describe component chatbot-statestore
```

#### 3. Check Application with Dapr

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=chatbot-todo-app -o jsonpath='{.items[0].metadata.name}')

# Check containers in pod (should see both app and daprd)
kubectl get pod $POD_NAME -o jsonpath='{.spec.containers[*].name}'

# Expected output: chatbot-todo-app daprd

# Check Dapr sidecar logs
kubectl logs $POD_NAME -c daprd

# Check Dapr health
kubectl exec $POD_NAME -c daprd -- wget -q -O- http://localhost:3500/v1.0/healthz
```

#### 4. Test Load Balancer

```bash
# Get external IP
kubectl get svc chatbot-todo-service

# Test HTTP
EXTERNAL_IP=$(kubectl get svc chatbot-todo-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP

# Test in browser
echo "http://$EXTERNAL_IP"
```

#### 5. Test Autoscaling (HPA)

```bash
# Check HPA status
kubectl get hpa

# Generate load (install Apache Bench)
ab -n 1000 -c 10 http://$EXTERNAL_IP/

# Watch HPA scale
kubectl get hpa -w

# Watch pods scale
kubectl get pods -l app=chatbot-todo-app -w
```

#### 6. Test Dapr Pub/Sub (Advanced)

```bash
# Publish message to Kafka via Dapr
kubectl exec -it $POD_NAME -c chatbot-todo-app -- \
  curl -X POST http://localhost:3500/v1.0/publish/chatbot-kafka-pubsub/chatbot-events \
  -H "Content-Type: application/json" \
  -d '{"message": "test event"}'

# Check Kafka topic for message
kubectl run kafka-consumer -ti --rm --restart=Never \
  --image=quay.io/strimzi/kafka:0.38.0-kafka-3.6.0 -n kafka \
  -- bin/kafka-console-consumer.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --topic chatbot-events \
  --from-beginning \
  --max-messages 1
```

#### 7. Test Dapr State Store (Advanced)

```bash
# Save state via Dapr
kubectl exec -it $POD_NAME -c chatbot-todo-app -- \
  curl -X POST http://localhost:3500/v1.0/state/chatbot-statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test-key","value":"test-value"}]'

# Retrieve state
kubectl exec -it $POD_NAME -c chatbot-todo-app -- \
  curl http://localhost:3500/v1.0/state/chatbot-statestore/test-key
```

---

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
# Ubuntu/Debian: sudo apt-get install apache2-utils
# macOS: brew install httpd (ab is included)
# Windows: Download from https://httpd.apache.org/download.cgi

# Local testing
ab -n 1000 -c 10 http://$(minikube ip):30080/

# Cloud testing
ab -n 1000 -c 10 http://$EXTERNAL_IP/
```

### Monitor Resource Usage

```bash
# Check pod resource usage
kubectl top pods

# Check node resource usage
kubectl top nodes

# Watch in real-time
watch kubectl top pods
```

### Stress Test

```bash
# Install stress tool in pod
kubectl exec -it $POD_NAME -- apt-get update && apt-get install -y stress

# CPU stress test
kubectl exec -it $POD_NAME -- stress --cpu 2 --timeout 60s

# Watch HPA response
kubectl get hpa -w
```

---

## Troubleshooting Tests

### Test 1: DNS Resolution

```bash
kubectl run dns-test -ti --rm --restart=Never --image=busybox -- nslookup kubernetes.default
```

### Test 2: Network Connectivity

```bash
# Test internal service connectivity
kubectl run netcat-test -ti --rm --restart=Never --image=busybox -- \
  nc -zv chatbot-release 8000
```

### Test 3: Database Persistence

```bash
# Get current data
kubectl exec -it $POD_NAME -- ls -la /app/data

# Delete pod
kubectl delete pod $POD_NAME

# Wait for new pod
sleep 30

# Check data still exists
NEW_POD=$(kubectl get pods -l app.kubernetes.io/name=chatbot-todo-app -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $NEW_POD -- ls -la /app/data
```

### Test 4: Secret Injection

```bash
# Check if secret is mounted
kubectl exec -it $POD_NAME -- printenv | grep OPENAI
```

### Test 5: Health Checks

```bash
# Test liveness probe
kubectl exec -it $POD_NAME -- curl http://localhost:8000/

# Check probe status
kubectl describe pod $POD_NAME | grep -A 5 Liveness
```

---

## Test Results Checklist

### Local Deployment

- [ ] Minikube is running
- [ ] Docker image built successfully
- [ ] Helm release installed
- [ ] 2 pods running
- [ ] Service accessible via NodePort
- [ ] PVC bound to storage
- [ ] Web UI loads successfully
- [ ] Can create/read todos
- [ ] AI chatbot responds
- [ ] Data persists after pod restart
- [ ] No errors in pod logs

### Cloud Deployment

- [ ] DOKS cluster created
- [ ] Kubectl connected to cluster
- [ ] Kafka cluster ready (3 brokers)
- [ ] Kafka topics created
- [ ] Dapr system running
- [ ] Dapr components configured
- [ ] Redis running
- [ ] Application pods running
- [ ] Dapr sidecars injected
- [ ] Load Balancer has external IP
- [ ] Application accessible via HTTP
- [ ] HPA configured
- [ ] Scaling works automatically
- [ ] Pub/Sub messaging works
- [ ] State store works
- [ ] No errors in app/dapr logs

---

## Continuous Testing

### Set Up Monitoring

```bash
# Install metrics server (if not already)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Create a test pod for continuous monitoring
kubectl run test-monitor --image=curlimages/curl:latest --command -- sleep infinity

# Use it for continuous testing
kubectl exec -it test-monitor -- sh
```

### Automated Health Checks

Create a cron job for periodic testing:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: health-check
spec:
  schedule: "*/5 * * * *"  # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: curl
            image: curlimages/curl:latest
            args:
            - /bin/sh
            - -c
            - curl -f http://chatbot-release:8000 || exit 1
          restartPolicy: OnFailure
```

---

## Performance Benchmarks

### Expected Response Times (Approximate)

| Operation | Local | Cloud |
|-----------|-------|-------|
| Health check (/) | < 50ms | < 100ms |
| Load homepage | < 200ms | < 300ms |
| Create todo | < 500ms | < 800ms |
| AI response | 1-3s | 1-3s |

### Resource Usage

| Component | CPU | Memory |
|-----------|-----|--------|
| App container | 100-250m | 256-512Mi |
| Dapr sidecar | 50-100m | 128-256Mi |
| Kafka broker | 500m | 1Gi |
| Redis | 100m | 256Mi |

---

**Happy Testing! 🧪**
