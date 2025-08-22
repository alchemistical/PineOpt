"""
Epic 6 API Routes: AI-Powered Strategy Conversion
Advanced Pine Script to Python conversion with AI analysis and UI generation
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Blueprint, request, jsonify
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from research.analysis.ai_strategy_analyzer import AIStrategyAnalyzer
from research.analysis.pynescript_converter import PynescriptConverter
from database.strategy_models import StrategyDatabase

logger = logging.getLogger(__name__)

# Create Blueprint
ai_conversion_bp = Blueprint('ai_conversion', __name__, url_prefix='/api/ai-conversion')

# Global instances
analyzer = None
converter = None
strategy_db = None

def get_analyzer():
    """Get or create AI analyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = AIStrategyAnalyzer()
        logger.info("AI Strategy Analyzer initialized")
    return analyzer

def get_converter():
    """Get or create PyneScript converter instance"""
    global converter
    if converter is None:
        converter = PynescriptConverter()
        logger.info(f"PyneScript Converter initialized (Available: {converter.available})")
    return converter

def get_strategy_db():
    """Get or create strategy database instance"""
    global strategy_db
    if strategy_db is None:
        db_path = Path(__file__).parent.parent / "database" / "pineopt.db"
        strategy_db = StrategyDatabase(str(db_path))
        logger.info("Strategy Database initialized")
    return strategy_db

