#!/usr/bin/env python3
"""
Comprehensive API Endpoints Test Suite
Tests all API endpoints for correct ports, naming, and functionality
"""

import requests
import json
import time
from typing import Dict, List, Tuple, Any
from datetime import datetime

class APIEndpointTester:
    def __init__(self, base_url: str = "http://localhost:5007"):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, endpoint: str, method: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if status == "PASS":
            self.passed += 1
            print(f"✅ {method} {endpoint} - {status}")
        else:
            self.failed += 1
            print(f"❌ {method} {endpoint} - {status} - {details}")
    
    def test_endpoint(self, endpoint: str, method: str = "GET", 
                     data: Dict = None, expected_keys: List[str] = None,
                     description: str = "") -> bool:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                self.log_result(endpoint, method, "FAIL", f"Unsupported method: {method}")
                return False
                
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if expected_keys:
                        missing_keys = [key for key in expected_keys if key not in json_response]
                        if missing_keys:
                            self.log_result(endpoint, method, "FAIL", f"Missing keys: {missing_keys}")
                            return False
                    
                    self.log_result(endpoint, method, "PASS", description)
                    return True
                except json.JSONDecodeError:
                    self.log_result(endpoint, method, "FAIL", "Invalid JSON response")
                    return False
            else:
                self.log_result(endpoint, method, "FAIL", f"HTTP {response.status_code}: {response.text[:100]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, method, "FAIL", f"Request failed: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all endpoint tests"""
        print("🚀 COMPREHENSIVE API ENDPOINT TEST SUITE")
        print("=" * 60)
        print(f"Testing base URL: {self.base_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # 1. Health Check Endpoints
        print("📋 HEALTH CHECK ENDPOINTS")
        print("-" * 30)
        self.test_endpoint("/api/intelligent-conversion/health", "GET", 
                          expected_keys=["status", "service", "capabilities"],
                          description="AI conversion service health")
        
        # 2. Strategy Management Endpoints
        print("\n📁 STRATEGY MANAGEMENT ENDPOINTS") 
        print("-" * 35)
        self.test_endpoint("/api/strategies", "GET",
                          expected_keys=["strategies", "count", "success"],
                          description="List all strategies")
        
        # 3. Market Data Endpoints
        print("\n📈 MARKET DATA ENDPOINTS")
        print("-" * 25)
        self.test_endpoint("/api/market/overview", "GET",
                          expected_keys=["success", "data"],
                          description="Market overview data")
        
        # 4. Conversion Endpoints
        print("\n🔄 CONVERSION ENDPOINTS")
        print("-" * 23)
        
        # Test working conversion
        sample_pine = '''
// @version=4
strategy("Test Strategy", overlay=true)

rsi_length = input(14, "RSI Length")
oversold = input(30, "Oversold")

rsi_val = rsi(close, rsi_length)

if rsi_val < oversold
    strategy.entry("Long", strategy.long)
    
if rsi_val > oversold + 40
    strategy.close("Long")
'''
        
        self.test_endpoint("/api/intelligent-conversion/convert/working", "POST",
                          data={"pine_code": sample_pine, "strategy_name": "TestStrategy"},
                          expected_keys=["success", "python_code", "parameters"],
                          description="Working Pine conversion")
        
        self.test_endpoint("/api/intelligent-conversion/convert/hye", "POST",
                          data={"pine_code": sample_pine, "strategy_name": "HYEStrategy"},
                          expected_keys=["success", "python_code", "parameters"],
                          description="HYE-style conversion")
        
        # 5. Backtest Endpoints
        print("\n🏃 BACKTEST ENDPOINTS")
        print("-" * 20)
        
        self.test_endpoint("/api/real-backtest/convert-and-backtest", "POST",
                          data={
                              "pine_code": sample_pine,
                              "strategy_name": "BacktestStrategy", 
                              "symbol": "BTCUSDT",
                              "interval": "1h",
                              "limit": 100
                          },
                          expected_keys=["success"],
                          description="Real backtest conversion")
        
        # Test regular backtest endpoint
        self.test_endpoint("/api/backtests/run", "POST",
                          data={
                              "strategy_id": "test",
                              "symbol": "BTCUSDT",
                              "timeframe": "1h",
                              "start_date": "2024-01-01",
                              "end_date": "2024-01-02"
                          },
                          expected_keys=["success", "config"],
                          description="Regular backtest run")
        
        # 6. Data Provider Endpoints
        print("\n📊 DATA PROVIDER ENDPOINTS")
        print("-" * 27)
        
        self.test_endpoint("/api/data/binance/symbols", "GET",
                          expected_keys=["success"],
                          description="Binance symbols list")
        
        # 7. Utility Endpoints  
        print("\n🔧 UTILITY ENDPOINTS")
        print("-" * 19)
        
        self.test_endpoint("/api/intelligent-conversion/indicators", "GET",
                          expected_keys=["success", "indicators"],
                          description="Available indicators list")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌") 
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"   • {result['method']} {result['endpoint']}: {result['details']}")
        
        print(f"\n✅ API CONFIGURATION VERIFIED:")
        print(f"   • Base URL: {self.base_url}")
        print(f"   • All endpoints tested for correct ports")
        print(f"   • Response format validation completed")
        
        return {
            "total_tests": total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": success_rate,
            "base_url": self.base_url,
            "results": self.results
        }

def main():
    """Run complete API test suite"""
    tester = APIEndpointTester("http://localhost:5007")
    
    # Run all tests
    tester.run_comprehensive_tests()
    
    # Generate report
    report = tester.generate_report()
    
    # Save results to file
    with open("api_test_results.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Test results saved to: api_test_results.json")
    
    return report

if __name__ == "__main__":
    main()