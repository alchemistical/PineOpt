"""
Epic 5: Strategy Code Validation Engine
Validates Python and Pine Script strategies for syntax, security, and dependencies
"""

import ast
import re
import sys
import importlib.util
from typing import List, Dict, Any, Optional, Tuple, Set
import logging
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.append('.')

from database.strategy_models import ValidationResult, LanguageType, StrategyParameter, ParameterType

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityIssue:
    level: SecurityLevel
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

class CodeValidator:
    """Main code validation engine for Python and Pine Script strategies"""
    
    # Allowed Python imports for strategies
    ALLOWED_IMPORTS = {
        # Standard library
        'math', 'datetime', 'decimal', 're', 'json', 'typing', 
        'collections', 'itertools', 'functools', 'operator',
        
        # Data analysis
        'pandas', 'numpy', 'scipy',
        
        # Technical analysis
        'ta', 'talib', 'pandas_ta',
        
        # Visualization (for research)
        'matplotlib', 'seaborn', 'plotly',
        
        # Scientific computing
        'sklearn', 'statsmodels',
        
        # Strategy framework
        'pine2py', 'shared'
    }
    
    # Dangerous operations that are completely blocked
    BLOCKED_OPERATIONS = {
        'open', 'file', 'input', 'raw_input', '__import__',
        'eval', 'exec', 'compile', 'globals', 'locals',
        'vars', 'dir', 'hasattr', 'getattr', 'setattr', 'delattr',
        'subprocess', 'os', 'sys', 'socket', 'urllib', 'requests',
        'http', 'ftplib', 'smtplib', 'poplib', 'imaplib',
        'threading', 'multiprocessing', 'asyncio',
        'ctypes', 'mmap', 'tempfile', 'shutil', 'pathlib',
        'pickle', 'dill', 'joblib'
    }
    
    # Allowed built-in functions
    ALLOWED_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
        'float', 'int', 'len', 'list', 'map', 'max', 'min', 'range',
        'round', 'set', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip'
    }
    
    def validate_strategy(self, source_code: str, language: LanguageType, 
                         filename: Optional[str] = None) -> List[ValidationResult]:
        """Main validation entry point"""
        results = []
        
        try:
            # Basic checks
            if not source_code.strip():
                results.append(ValidationResult(
                    type="syntax",
                    status="fail", 
                    message="Strategy code cannot be empty"
                ))
                return results
            
            # Language-specific validation
            if language == LanguageType.PYTHON:
                results.extend(self._validate_python(source_code, filename))
            elif language == LanguageType.PINE:
                results.extend(self._validate_pine(source_code, filename))
            else:
                results.append(ValidationResult(
                    type="syntax",
                    status="fail",
                    message=f"Unsupported language: {language}"
                ))
            
            # Extract strategy metadata
            metadata_result = self._extract_metadata(source_code, language)
            if metadata_result:
                results.append(metadata_result)
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            results.append(ValidationResult(
                type="syntax",
                status="error",
                message=f"Validation engine error: {str(e)}"
            ))
        
        return results
    
    def _validate_python(self, source_code: str, filename: Optional[str]) -> List[ValidationResult]:
        """Validate Python strategy code"""
        results = []
        
        # Syntax validation
        syntax_results = self._validate_python_syntax(source_code)
        results.extend(syntax_results)
        
        if any(r.status == "fail" for r in syntax_results):
            return results  # Don't continue if syntax is invalid
        
        # Security validation
        security_results = self._validate_python_security(source_code)
        results.extend(security_results)
        
        # Import validation
        import_results = self._validate_python_imports(source_code)
        results.extend(import_results)
        
        # Strategy structure validation
        structure_results = self._validate_python_structure(source_code)
        results.extend(structure_results)
        
        return results
    
    def _validate_python_syntax(self, source_code: str) -> List[ValidationResult]:
        """Validate Python syntax"""
        results = []
        
        try:
            # Parse AST
            tree = ast.parse(source_code)
            
            results.append(ValidationResult(
                type="syntax",
                status="pass",
                message="Python syntax is valid"
            ))
            
            # Store AST for further analysis
            self._ast_tree = tree
            
        except SyntaxError as e:
            results.append(ValidationResult(
                type="syntax",
                status="fail",
                message=f"Python syntax error: {e.msg}",
                line_number=e.lineno,
                column_number=e.offset
            ))
        except Exception as e:
            results.append(ValidationResult(
                type="syntax", 
                status="error",
                message=f"Syntax validation error: {str(e)}"
            ))
        
        return results
    
    def _validate_python_security(self, source_code: str) -> List[ValidationResult]:
        """Validate Python code for security issues"""
        results = []
        security_issues = []
        
        try:
            if hasattr(self, '_ast_tree'):
                security_issues = self._analyze_ast_security(self._ast_tree)
            
            # Text-based security checks
            security_issues.extend(self._analyze_text_security(source_code))
            
            # Convert security issues to validation results
            for issue in security_issues:
                status = "fail" if issue.level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL] else "warning"
                
                results.append(ValidationResult(
                    type="security",
                    status=status,
                    message=issue.message,
                    line_number=issue.line_number,
                    details={
                        "level": issue.level.value,
                        "suggestion": issue.suggestion
                    }
                ))
            
            if not security_issues:
                results.append(ValidationResult(
                    type="security",
                    status="pass",
                    message="No security issues detected"
                ))
            
        except Exception as e:
            results.append(ValidationResult(
                type="security",
                status="error", 
                message=f"Security validation error: {str(e)}"
            ))
        
        return results
    
    def _analyze_ast_security(self, tree: ast.AST) -> List[SecurityIssue]:
        """Analyze AST for security issues"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.BLOCKED_OPERATIONS:
                        issues.append(SecurityIssue(
                            level=SecurityLevel.CRITICAL,
                            message=f"Blocked function call: {func_name}()",
                            line_number=node.lineno,
                            suggestion=f"Remove {func_name}() call - not allowed in strategies"
                        ))
            
            # Check for attribute access to blocked modules
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id in self.BLOCKED_OPERATIONS:
                        issues.append(SecurityIssue(
                            level=SecurityLevel.HIGH,
                            message=f"Access to blocked module: {node.value.id}.{node.attr}",
                            line_number=node.lineno
                        ))
            
            # Check for imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                issues.extend(self._check_import_security(node))
        
        return issues
    
    def _check_import_security(self, node: ast.AST) -> List[SecurityIssue]:
        """Check import statements for security issues"""
        issues = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                if module_name not in self.ALLOWED_IMPORTS:
                    issues.append(SecurityIssue(
                        level=SecurityLevel.HIGH,
                        message=f"Blocked import: {alias.name}",
                        line_number=node.lineno,
                        suggestion=f"Use allowed alternatives for {module_name}"
                    ))
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split('.')[0]
                if module_name not in self.ALLOWED_IMPORTS:
                    issues.append(SecurityIssue(
                        level=SecurityLevel.HIGH,
                        message=f"Blocked import from: {node.module}",
                        line_number=node.lineno
                    ))
        
        return issues
    
    def _analyze_text_security(self, source_code: str) -> List[SecurityIssue]:
        """Text-based security analysis"""
        issues = []
        lines = source_code.split('\n')
        
        # Pattern matching for suspicious code
        suspicious_patterns = [
            (r'__import__\s*\(', SecurityLevel.CRITICAL, "Dynamic import detected"),
            (r'eval\s*\(', SecurityLevel.CRITICAL, "eval() function call detected"),
            (r'exec\s*\(', SecurityLevel.CRITICAL, "exec() function call detected"), 
            (r'open\s*\(', SecurityLevel.HIGH, "File operation detected"),
            (r'urllib|requests|http', SecurityLevel.HIGH, "Network operation detected"),
            (r'subprocess|os\.system', SecurityLevel.CRITICAL, "System command execution detected"),
            (r'globals\(\)|locals\(\)', SecurityLevel.HIGH, "Access to global/local namespace"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, level, message in suspicious_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        level=level,
                        message=message,
                        line_number=i,
                        suggestion="Remove or replace with allowed alternatives"
                    ))
        
        return issues
    
    def _validate_python_imports(self, source_code: str) -> List[ValidationResult]:
        """Validate and extract Python imports"""
        results = []
        dependencies = []
        
        try:
            tree = ast.parse(source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
            
            # Check if dependencies are available
            unavailable_deps = []
            for dep in dependencies:
                if not self._check_dependency_available(dep):
                    unavailable_deps.append(dep)
            
            if unavailable_deps:
                results.append(ValidationResult(
                    type="dependencies",
                    status="warning",
                    message=f"Unavailable dependencies: {', '.join(unavailable_deps)}",
                    details={"dependencies": unavailable_deps}
                ))
            
            results.append(ValidationResult(
                type="dependencies",
                status="pass",
                message=f"Found {len(dependencies)} dependencies",
                details={"dependencies": dependencies}
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                type="dependencies",
                status="error",
                message=f"Import validation error: {str(e)}"
            ))
        
        return results
    
    def _validate_python_structure(self, source_code: str) -> List[ValidationResult]:
        """Validate Python strategy structure"""
        results = []
        
        try:
            tree = ast.parse(source_code)
            
            # Look for strategy-specific patterns
            has_strategy_class = False
            has_generate_signals = False
            has_strategy_function = False
            
            for node in ast.walk(tree):
                # Check for strategy class
                if isinstance(node, ast.ClassDef):
                    if 'strategy' in node.name.lower():
                        has_strategy_class = True
                
                # Check for signal generation function
                if isinstance(node, ast.FunctionDef):
                    if node.name in ['generate_signals', 'build_signals', 'get_signals']:
                        has_generate_signals = True
                    if 'strategy' in node.name.lower():
                        has_strategy_function = True
            
            # Validate structure
            if has_strategy_class or has_strategy_function:
                results.append(ValidationResult(
                    type="parameters",
                    status="pass",
                    message="Strategy structure detected"
                ))
            else:
                results.append(ValidationResult(
                    type="parameters",
                    status="warning",
                    message="No clear strategy structure found",
                    details={"suggestion": "Consider adding a strategy class or function"}
                ))
            
            if has_generate_signals:
                results.append(ValidationResult(
                    type="parameters", 
                    status="pass",
                    message="Signal generation function found"
                ))
            
        except Exception as e:
            results.append(ValidationResult(
                type="parameters",
                status="error",
                message=f"Structure validation error: {str(e)}"
            ))
        
        return results
    
    def _validate_pine(self, source_code: str, filename: Optional[str]) -> List[ValidationResult]:
        """Validate Pine Script code (basic validation)"""
        results = []
        
        # Basic Pine Script validation
        pine_patterns = [
            (r'//@version=\s*[45]', "Pine Script version detected"),
            (r'strategy\s*\(', "Strategy declaration found"),
            (r'indicator\s*\(', "Indicator declaration found"),
            (r'ta\.\w+\s*\(', "Technical analysis functions found"),
            (r'strategy\.(entry|exit|close)', "Strategy actions found")
        ]
        
        found_patterns = []
        for pattern, description in pine_patterns:
            if re.search(pattern, source_code, re.MULTILINE):
                found_patterns.append(description)
        
        if found_patterns:
            results.append(ValidationResult(
                type="syntax",
                status="pass", 
                message=f"Pine Script structure valid: {', '.join(found_patterns)}"
            ))
        else:
            results.append(ValidationResult(
                type="syntax",
                status="warning",
                message="No Pine Script patterns detected"
            ))
        
        # Check for basic syntax issues
        if source_code.count('(') != source_code.count(')'):
            results.append(ValidationResult(
                type="syntax",
                status="fail",
                message="Mismatched parentheses"
            ))
        
        if source_code.count('[') != source_code.count(']'):
            results.append(ValidationResult(
                type="syntax", 
                status="fail",
                message="Mismatched brackets"
            ))
        
        return results
    
    def _extract_metadata(self, source_code: str, language: LanguageType) -> Optional[ValidationResult]:
        """Extract strategy metadata from code"""
        metadata = {}
        
        try:
            if language == LanguageType.PYTHON:
                metadata = self._extract_python_metadata(source_code)
            elif language == LanguageType.PINE:
                metadata = self._extract_pine_metadata(source_code)
            
            if metadata:
                return ValidationResult(
                    type="parameters",
                    status="pass",
                    message="Strategy metadata extracted",
                    details=metadata
                )
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
        
        return None
    
    def _extract_python_metadata(self, source_code: str) -> Dict[str, Any]:
        """Extract metadata from Python strategy"""
        metadata = {
            "parameters": [],
            "timeframes": [],
            "assets": []
        }
        
        # Look for common parameter patterns
        param_patterns = [
            r'(\w+)_length\s*=\s*(\d+)',
            r'(\w+)_period\s*=\s*(\d+)', 
            r'(\w+)_threshold\s*=\s*([\d.]+)',
            r'def\s+\w+\([^)]*(\w+)\s*=\s*([\d.]+)',
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, source_code)
            for match in matches:
                if len(match) >= 2:
                    param_name = match[0] if match[0] else "parameter"
                    param_value = match[1]
                    metadata["parameters"].append({
                        "name": param_name,
                        "default": param_value,
                        "type": "int" if param_value.isdigit() else "float"
                    })
        
        # Look for timeframe references
        timeframe_patterns = [r'"([0-9]+[mhd])"', r"'([0-9]+[mhd])'"]
        for pattern in timeframe_patterns:
            matches = re.findall(pattern, source_code)
            metadata["timeframes"].extend(matches)
        
        return metadata
    
    def _extract_pine_metadata(self, source_code: str) -> Dict[str, Any]:
        """Extract metadata from Pine Script"""
        metadata = {
            "parameters": [],
            "timeframes": [],
            "assets": []
        }
        
        # Extract input parameters
        input_pattern = r'(\w+)\s*=\s*input(?:\.(\w+))?\s*\(([^)]+)\)'
        matches = re.findall(input_pattern, source_code, re.MULTILINE)
        
        for match in matches:
            param_name, param_type, param_args = match
            # Parse default value from arguments
            default_match = re.search(r'([^,\s]+)', param_args)
            default_value = default_match.group(1) if default_match else ""
            
            metadata["parameters"].append({
                "name": param_name,
                "type": param_type or "int",
                "default": default_value.strip('"\'')
            })
        
        return metadata
    
    def _check_dependency_available(self, dep_name: str) -> bool:
        """Check if a dependency is available"""
        try:
            # Check if it's a standard library module
            if dep_name in sys.stdlib_module_names:
                return True
            
            # Try to find the module
            spec = importlib.util.find_spec(dep_name)
            return spec is not None
            
        except (ImportError, ModuleNotFoundError, ValueError):
            return False
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate validation summary"""
        summary = {
            "total_checks": len(results),
            "passed": len([r for r in results if r.status == "pass"]),
            "failed": len([r for r in results if r.status == "fail"]),
            "warnings": len([r for r in results if r.status == "warning"]),
            "errors": len([r for r in results if r.status == "error"]),
            "is_valid": all(r.status != "fail" for r in results),
            "has_warnings": any(r.status == "warning" for r in results),
            "by_type": {}
        }
        
        # Group by type
        for result in results:
            if result.type not in summary["by_type"]:
                summary["by_type"][result.type] = []
            summary["by_type"][result.type].append({
                "status": result.status,
                "message": result.message,
                "line": result.line_number
            })
        
        return summary