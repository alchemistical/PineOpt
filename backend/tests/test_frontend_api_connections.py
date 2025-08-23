#!/usr/bin/env python3
"""
Frontend API Connection Tester
Verifies all frontend components are using correct API endpoints and ports
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import json

class FrontendAPITester:
    def __init__(self, src_path: str = "./src"):
        self.src_path = Path(src_path)
        self.results = {
            "correct_endpoints": [],
            "incorrect_endpoints": [],
            "files_checked": [],
            "summary": {}
        }
        
    def find_api_calls(self, file_path: Path) -> List[Dict]:
        """Find all API calls in a file"""
        api_calls = []
        
        try:
            content = file_path.read_text()
            
            # Find fetch calls with URLs
            fetch_pattern = r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]'
            matches = re.findall(fetch_pattern, content)
            
            for match in matches:
                if 'localhost' in match or '/api/' in match:
                    line_num = content[:content.find(match)].count('\n') + 1
                    api_calls.append({
                        "url": match,
                        "line": line_num,
                        "file": str(file_path)
                    })
            
            # Also look for template literals with URLs
            template_pattern = r'`([^`]*localhost[^`]*)`'
            template_matches = re.findall(template_pattern, content)
            
            for match in template_matches:
                if '/api/' in match:
                    line_num = content[:content.find(match)].count('\n') + 1
                    api_calls.append({
                        "url": match,
                        "line": line_num, 
                        "file": str(file_path)
                    })
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return api_calls
    
    def analyze_endpoints(self):
        """Analyze all frontend files for API endpoints"""
        print("🔍 FRONTEND API CONNECTION ANALYSIS")
        print("=" * 50)
        
        # Find all TypeScript/JavaScript files
        file_patterns = ['**/*.tsx', '**/*.ts', '**/*.jsx', '**/*.js']
        all_files = []
        
        for pattern in file_patterns:
            all_files.extend(self.src_path.glob(pattern))
        
        correct_port = "5007"
        incorrect_ports = ["5001", "3001", "8000", "3000"]  # Common wrong ports
        
        total_api_calls = 0
        correct_calls = 0
        incorrect_calls = 0
        
        print(f"Scanning {len(all_files)} files...\n")
        
        for file_path in all_files:
            api_calls = self.find_api_calls(file_path)
            
            if api_calls:
                self.results["files_checked"].append(str(file_path))
                total_api_calls += len(api_calls)
                
                print(f"📄 {file_path.name}:")
                
                for call in api_calls:
                    url = call["url"]
                    line = call["line"]
                    
                    # Check if using correct port
                    if f":{correct_port}" in url:
                        print(f"   ✅ Line {line}: {url}")
                        self.results["correct_endpoints"].append(call)
                        correct_calls += 1
                    elif any(f":{port}" in url for port in incorrect_ports):
                        print(f"   ❌ Line {line}: {url}")
                        self.results["incorrect_endpoints"].append(call)
                        incorrect_calls += 1
                    elif "localhost" in url and ":500" in url:  # Any 5xxx port that's not 5007
                        print(f"   ⚠️  Line {line}: {url} (suspicious port)")
                        self.results["incorrect_endpoints"].append(call)
                        incorrect_calls += 1
                    else:
                        # Relative URLs or external URLs
                        print(f"   ℹ️  Line {line}: {url} (relative/external)")
                        self.results["correct_endpoints"].append(call)
                        correct_calls += 1
                
                print()
        
        # Summary
        self.results["summary"] = {
            "total_files_scanned": len(all_files),
            "files_with_api_calls": len(self.results["files_checked"]),
            "total_api_calls": total_api_calls,
            "correct_calls": correct_calls,
            "incorrect_calls": incorrect_calls,
            "success_rate": (correct_calls / total_api_calls * 100) if total_api_calls > 0 else 0
        }
        
        return self.results
    
    def generate_report(self):
        """Generate detailed report"""
        print("=" * 50)
        print("📊 FRONTEND API CONNECTION REPORT")
        print("=" * 50)
        
        summary = self.results["summary"]
        
        print(f"Files Scanned: {summary['total_files_scanned']}")
        print(f"Files with API Calls: {summary['files_with_api_calls']}")
        print(f"Total API Calls Found: {summary['total_api_calls']}")
        print(f"Correct Endpoints: {summary['correct_calls']} ✅")
        print(f"Incorrect Endpoints: {summary['incorrect_calls']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if self.results["incorrect_endpoints"]:
            print(f"\n❌ INCORRECT ENDPOINTS FOUND:")
            for endpoint in self.results["incorrect_endpoints"]:
                file_name = Path(endpoint["file"]).name
                print(f"   • {file_name}:{endpoint['line']} - {endpoint['url']}")
        
        print(f"\n✅ CONFIGURATION STATUS:")
        if summary['success_rate'] >= 95:
            print("   🎉 EXCELLENT - All endpoints correctly configured!")
        elif summary['success_rate'] >= 80:
            print("   ✅ GOOD - Most endpoints correct, minor issues to fix")
        elif summary['success_rate'] >= 60:
            print("   ⚠️  FAIR - Several endpoints need correction")
        else:
            print("   ❌ POOR - Major endpoint configuration issues")
        
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        if self.results["incorrect_endpoints"]:
            print("   1. Update incorrect endpoints to use port 5007")
            print("   2. Consider using the centralized API config file")
            print("   3. Run this test after making changes")
        else:
            print("   1. All endpoints are correctly configured!")
            print("   2. Consider using centralized API config for future changes")
        
        return self.results

def main():
    """Run frontend API connection analysis"""
    tester = FrontendAPITester("./src")
    
    # Analyze endpoints
    results = tester.analyze_endpoints()
    
    # Generate report
    tester.generate_report()
    
    # Save results
    with open("frontend_api_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Frontend test results saved to: frontend_api_test_results.json")
    
    return results

if __name__ == "__main__":
    main()