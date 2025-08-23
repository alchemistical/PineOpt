"""
Parameter Management API Routes
Handle strategy parameter configurations, validation, and presets
"""

import sys
from pathlib import Path
import json
import sqlite3
import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Create Blueprint
parameter_bp = Blueprint('parameters', __name__, url_prefix='/api/parameters')

def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent / "strategies.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_parameter_tables():
    """Initialize parameter management tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Parameter configurations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parameter_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id TEXT NOT NULL,
            config_name TEXT NOT NULL,
            parameters TEXT NOT NULL,
            description TEXT,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Parameter validation rules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parameter_validation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id TEXT NOT NULL,
            parameter_name TEXT NOT NULL,
            min_value REAL,
            max_value REAL,
            step_value REAL,
            allowed_values TEXT,
            validation_rule TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize tables when module is imported
init_parameter_tables()

@parameter_bp.route('/health', methods=['GET'])
def health_check():
    """Parameter management health check"""
    return jsonify({
        "status": "healthy",
        "service": "Parameter Management",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "parameter_validation",
            "configuration_presets",
            "parameter_optimization",
            "batch_parameter_testing"
        ]
    })

@parameter_bp.route('/strategy/<strategy_id>', methods=['GET'])
def get_strategy_parameters(strategy_id: str):
    """
    Get parameter schema and current values for a strategy
    
    Response includes:
    - Parameter definitions with types and constraints
    - Default values
    - Validation rules
    - Available presets
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get strategy info
        cursor.execute("SELECT name, python_code FROM strategies WHERE id = ?", (strategy_id,))
        strategy = cursor.fetchone()
        
        if not strategy:
            return jsonify({
                "success": False,
                "error": f"Strategy {strategy_id} not found"
            }), 404
        
        # Get parameter validation rules
        cursor.execute("""
            SELECT parameter_name, min_value, max_value, step_value, 
                   allowed_values, validation_rule
            FROM parameter_validation 
            WHERE strategy_id = ?
        """, (strategy_id,))
        
        validation_rules = cursor.fetchall()
        
        # Get parameter configurations/presets
        cursor.execute("""
            SELECT id, config_name, parameters, description, is_default, created_at
            FROM parameter_configs 
            WHERE strategy_id = ?
            ORDER BY is_default DESC, created_at DESC
        """, (strategy_id,))
        
        configs = cursor.fetchall()
        conn.close()
        
        # Try to extract parameters from converted strategy
        parameters = []
        try:
            # Get parameters from intelligent conversion if available
            from intelligent_conversion_routes import IntelligentConverter
            converter = IntelligentConverter()
            
            # This would ideally come from the stored conversion result
            # For now, return a mock parameter set for HYE strategies
            if 'hye' in strategy['name'].lower():
                parameters = [
                    {
                        "name": "small_vwap_period",
                        "default": 8,
                        "min_val": 1,
                        "max_val": 50,
                        "description": "Small VWAP Period",
                        "type": "integer"
                    },
                    {
                        "name": "big_vwap_period",
                        "default": 10,
                        "min_val": 1,
                        "max_val": 50,
                        "description": "Big VWAP Period",
                        "type": "integer"
                    },
                    {
                        "name": "mean_vwap_period",
                        "default": 50,
                        "min_val": 10,
                        "max_val": 200,
                        "description": "Mean VWAP Period",
                        "type": "integer"
                    },
                    {
                        "name": "rsi_period",
                        "default": 14,
                        "min_val": 2,
                        "max_val": 50,
                        "description": "RSI Period",
                        "type": "integer"
                    },
                    {
                        "name": "rsi_ema_period",
                        "default": 3,
                        "min_val": 1,
                        "max_val": 20,
                        "description": "RSI EMA Smoothing Period",
                        "type": "integer"
                    },
                    {
                        "name": "tsv_length",
                        "default": 20,
                        "min_val": 5,
                        "max_val": 100,
                        "description": "TSV Length",
                        "type": "integer"
                    },
                    {
                        "name": "percent_below_to_buy",
                        "default": 2.0,
                        "min_val": 0.1,
                        "max_val": 10.0,
                        "description": "Percent below VWAP to trigger buy",
                        "type": "float"
                    }
                ]
        except Exception as e:
            logger.warning(f"Could not extract parameters: {e}")
        
        # Apply validation rules to parameters
        validation_map = {rule['parameter_name']: dict(rule) for rule in validation_rules}
        
        for param in parameters:
            if param['name'] in validation_map:
                rule = validation_map[param['name']]
                if rule['min_value'] is not None:
                    param['min_val'] = rule['min_value']
                if rule['max_value'] is not None:
                    param['max_val'] = rule['max_value']
                if rule['step_value'] is not None:
                    param['step'] = rule['step_value']
                if rule['allowed_values']:
                    param['options'] = json.loads(rule['allowed_values'])
        
        # Format presets
        presets = []
        for config in configs:
            presets.append({
                "id": config['id'],
                "name": config['config_name'],
                "parameters": json.loads(config['parameters']),
                "description": config['description'],
                "is_default": bool(config['is_default']),
                "created_at": config['created_at']
            })
        
        return jsonify({
            "success": True,
            "strategy_id": strategy_id,
            "strategy_name": strategy['name'],
            "parameters": parameters,
            "presets": presets,
            "validation_rules": len(validation_rules),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get strategy parameters: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@parameter_bp.route('/validate', methods=['POST'])
def validate_parameters():
    """
    Validate parameter values against strategy constraints
    
    Request body:
    {
        "strategy_id": "12",
        "parameters": {
            "rsi_period": 14,
            "small_vwap_period": 8,
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'strategy_id' not in data or 'parameters' not in data:
            return jsonify({
                "success": False,
                "error": "strategy_id and parameters are required"
            }), 400
        
        strategy_id = data['strategy_id']
        parameters = data['parameters']
        
        # Get validation rules
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT parameter_name, min_value, max_value, step_value, 
                   allowed_values, validation_rule
            FROM parameter_validation 
            WHERE strategy_id = ?
        """, (strategy_id,))
        
        validation_rules = cursor.fetchall()
        conn.close()
        
        # Build validation map
        rules_map = {rule['parameter_name']: dict(rule) for rule in validation_rules}
        
        validation_results = {
            "is_valid": True,
            "parameter_results": {},
            "errors": []
        }
        
        # Validate each parameter
        for param_name, param_value in parameters.items():
            param_result = {
                "name": param_name,
                "value": param_value,
                "is_valid": True,
                "warnings": [],
                "errors": []
            }
            
            # Check if we have validation rules for this parameter
            if param_name in rules_map:
                rule = rules_map[param_name]
                
                # Check numeric constraints
                if isinstance(param_value, (int, float)):
                    if rule['min_value'] is not None and param_value < rule['min_value']:
                        param_result['is_valid'] = False
                        param_result['errors'].append(f"Value {param_value} is below minimum {rule['min_value']}")
                    
                    if rule['max_value'] is not None and param_value > rule['max_value']:
                        param_result['is_valid'] = False
                        param_result['errors'].append(f"Value {param_value} is above maximum {rule['max_value']}")
                    
                    if rule['step_value'] is not None:
                        remainder = (param_value - (rule['min_value'] or 0)) % rule['step_value']
                        if abs(remainder) > 1e-10:  # Account for floating point precision
                            param_result['warnings'].append(f"Value should be a multiple of {rule['step_value']}")
                
                # Check allowed values
                if rule['allowed_values']:
                    allowed = json.loads(rule['allowed_values'])
                    if param_value not in allowed:
                        param_result['is_valid'] = False
                        param_result['errors'].append(f"Value must be one of: {', '.join(map(str, allowed))}")
                
                # Apply custom validation rule if present
                if rule['validation_rule']:
                    try:
                        # Simple eval-based validation (in production, use safer validation)
                        validation_expr = rule['validation_rule'].replace('value', str(param_value))
                        if not eval(validation_expr):
                            param_result['is_valid'] = False
                            param_result['errors'].append(f"Custom validation failed: {rule['validation_rule']}")
                    except Exception as e:
                        param_result['warnings'].append(f"Custom validation error: {e}")
            
            validation_results['parameter_results'][param_name] = param_result
            
            if not param_result['is_valid']:
                validation_results['is_valid'] = False
                validation_results['errors'].extend(param_result['errors'])
        
        return jsonify({
            "success": True,
            "validation": validation_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Parameter validation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@parameter_bp.route('/presets', methods=['POST'])
def save_parameter_preset():
    """
    Save a parameter configuration as a preset
    
    Request body:
    {
        "strategy_id": "12",
        "config_name": "Aggressive Settings",
        "parameters": {...},
        "description": "High-frequency trading settings",
        "is_default": false
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['strategy_id', 'config_name', 'parameters']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"{field} is required"
                }), 400
        
        strategy_id = data['strategy_id']
        config_name = data['config_name']
        parameters = data['parameters']
        description = data.get('description', '')
        is_default = data.get('is_default', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # If this is set as default, unset other defaults
        if is_default:
            cursor.execute("""
                UPDATE parameter_configs 
                SET is_default = FALSE 
                WHERE strategy_id = ?
            """, (strategy_id,))
        
        # Save the preset
        cursor.execute("""
            INSERT INTO parameter_configs 
            (strategy_id, config_name, parameters, description, is_default)
            VALUES (?, ?, ?, ?, ?)
        """, (
            strategy_id,
            config_name,
            json.dumps(parameters),
            description,
            is_default
        ))
        
        preset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "preset_id": preset_id,
            "message": f"Parameter preset '{config_name}' saved successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to save parameter preset: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@parameter_bp.route('/presets/<strategy_id>', methods=['GET'])
def get_parameter_presets(strategy_id: str):
    """Get all parameter presets for a strategy"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, config_name, parameters, description, is_default, 
                   created_at, updated_at
            FROM parameter_configs 
            WHERE strategy_id = ?
            ORDER BY is_default DESC, created_at DESC
        """, (strategy_id,))
        
        presets = cursor.fetchall()
        conn.close()
        
        preset_list = []
        for preset in presets:
            preset_list.append({
                "id": preset['id'],
                "name": preset['config_name'],
                "parameters": json.loads(preset['parameters']),
                "description": preset['description'],
                "is_default": bool(preset['is_default']),
                "created_at": preset['created_at'],
                "updated_at": preset['updated_at']
            })
        
        return jsonify({
            "success": True,
            "strategy_id": strategy_id,
            "presets": preset_list,
            "total": len(preset_list),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get parameter presets: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@parameter_bp.route('/optimize', methods=['POST'])
def optimize_parameters():
    """
    Run parameter optimization for a strategy
    
    Request body:
    {
        "strategy_id": "12",
        "optimization_method": "grid_search|random_search|bayesian",
        "parameter_ranges": {
            "rsi_period": {"min": 10, "max": 20, "step": 2},
            "small_vwap_period": {"min": 5, "max": 15, "step": 1}
        },
        "optimization_metric": "sharpe_ratio|total_return|max_drawdown",
        "max_iterations": 100
    }
    """
    try:
        data = request.get_json()
        
        strategy_id = data.get('strategy_id')
        if not strategy_id:
            return jsonify({
                "success": False,
                "error": "strategy_id is required"
            }), 400
        
        optimization_method = data.get('optimization_method', 'grid_search')
        parameter_ranges = data.get('parameter_ranges', {})
        optimization_metric = data.get('optimization_metric', 'sharpe_ratio')
        max_iterations = data.get('max_iterations', 50)
        
        # For now, return a mock optimization result
        # In a full implementation, this would run actual backtests
        
        import random
        import time
        
        # Simulate optimization process
        time.sleep(1)  # Simulate computation time
        
        # Generate mock results
        optimization_results = {
            "method": optimization_method,
            "metric": optimization_metric,
            "iterations_run": min(max_iterations, len(parameter_ranges) * 10),
            "best_parameters": {},
            "best_score": random.uniform(0.5, 2.5),
            "parameter_sensitivity": {},
            "optimization_history": []
        }
        
        # Generate best parameters
        for param_name, param_range in parameter_ranges.items():
            if 'min' in param_range and 'max' in param_range:
                best_val = random.uniform(param_range['min'], param_range['max'])
                if 'step' in param_range:
                    best_val = round(best_val / param_range['step']) * param_range['step']
                optimization_results['best_parameters'][param_name] = best_val
                
                # Generate sensitivity analysis
                optimization_results['parameter_sensitivity'][param_name] = {
                    'importance': random.uniform(0.1, 1.0),
                    'correlation_with_metric': random.uniform(-0.5, 0.5)
                }
        
        # Generate optimization history
        for i in range(min(10, optimization_results['iterations_run'])):
            optimization_results['optimization_history'].append({
                'iteration': i + 1,
                'score': random.uniform(0.1, optimization_results['best_score']),
                'parameters': {k: random.uniform(v['min'], v['max']) for k, v in parameter_ranges.items() if 'min' in v and 'max' in v}
            })
        
        return jsonify({
            "success": True,
            "strategy_id": strategy_id,
            "optimization_results": optimization_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Parameter optimization failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@parameter_bp.route('/presets/<preset_id>', methods=['DELETE'])
def delete_parameter_preset(preset_id: str):
    """Delete a parameter preset"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM parameter_configs WHERE id = ?", (preset_id,))
        
        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "error": f"Preset {preset_id} not found"
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Preset {preset_id} deleted successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to delete parameter preset: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Export the blueprint
__all__ = ['parameter_bp']