@ai_conversion_bp.route('/health', methods=['GET'])
def health_check():
    """AI conversion system health check"""
    try:
        analyzer_status = get_analyzer() is not None
        converter_status = get_converter() is not None
        pynescript_available = converter_status and get_converter().available
        
        return jsonify({
            "status": "healthy",
            "success": True,
            "services": {
                "ai_analyzer": "online" if analyzer_status else "offline",
                "pynescript_converter": "online" if converter_status else "offline",
                "pynescript_library": "available" if pynescript_available else "unavailable",
                "strategy_database": "online"
            },
            "features": {
                "ai_code_analysis": True,
                "feature_extraction": True,
                "ui_generation": True,
                "pynescript_integration": pynescript_available,
                "settings_panels": True,
                "performance_estimation": True
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI conversion health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@ai_conversion_bp.route('/analyze', methods=['POST'])
def analyze_strategy():
    """
    AI-powered strategy analysis - extract all features and components
    
    Request body:
    {
        "code": "Pine Script or Python code",
        "language": "pine" or "python",
        "strategy_name": "Optional strategy name"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: code"
            }), 400
        
        code = data['code']
        language = data.get('language', 'pine')
        strategy_name = data.get('strategy_name', 'Unknown Strategy')
        
        if language not in ['pine', 'python']:
            return jsonify({
                "success": False,
                "error": "Language must be 'pine' or 'python'"
            }), 400
        
        # Run AI analysis
        analyzer = get_analyzer()
        features = analyzer.analyze_strategy(code, language)
        
        if strategy_name != 'Unknown Strategy':
            features.strategy_name = strategy_name
        
        logger.info(f"Analysis complete for {features.strategy_name}: {features.strategy_type.value}")
        
        # Convert features to dict for JSON response
        response_data = {
            "success": True,
            "strategy_analysis": {
                "name": features.strategy_name,
                "type": features.strategy_type.value,
                "description": features.description,
                "complexity_score": features.complexity_score,
                "conversion_confidence": features.conversion_confidence,
                "estimated_performance": features.estimated_performance,
                
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.param_type,
                        "default": p.default_value,
                        "min": p.min_value,
                        "max": p.max_value,
                        "title": p.title,
                        "group": p.group
                    }
                    for p in features.parameters
                ],
                
                "indicators": {
                    name: {
                        "name": info.get("name", name),
                        "type": info.get("type", "unknown"),
                        "parameters": info.get("parameters_used", [])
                    }
                    for name, info in features.indicators.items()
                },
                
                "trading_components": {
                    "entry_logic": len(features.entry_logic),
                    "exit_logic": len(features.exit_logic),
                    "risk_management": len(features.risk_management),
                    "filters": len(features.filters)
                },
                
                "entry_conditions": [
                    {
                        "type": logic.logic_type,
                        "conditions": logic.conditions,
                        "indicators": logic.indicators_used,
                        "code": logic.code_snippet
                    }
                    for logic in features.entry_logic
                ],
                
                "exit_conditions": [
                    {
                        "type": logic.logic_type,
                        "conditions": logic.conditions,
                        "indicators": logic.indicators_used,
                        "code": logic.code_snippet
                    }
                    for logic in features.exit_logic
                ],
                
                "risk_management": [
                    {
                        "component": logic.component.value,
                        "conditions": logic.conditions,
                        "code": logic.code_snippet
                    }
                    for logic in features.risk_management
                ],
                
                "timeframes": features.timeframes,
                "regime_detection": features.regime_detection,
                "market_conditions": features.market_conditions,
                "plot_elements": features.plot_elements
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Strategy analysis failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_conversion_bp.route('/convert', methods=['POST'])
def convert_strategy():
    """
    AI-powered strategy conversion with PyneScript integration
    
    Request body:
    {
        "pine_code": "Pine Script code",
        "strategy_name": "Optional strategy name",
        "save_to_db": true/false
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'pine_code' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: pine_code"
            }), 400
        
        pine_code = data['pine_code']
        strategy_name = data.get('strategy_name')
        save_to_db = data.get('save_to_db', False)
        
        # Run AI conversion
        converter = get_converter()
        result = converter.convert_strategy(pine_code, strategy_name)
        
        if not result.success:
            return jsonify({
                "success": False,
                "error": result.error_message or "Conversion failed"
            }), 500
        
        logger.info(f"Conversion successful for {result.strategy_features.strategy_name}")
        
        # Save to database if requested
        strategy_id = None
        if save_to_db:
            try:
                db = get_strategy_db()
                strategy_id = db.create_strategy(
                    name=result.strategy_features.strategy_name,
                    source_code=result.python_code,
                    metadata={
                        "original_pine_code": pine_code,
                        "strategy_type": result.strategy_features.strategy_type.value,
                        "complexity_score": result.strategy_features.complexity_score,
                        "conversion_confidence": result.strategy_features.conversion_confidence,
                        "conversion_method": "ai_pynescript",
                        "conversion_timestamp": datetime.now().isoformat(),
                        "settings_panel": result.settings_panel,
                        "ui_components": result.ui_components
                    }
                )
                logger.info(f"Strategy saved to database with ID: {strategy_id}")
            except Exception as e:
                logger.warning(f"Failed to save strategy to database: {e}")
        
        # Prepare response
        response_data = result.to_dict()
        response_data.update({
            "strategy_id": strategy_id,
            "saved_to_database": save_to_db and strategy_id is not None
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Strategy conversion failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_conversion_bp.route('/validate', methods=['POST'])
def validate_conversion():
    """
    Validate converted strategy for correctness and completeness
    
    Request body:
    {
        "python_code": "Generated Python code",
        "original_pine_code": "Original Pine Script",
        "run_tests": true/false
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'python_code' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: python_code"
            }), 400
        
        python_code = data['python_code']
        original_pine = data.get('original_pine_code', '')
        run_tests = data.get('run_tests', True)
        
        validation_results = {
            "success": True,
            "validation_score": 0.0,
            "checks": {},
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Syntax validation
        try:
            compile(python_code, '<generated>', 'exec')
            validation_results["checks"]["syntax"] = True
            validation_results["validation_score"] += 20
        except SyntaxError as e:
            validation_results["success"] = False
            validation_results["checks"]["syntax"] = False
            validation_results["errors"].append(f"Syntax error: {e}")
        
        # Required imports validation
        required_imports = ['pandas', 'numpy', 'StrategySignals']
        imports_found = []
        for imp in required_imports:
            if imp in python_code:
                imports_found.append(imp)
        
        validation_results["checks"]["imports"] = len(imports_found) == len(required_imports)
        validation_results["validation_score"] += (len(imports_found) / len(required_imports)) * 15
        
        # Strategy function validation
        has_build_signals = 'def build_signals(' in python_code
        validation_results["checks"]["main_function"] = has_build_signals
        if has_build_signals:
            validation_results["validation_score"] += 20
        else:
            validation_results["errors"].append("Missing main build_signals function")
        
        # Parameters validation
        has_params = 'PARAMS = {' in python_code
        validation_results["checks"]["parameters"] = has_params
        if has_params:
            validation_results["validation_score"] += 15
        else:
            validation_results["warnings"].append("No parameters section found")
        
        # Metadata validation
        has_metadata = 'METADATA = StrategyMetadata(' in python_code
        validation_results["checks"]["metadata"] = has_metadata
        if has_metadata:
            validation_results["validation_score"] += 10
        else:
            validation_results["warnings"].append("No metadata section found")
        
        # Technical indicators validation
        indicator_patterns = ['rsi', 'sma', 'ema', 'macd', 'bb', 'atr']
        indicators_found = sum(1 for pattern in indicator_patterns if pattern in python_code.lower())
        validation_results["checks"]["indicators"] = indicators_found > 0
        if indicators_found > 0:
            validation_results["validation_score"] += min(indicators_found * 5, 20)
        
        # Code structure validation
        has_classes = 'class ' in python_code
        has_functions = python_code.count('def ') >= 2  # At least build_signals and one other
        validation_results["checks"]["code_structure"] = has_classes and has_functions
        if has_classes and has_functions:
            validation_results["validation_score"] += 10
        
        # Run basic tests if requested
        if run_tests and validation_results["checks"]["syntax"]:
            try:
                # Test imports
                test_code = f"""
import pandas as pd
import numpy as np
{python_code}
"""
                exec(test_code, {})
                validation_results["checks"]["execution"] = True
                validation_results["validation_score"] += 10
            except Exception as e:
                validation_results["checks"]["execution"] = False
                validation_results["warnings"].append(f"Execution test failed: {str(e)[:100]}")
        
        # Comparison with original Pine Script (if provided)
        if original_pine:
            analyzer = get_analyzer()
            pine_features = analyzer.analyze_strategy(original_pine, "pine")
            python_features = analyzer.analyze_strategy(python_code, "python")
            
            # Compare feature counts
            param_match = len(pine_features.parameters) == len(python_features.parameters)
            indicator_match = len(pine_features.indicators) >= len(python_features.indicators)
            
            validation_results["checks"]["feature_preservation"] = param_match and indicator_match
            if param_match and indicator_match:
                validation_results["validation_score"] += 15
            else:
                validation_results["warnings"].append("Some features may not have been preserved from original")
        
        # Generate suggestions
        if validation_results["validation_score"] < 70:
            validation_results["suggestions"].append("Consider manual code review and testing")
        if not validation_results["checks"].get("parameters", True):
            validation_results["suggestions"].append("Add parameter definitions for strategy customization")
        if indicators_found == 0:
            validation_results["suggestions"].append("Add technical indicator calculations")
        
        # Final score normalization
        validation_results["validation_score"] = min(validation_results["validation_score"], 100.0)
        
        logger.info(f"Validation complete: {validation_results['validation_score']:.1f}% score")
        
        return jsonify({
            "success": True,
            "validation": validation_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_conversion_bp.route('/strategy/<strategy_id>/ui-config', methods=['GET'])
def get_strategy_ui_config(strategy_id: str):
    """Get UI configuration for a converted strategy"""
    try:
        db = get_strategy_db()
        strategy = db.get_strategy(strategy_id)
        
        if not strategy:
            return jsonify({
                "success": False,
                "error": "Strategy not found"
            }), 404
        
        metadata = strategy.metadata or {}
        
        # Extract UI configuration from metadata
        ui_config = {
            "settings_panel": metadata.get("settings_panel", {}),
            "ui_components": metadata.get("ui_components", []),
            "strategy_info": {
                "name": strategy.name,
                "type": metadata.get("strategy_type", "unknown"),
                "complexity_score": metadata.get("complexity_score", 0),
                "conversion_confidence": metadata.get("conversion_confidence", 0)
            },
            "chart_overlays": [
                comp for comp in metadata.get("ui_components", [])
                if comp.get("type") == "chart_overlay"
            ],
            "performance_gauges": [
                comp for comp in metadata.get("ui_components", [])
                if comp.get("type") == "gauge"
            ]
        }
        
        return jsonify({
            "success": True,
            "strategy_id": strategy_id,
            "ui_config": ui_config,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get UI config for strategy {strategy_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_conversion_bp.route('/capabilities', methods=['GET'])
def get_conversion_capabilities():
    """Get AI conversion system capabilities and supported features"""
    try:
        converter = get_converter()
        
        capabilities = {
            "ai_analysis": {
                "feature_extraction": True,
                "strategy_classification": True,
                "complexity_assessment": True,
                "performance_estimation": True,
                "supported_languages": ["pine", "python"]
            },
            
            "conversion_features": {
                "pynescript_integration": converter.available,
                "parameter_extraction": True,
                "ui_generation": True,
                "settings_panels": True,
                "chart_overlays": True,
                "performance_gauges": True,
                "risk_management_detection": True,
                "regime_detection": True
            },
            
            "supported_indicators": list(converter.analyzer.indicator_mappings.keys()),
            
            "strategy_types": [
                "trend_following",
                "mean_reversion", 
                "momentum",
                "breakout",
                "scalping",
                "swing_trading",
                "hybrid"
            ],
            
            "validation_features": {
                "syntax_checking": True,
                "execution_testing": True,
                "feature_preservation": True,
                "code_structure_analysis": True
            }
        }
        
        return jsonify({
            "success": True,
            "capabilities": capabilities,
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get capabilities: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Error handlers
@ai_conversion_bp.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "Strategy code too large. Maximum size is 1MB."
    }), 413

@ai_conversion_bp.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        "success": False,
        "error": "Rate limit exceeded. Please wait before making another request."
    }), 429