#!/bin/bash
# Test Cloud Deployment Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================"
echo "Testing Cloud Deployment"
echo -e "========================================${NC}"

ALL_TESTS_PASSED=true

# Test 1: Check Kafka cluster
echo -e "\n${GREEN}Test 1: Checking Kafka cluster...${NC}"
KAFKA_STATUS=$(kubectl get kafka my-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
if [ "$KAFKA_STATUS" == "True" ]; then
    echo -e "${GREEN}✓ Kafka cluster is Ready${NC}"
else
    echo -e "${RED}✗ Kafka cluster is not Ready (Status: $KAFKA_STATUS)${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 2: Check Kafka topics
echo -e "\n${GREEN}Test 2: Checking Kafka topics...${NC}"
TOPIC_COUNT=$(kubectl get kafkatopic -n kafka 2>/dev/null | wc -l)
if [ $TOPIC_COUNT -gt 1 ]; then
    echo -e "${GREEN}✓ Kafka topics found${NC}"
    kubectl get kafkatopic -n kafka
else
    echo -e "${RED}✗ No Kafka topics found${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 3: Check Dapr system
echo -e "\n${GREEN}Test 3: Checking Dapr system...${NC}"
DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
if [ $DAPR_PODS -ge 3 ]; then
    echo -e "${GREEN}✓ Dapr system pods running ($DAPR_PODS pods)${NC}"
    kubectl get pods -n dapr-system
else
    echo -e "${RED}✗ Dapr system incomplete ($DAPR_PODS pods found)${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 4: Check Dapr components
echo -e "\n${GREEN}Test 4: Checking Dapr components...${NC}"
COMPONENTS=$(kubectl get components --no-headers 2>/dev/null | wc -l)
if [ $COMPONENTS -ge 2 ]; then
    echo -e "${GREEN}✓ Dapr components configured ($COMPONENTS components)${NC}"
    kubectl get components
else
    echo -e "${RED}✗ Dapr components missing ($COMPONENTS components found)${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 5: Check Redis
echo -e "\n${GREEN}Test 5: Checking Redis...${NC}"
REDIS_PODS=$(kubectl get pods -l app.kubernetes.io/name=redis --no-headers 2>/dev/null | grep -c Running)
if [ $REDIS_PODS -gt 0 ]; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 6: Check application pods
echo -e "\n${GREEN}Test 6: Checking application pods...${NC}"
APP_PODS=$(kubectl get pods -l app=chatbot-todo-app -o json 2>/dev/null)
if [ ! -z "$APP_PODS" ]; then
    RUNNING_PODS=$(echo $APP_PODS | jq -r '.items[] | select(.status.phase=="Running") | .metadata.name' | wc -l)
    TOTAL_PODS=$(echo $APP_PODS | jq -r '.items | length')

    if [ $RUNNING_PODS -gt 0 ]; then
        echo -e "${GREEN}✓ Application pods running ($RUNNING_PODS/$TOTAL_PODS)${NC}"
        kubectl get pods -l app=chatbot-todo-app
    else
        echo -e "${RED}✗ No application pods running${NC}"
        ALL_TESTS_PASSED=false
    fi
else
    echo -e "${RED}✗ No application pods found${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 7: Check Dapr sidecars
echo -e "\n${GREEN}Test 7: Checking Dapr sidecars...${NC}"
POD_NAME=$(kubectl get pods -l app=chatbot-todo-app -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ ! -z "$POD_NAME" ]; then
    CONTAINERS=$(kubectl get pod $POD_NAME -o jsonpath='{.spec.containers[*].name}')
    if echo "$CONTAINERS" | grep -q "daprd"; then
        echo -e "${GREEN}✓ Dapr sidecar injected in pod $POD_NAME${NC}"
    else
        echo -e "${RED}✗ Dapr sidecar not found in pod $POD_NAME${NC}"
        ALL_TESTS_PASSED=false
    fi
fi

# Test 8: Check Load Balancer service
echo -e "\n${GREEN}Test 8: Checking Load Balancer service...${NC}"
EXTERNAL_IP=$(kubectl get svc chatbot-todo-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ ! -z "$EXTERNAL_IP" ]; then
    echo -e "${GREEN}✓ Load Balancer IP assigned: $EXTERNAL_IP${NC}"
else
    echo -e "${YELLOW}⚠ Load Balancer IP not assigned yet${NC}"
    echo -e "${YELLOW}  This is normal if deployment is recent. Wait a few minutes.${NC}"
fi

# Test 9: Check PVC
echo -e "\n${GREEN}Test 9: Checking Persistent Volume Claim...${NC}"
PVC_STATUS=$(kubectl get pvc chatbot-data-pvc -o jsonpath='{.status.phase}' 2>/dev/null)
if [ "$PVC_STATUS" == "Bound" ]; then
    echo -e "${GREEN}✓ PVC is Bound${NC}"
else
    echo -e "${RED}✗ PVC is $PVC_STATUS${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 10: Check HPA
echo -e "\n${GREEN}Test 10: Checking Horizontal Pod Autoscaler...${NC}"
HPA_EXISTS=$(kubectl get hpa chatbot-todo-app-hpa 2>/dev/null)
if [ ! -z "$HPA_EXISTS" ]; then
    echo -e "${GREEN}✓ HPA configured${NC}"
    kubectl get hpa chatbot-todo-app-hpa
else
    echo -e "${YELLOW}⚠ HPA not found${NC}"
fi

# Test 11: Check secrets
echo -e "\n${GREEN}Test 11: Checking secrets...${NC}"
SECRET_EXISTS=$(kubectl get secret chatbot-secrets 2>/dev/null)
if [ ! -z "$SECRET_EXISTS" ]; then
    echo -e "${GREEN}✓ Application secrets exist${NC}"
else
    echo -e "${RED}✗ Application secrets not found${NC}"
    ALL_TESTS_PASSED=false
fi

# Test 12: Test HTTP endpoint
if [ ! -z "$EXTERNAL_IP" ]; then
    echo -e "\n${GREEN}Test 12: Testing HTTP endpoint...${NC}"
    echo -e "  ${CYAN}Testing: http://$EXTERNAL_IP${NC}"

    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$EXTERNAL_IP --max-time 10)
    if [ "$HTTP_STATUS" == "200" ]; then
        echo -e "${GREEN}✓ HTTP endpoint accessible (Status: 200)${NC}"
    else
        echo -e "${RED}✗ HTTP endpoint returned status: $HTTP_STATUS${NC}"
        ALL_TESTS_PASSED=false
    fi
