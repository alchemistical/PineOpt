#!/usr/bin/env node
/**
 * Epic 7 Sprint 1 - Frontend API Migration Test
 * Tests the new API endpoints from frontend perspective
 */

const API_BASE = 'http://localhost:5007';

// Epic 7 Consolidated Endpoints
const ENDPOINTS = {
    // Health endpoints
    health_basic: '/api/health',
    health_detailed: '/api/v1/health/detailed',
    
    // Market data endpoints
    market_overview: '/api/v1/market/overview',
    market_symbols: '/api/v1/market/symbols?limit=5',
    market_tickers: '/api/v1/market/tickers',
    market_status: '/api/v1/market/status',
    
    // Strategy endpoints
    strategy_list: '/api/v1/strategies/list?limit=5',
    strategy_stats: '/api/v1/strategies/stats',
};

async function testEndpoint(name, endpoint) {
    try {
        console.log(`🔍 Testing ${name}...`);
        const response = await fetch(`${API_BASE}${endpoint}`);
        const data = await response.json();
        
        if (response.ok && (data.status === 'success' || data.status === 'healthy')) {
            console.log(`✅ ${name}: OK`);
            return true;
        } else {
            console.log(`❌ ${name}: Failed - ${data.error || 'Unknown error'}`);
            return false;
        }
    } catch (error) {
        console.log(`💥 ${name}: Error - ${error.message}`);
        return false;
    }
}

async function runTests() {
    console.log('🚀 Epic 7 Sprint 1 - Frontend API Migration Test\n');
    
    const results = [];
    
    for (const [name, endpoint] of Object.entries(ENDPOINTS)) {
        const success = await testEndpoint(name, endpoint);
        results.push({ name, success });
        await new Promise(resolve => setTimeout(resolve, 100)); // Small delay
    }
    
    console.log('\n📊 Test Results:');
    const passed = results.filter(r => r.success).length;
    const total = results.length;
    
    console.log(`✅ Passed: ${passed}/${total}`);
    console.log(`❌ Failed: ${total - passed}/${total}`);
    
    if (passed === total) {
        console.log('\n🎉 All Epic 7 Sprint 1 endpoints are working!');
        console.log('✅ Frontend API Migration: COMPLETE');
    } else {
        console.log('\n⚠️  Some endpoints need attention');
        results.filter(r => !r.success).forEach(r => {
            console.log(`   - ${r.name}`);
        });
    }
    
    return passed === total;
}

// Run the test
if (require.main === module) {
    runTests().then(success => {
        process.exit(success ? 0 : 1);
    });
}

module.exports = { runTests };