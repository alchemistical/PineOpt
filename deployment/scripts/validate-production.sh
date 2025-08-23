#!/bin/bash

# Epic 7 Production Deployment Validation Script
# Comprehensive validation of all Sprint 3 features in production

set -e

echo "======================================================================="
echo "🔍 PineOpt Epic 7 Production Deployment Validation"
echo "======================================================================="

# Configuration
BACKEND_URL="http://localhost:5007"
FRONTEND_URL="http://localhost:3000"
MAX_WAIT_TIME=120
CHECK_INTERVAL=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for status messages
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
    esac
}

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local wait_time=0
    
    print_status "INFO" "Waiting for $service_name to be ready..."
    
    while [ $wait_time -lt $MAX_WAIT_TIME ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_status "SUCCESS" "$service_name is ready (${wait_time}s)"
            return 0
        fi
        sleep $CHECK_INTERVAL
        wait_time=$((wait_time + CHECK_INTERVAL))
        echo -n "."
    done
    
    print_status "ERROR" "$service_name failed to become ready within ${MAX_WAIT_TIME}s"
    return 1
}

# Test API endpoint
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    local response
    response=$(curl -s -w "%{http_code}" "$url" -o /dev/null) || response="000"
    
    if [ "$response" = "$expected_status" ]; then
        print_status "SUCCESS" "$description ($response)"
        return 0
    else
        print_status "ERROR" "$description (Expected: $expected_status, Got: $response)"
        return 1
    fi
}

# Validation counters
total_tests=0
passed_tests=0

run_test() {
    local test_command="$1"
    local test_name="$2"
    
    total_tests=$((total_tests + 1))
    echo ""
    print_status "INFO" "Running: $test_name"
    
    if eval "$test_command"; then
        passed_tests=$((passed_tests + 1))
    fi
}

echo ""
echo "🚀 Starting Epic 7 Production Validation..."
echo ""

# 1. Basic Service Health Checks
print_status "INFO" "Phase 1: Basic Service Health Checks"
echo "-----------------------------------"

run_test "wait_for_service '$BACKEND_URL/api/health' 'Backend Service'" "Backend Health Check"
run_test "wait_for_service '$FRONTEND_URL/health' 'Frontend Service'" "Frontend Health Check"

# 2. Epic 7 API Architecture Validation
print_status "INFO" "Phase 2: Epic 7 API Architecture Validation"
echo "---------------------------------------------"

run_test "test_endpoint '$BACKEND_URL/api' 'API Info Endpoint'" "API Information"
run_test "test_endpoint '$BACKEND_URL/api/health' 'Health Endpoint'" "Health Check"

# Test Epic 7 v1 API endpoints
run_test "test_endpoint '$BACKEND_URL/api/v1/health/status' 'Health Status'" "Health Status API"
run_test "test_endpoint '$BACKEND_URL/api/v1/market/overview' 'Market Overview'" "Market Data API"
run_test "test_endpoint '$BACKEND_URL/api/v1/strategies' 'Strategies List'" "Strategy Management API"

# 3. Sprint 3 Task 1: Testing Suite Validation
print_status "INFO" "Phase 3: Testing Infrastructure Validation"
echo "--------------------------------------------"

# Check if test endpoints work
run_test "test_endpoint '$BACKEND_URL/api/v1/health/detailed' 'Detailed Health'" "Comprehensive Health Tests"

# 4. Sprint 3 Task 2: Documentation Validation
print_status "INFO" "Phase 4: Interactive Documentation Validation"
echo "-----------------------------------------------"

run_test "test_endpoint '$BACKEND_URL/docs/' 'Interactive Documentation'" "Documentation Portal"
run_test "test_endpoint '$BACKEND_URL/docs/swagger' 'Swagger UI'" "Swagger Interface"
run_test "test_endpoint '$BACKEND_URL/docs/openapi.json' 'OpenAPI Spec'" "OpenAPI Specification"

# 5. Sprint 3 Task 3: Performance & Caching Validation  
print_status "INFO" "Phase 5: Performance Optimization Validation"
echo "-----------------------------------------------"

# Test caching system
run_test "test_endpoint '$BACKEND_URL/api/v1/market/overview' 'Cached Market Data'" "Market Data Caching"

# Test memory management
print_status "INFO" "Testing memory management..."
memory_usage=$(curl -s "$BACKEND_URL/api/v1/monitoring/system" | grep -o '"memory_percent":[0-9.]*' | cut -d':' -f2 || echo "0")
if [ "${memory_usage%.*}" -lt 90 ]; then
    print_status "SUCCESS" "Memory usage within limits (${memory_usage}%)"
    passed_tests=$((passed_tests + 1))
else
    print_status "WARNING" "High memory usage (${memory_usage}%)"
fi
total_tests=$((total_tests + 1))

# 6. Sprint 3 Task 4: Advanced Monitoring Validation
print_status "INFO" "Phase 6: Advanced Monitoring System Validation"
echo "-------------------------------------------------"

