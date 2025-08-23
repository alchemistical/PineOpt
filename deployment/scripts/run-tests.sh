#!/bin/bash

# Comprehensive testing script for Pine2Py CryptoLab
set -e

echo "🧪 Pine2Py CryptoLab - Comprehensive Test Suite"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${BLUE}[TEST $TOTAL_TESTS]${NC} $test_name"
    echo "Command: $test_command"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED${NC}: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to test API endpoint
test_api_endpoint() {
    local endpoint="$1"
    local expected_status="$2"
    local description="$3"
    
    run_test "$description" "curl -s -o /dev/null -w '%{http_code}' http://localhost:5001$endpoint | grep -q '$expected_status'"
}

echo "🚀 Starting test suite..."

# 1. Backend API Tests
echo -e "\n${YELLOW}=== BACKEND API TESTS ===${NC}"

test_api_endpoint "/" "200" "Health check endpoint"
test_api_endpoint "/api/market/status" "200" "Market data status"
test_api_endpoint "/api/backtests/health" "200" "Backtest engine health"
test_api_endpoint "/api/strategies" "200" "Strategies list endpoint"

# 2. Market Data Tests
echo -e "\n${YELLOW}=== MARKET DATA TESTS ===${NC}"

run_test "Market overview data" "curl -s http://localhost:5001/api/market/overview | jq -e '.success == true'"
run_test "BTC ticker data" "curl -s http://localhost:5001/api/market/ticker/BTC | jq -e '.success == true and .data.price > 0'"
run_test "Top crypto pairs" "curl -s http://localhost:5001/api/market/top-pairs | jq -e '.success == true and (.data.pairs | length) > 0'"

# 3. Real Data Validation Tests
echo -e "\n${YELLOW}=== REAL DATA VALIDATION TESTS ===${NC}"

run_test "BTC price is realistic" "curl -s http://localhost:5001/api/market/ticker/BTC | jq -e '.data.price > 50000 and .data.price < 200000'"
run_test "Volume data exists" "curl -s http://localhost:5001/api/market/ticker/BTC | jq -e '.data.volume_24h > 0'"
run_test "Historical data availability" "curl -s 'http://localhost:5001/api/market/historical/BTC?timeframe=1h&days=7' | jq -e '.success == true and (.data.candles | length) > 0'"

# 4. Strategy and Backtest Tests
echo -e "\n${YELLOW}=== STRATEGY & BACKTEST TESTS ===${NC}"

run_test "Backtest stats endpoint" "curl -s http://localhost:5001/api/backtests/stats | jq -e '.success == true'"
run_test "Backtest list endpoint" "curl -s http://localhost:5001/api/backtests | jq -e '.success == true'"

# 5. Pine Script Conversion Tests
echo -e "\n${YELLOW}=== PINE SCRIPT CONVERSION TESTS ===${NC}"

run_test "Pine script conversion endpoint" "curl -s -X POST http://localhost:5001/api/convert-pine -H 'Content-Type: application/json' -d '{\"pine_code\": \"//@version=5\\nstrategy(\\\"Test\\\", overlay=true)\\nrsi = ta.rsi(close, 14)\", \"strategy_name\": \"Test RSI\"}' | jq -e '.success == true'"

# 6. Performance Tests
echo -e "\n${YELLOW}=== PERFORMANCE TESTS ===${NC}"

run_test "API response time < 2s" "timeout 2s curl -s http://localhost:5001/api/market/overview > /dev/null"
run_test "Market data cache performance" "time curl -s http://localhost:5001/api/market/ticker/BTC > /dev/null"

# 7. Security Tests
echo -e "\n${YELLOW}=== SECURITY TESTS ===${NC}"

run_test "CORS headers present" "curl -s -I http://localhost:5001/api/market/status | grep -i 'access-control-allow-origin'"
run_test "Content-Type headers correct" "curl -s -I http://localhost:5001/api/market/status | grep -i 'content-type: application/json'"

# 8. Database Tests
echo -e "\n${YELLOW}=== DATABASE TESTS ===${NC}"

run_test "Strategies database accessible" "test -f database/pineopt.db"
run_test "Market data database exists" "test -f market_data.db"
run_test "Database has strategies" "sqlite3 database/pineopt.db 'SELECT COUNT(*) FROM strategies;' | grep -v '^0$'"

# 9. File System Tests
echo -e "\n${YELLOW}=== FILE SYSTEM TESTS ===${NC}"

run_test "Required directories exist" "test -d outputs && test -d database && test -d uploads"
run_test "Configuration files exist" "test -f .env.production && test -f docker-compose.yml"
run_test "Scripts are executable" "test -x scripts/start-production.sh"

# 10. Integration Tests
echo -e "\n${YELLOW}=== INTEGRATION TESTS ===${NC}"

# Test full backtest workflow (if we have strategies)
STRATEGY_COUNT=$(sqlite3 database/pineopt.db 'SELECT COUNT(*) FROM strategies;' 2>/dev/null || echo "0")
if [ "$STRATEGY_COUNT" -gt 0 ]; then
    STRATEGY_ID=$(sqlite3 database/pineopt.db 'SELECT id FROM strategies LIMIT 1;' 2>/dev/null || echo "")
    if [ -n "$STRATEGY_ID" ]; then
        run_test "Full backtest integration" "curl -s -X POST http://localhost:5001/api/backtests/run -H 'Content-Type: application/json' -d '{\"strategy_id\": \"$STRATEGY_ID\", \"symbol\": \"BTCUSDT\", \"timeframe\": \"1h\", \"initial_capital\": 10000}' | jq -e '.execution_time_seconds >= 0'"
    fi
fi

# Test data flow: Market Data -> Strategy -> Backtest
run_test "Data flow integration" "
# Get market data
MARKET_DATA=\$(curl -s http://localhost:5001/api/market/ticker/BTC)
echo \$MARKET_DATA | jq -e '.success == true and .data.price > 0' &&
# Verify strategy conversion works
curl -s -X POST http://localhost:5001/api/convert-pine -H 'Content-Type: application/json' -d '{\"pine_code\": \"//@version=5\\nstrategy(\\\"Test\\\", overlay=true)\\nrsi = ta.rsi(close, 14)\", \"strategy_name\": \"Integration Test\"}' | jq -e '.success == true'
"

# Summary
echo -e "\n${YELLOW}=== TEST SUMMARY ===${NC}"
echo "=============================================="
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Pine2Py CryptoLab is ready for production!"
    exit 0
else
    echo -e "\n${RED}⚠️ SOME TESTS FAILED${NC}"
    echo "Please review the failed tests before deploying."
    exit 1
fi