else
    echo -e "\n${YELLOW}Test 12: Skipping HTTP test (no external IP)${NC}"
fi

# Test 13: Check pod logs
echo -e "\n${GREEN}Test 13: Checking pod logs for errors...${NC}"
if [ ! -z "$POD_NAME" ]; then
    ERROR_COUNT=$(kubectl logs $POD_NAME -c chatbot-todo-app --tail=100 2>/dev/null | grep -iE "error|exception|fatal" | wc -l)
    if [ $ERROR_COUNT -eq 0 ]; then
        echo -e "${GREEN}✓ No errors in application logs${NC}"
    else
        echo -e "${YELLOW}⚠ Found $ERROR_COUNT potential errors in logs${NC}"
        echo -e "${YELLOW}  Review logs with: kubectl logs $POD_NAME -c chatbot-todo-app${NC}"
    fi
fi

# Test 14: Check Dapr health
echo -e "\n${GREEN}Test 14: Checking Dapr health...${NC}"
if [ ! -z "$POD_NAME" ]; then
    DAPR_HEALTH=$(kubectl exec $POD_NAME -c daprd -- wget -q -O- http://localhost:3500/v1.0/healthz 2>/dev/null)
    if [ ! -z "$DAPR_HEALTH" ]; then
        echo -e "${GREEN}✓ Dapr sidecar is healthy${NC}"
    else
        echo -e "${RED}✗ Dapr sidecar health check failed${NC}"
        ALL_TESTS_PASSED=false
    fi
fi

# Summary
echo -e "\n${CYAN}========================================"
if [ "$ALL_TESTS_PASSED" = true ]; then
    echo -e "${GREEN}All Critical Tests Passed! ✓${NC}"
    echo -e "${CYAN}========================================${NC}"

    if [ ! -z "$EXTERNAL_IP" ]; then
        echo -e "\n${GREEN}Application URL:${NC}"
        echo -e "  ${WHITE}http://$EXTERNAL_IP${NC}"
    fi

    echo -e "\n${YELLOW}Monitoring Commands:${NC}"
    echo -e "  Dapr dashboard: ${WHITE}dapr dashboard -k -p 8080${NC}"
    echo -e "  View metrics: ${WHITE}kubectl top pods${NC}"
    echo -e "  View HPA: ${WHITE}kubectl get hpa${NC}"
else
    echo -e "${RED}Some Tests Failed! ✗${NC}"
    echo -e "${CYAN}========================================${NC}"

    echo -e "\n${YELLOW}Debugging Commands:${NC}"
    echo -e "  View all pods: ${WHITE}kubectl get pods --all-namespaces${NC}"
    echo -e "  View events: ${WHITE}kubectl get events --sort-by='.lastTimestamp'${NC}"
    echo -e "  Describe pod: ${WHITE}kubectl describe pod $POD_NAME${NC}"
    echo -e "  View app logs: ${WHITE}kubectl logs $POD_NAME -c chatbot-todo-app${NC}"
    echo -e "  View Dapr logs: ${WHITE}kubectl logs $POD_NAME -c daprd${NC}"
fi
echo -e "${CYAN}========================================${NC}"