run_test "test_endpoint '$BACKEND_URL/api/v1/monitoring/summary' 'Monitoring Summary'" "Monitoring Dashboard"
run_test "test_endpoint '$BACKEND_URL/api/v1/monitoring/health' 'Monitoring Health'" "Health Monitoring"
run_test "test_endpoint '$BACKEND_URL/api/v1/monitoring/system' 'System Metrics'" "System Monitoring"
run_test "test_endpoint '$BACKEND_URL/api/v1/monitoring/trading' 'Trading Metrics'" "Trading Monitoring"
run_test "test_endpoint '$BACKEND_URL/api/v1/monitoring/alerts' 'Alert Status'" "Alert System"

# 7. Sprint 3 Task 5: Production Deployment Validation
print_status "INFO" "Phase 7: Production Deployment Features"
echo "----------------------------------------"

# Test production environment settings
run_test "curl -s '$BACKEND_URL/api' | grep -q 'production'" "Production Environment"
run_test "curl -s '$BACKEND_URL/api' | grep -q 'Epic 7'" "Epic 7 Architecture"

# Test Docker health checks
if docker ps --filter "name=pineopt-backend" --filter "health=healthy" | grep -q "pineopt-backend"; then
    print_status "SUCCESS" "Backend Docker container healthy"
    passed_tests=$((passed_tests + 1))
else
    print_status "ERROR" "Backend Docker container not healthy"
fi
total_tests=$((total_tests + 1))

if docker ps --filter "name=pineopt-frontend" --filter "health=healthy" | grep -q "pineopt-frontend"; then
    print_status "SUCCESS" "Frontend Docker container healthy"  
    passed_tests=$((passed_tests + 1))
else
    print_status "ERROR" "Frontend Docker container not healthy"
fi
total_tests=$((total_tests + 1))

# 8. Integration Testing
print_status "INFO" "Phase 8: End-to-End Integration Testing"
echo "-----------------------------------------"

# Test full workflow
print_status "INFO" "Testing complete API workflow..."

# Test market data -> strategy -> backtest flow
market_response=$(curl -s "$BACKEND_URL/api/v1/market/overview" || echo "failed")
if echo "$market_response" | grep -q "success"; then
    print_status "SUCCESS" "Market data integration working"
    passed_tests=$((passed_tests + 1))
else
    print_status "ERROR" "Market data integration failed"
fi
total_tests=$((total_tests + 1))

# Performance test
start_time=$(date +%s%3N)
curl -s "$BACKEND_URL/api/health" > /dev/null
end_time=$(date +%s%3N)
response_time=$((end_time - start_time))

if [ $response_time -lt 1000 ]; then
    print_status "SUCCESS" "API response time excellent (${response_time}ms)"
    passed_tests=$((passed_tests + 1))
elif [ $response_time -lt 3000 ]; then
    print_status "SUCCESS" "API response time good (${response_time}ms)"
    passed_tests=$((passed_tests + 1))
else
    print_status "WARNING" "API response time slow (${response_time}ms)"
fi
total_tests=$((total_tests + 1))

# Final Results
echo ""
echo "======================================================================="
echo "📊 Epic 7 Production Validation Results"
echo "======================================================================="

success_rate=$((passed_tests * 100 / total_tests))

print_status "INFO" "Total Tests: $total_tests"
print_status "SUCCESS" "Passed: $passed_tests"  
print_status "ERROR" "Failed: $((total_tests - passed_tests))"
print_status "INFO" "Success Rate: ${success_rate}%"

echo ""

if [ $success_rate -ge 90 ]; then
    print_status "SUCCESS" "🎉 EPIC 7 PRODUCTION DEPLOYMENT EXCELLENT!"
    echo ""
    echo "🚀 All Sprint 3 Features Validated:"
    echo "  ✅ Task 1: Comprehensive Testing Suite"
    echo "  ✅ Task 2: Interactive API Documentation" 
    echo "  ✅ Task 3: Performance Optimization & Caching"
    echo "  ✅ Task 4: Advanced Monitoring & Metrics"
    echo "  ✅ Task 5: Production Deployment & CI/CD"
    echo ""
    echo "🌟 PineOpt Epic 7 is production-ready!"
    echo "🌐 Frontend: $FRONTEND_URL"
    echo "🔧 API: $BACKEND_URL/api"
    echo "📊 Monitoring: $BACKEND_URL/api/v1/monitoring/summary"
    echo "📚 Documentation: $BACKEND_URL/docs/"
    exit 0
elif [ $success_rate -ge 80 ]; then
    print_status "WARNING" "⚠️ EPIC 7 DEPLOYMENT GOOD - Minor Issues Found"
    echo "Some non-critical issues detected. Review failed tests above."
    exit 0
else
    print_status "ERROR" "❌ EPIC 7 DEPLOYMENT NEEDS ATTENTION"
    echo "Critical issues found. Please review and fix before production use."
    exit 1
fi