"""
Epic 5: Strategy Management API Routes
Handles strategy upload, validation, and CRUD operations
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from database.strategy_models import (
    StrategyDatabase, StrategyMetadata, LanguageType, ValidationStatus,
    ValidationResult, ParameterType
)
from research.validation.code_validator import CodeValidator
from research.analysis.strategy_profiler import StrategyProfiler

logger = logging.getLogger(__name__)

# Create Blueprint
strategy_bp = Blueprint('strategies', __name__, url_prefix='/api/strategies')

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.py', '.pine'}
UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads' / 'strategies'

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Initialize services
db = StrategyDatabase(str(Path(__file__).parent.parent / 'database' / 'pineopt.db'))
validator = CodeValidator()

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def detect_language(filename: str, content: str) -> LanguageType:
    """Detect strategy language from filename and content"""
    extension = Path(filename).suffix.lower()
    
    if extension == '.py':
        return LanguageType.PYTHON
    elif extension == '.pine':
        return LanguageType.PINE
    
    # Content-based detection
    if any(pattern in content.lower() for pattern in ['def ', 'class ', 'import ', 'from ']):
        return LanguageType.PYTHON
    elif any(pattern in content for pattern in ['//@version', 'strategy(', 'indicator(']):
        return LanguageType.PINE
    
    # Default to Python
    return LanguageType.PYTHON

@strategy_bp.route('/upload', methods=['POST'])
def upload_strategy():
    """
    Upload and validate a strategy file
    
    Form Data:
    - file: Strategy file (.py or .pine)
    - name: Optional strategy name
    - description: Optional description
    - author: Optional author name
    - tags: Optional comma-separated tags
    """
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Read file content
        file_content = file.read().decode('utf-8')
        file_size = len(file_content.encode('utf-8'))
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        if not file_content.strip():
            return jsonify({
                'success': False,
                'error': 'File cannot be empty'
            }), 400
        
        # Extract metadata from form
        strategy_name = request.form.get('name', Path(file.filename).stem)
        description = request.form.get('description', '')
        author = request.form.get('author', 'Unknown')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        # Detect language
        language = detect_language(file.filename, file_content)
        
        # Create strategy metadata
        strategy = StrategyMetadata(
            name=strategy_name,
            description=description,
            author=author,
            language=language,
            original_filename=secure_filename(file.filename),
            file_size=file_size,
            source_code=file_content,
            tags=tags,
            validation_status=ValidationStatus.PENDING
        )
        
        # Validate strategy code
        logger.info(f"Validating strategy: {strategy_name} ({language.value})")
        validation_results = validator.validate_strategy(
            file_content, 
            language, 
            file.filename
        )
        
        # Determine overall validation status
        has_errors = any(r.status == "fail" for r in validation_results)
        has_warnings = any(r.status == "warning" for r in validation_results)
        
        if has_errors:
            strategy.validation_status = ValidationStatus.INVALID
        elif has_warnings:
            strategy.validation_status = ValidationStatus.VALID  # Valid with warnings
        else:
            strategy.validation_status = ValidationStatus.VALID
        
        strategy.validation_errors = [
            {
                'type': r.type,
                'status': r.status, 
                'message': r.message,
                'line_number': r.line_number,
                'column_number': r.column_number,
                'details': r.details
            } for r in validation_results
        ]
        strategy.validation_timestamp = datetime.utcnow()
        
        # Extract parameters from validation results
        for result in validation_results:
            if result.type == "parameters" and result.details:
                if "parameters" in result.details:
                    strategy.parameters = {
                        param["name"]: {
                            "default": param.get("default"),
                            "type": param.get("type", "str"),
                            "description": param.get("description", "")
                        }
                        for param in result.details["parameters"]
                    }
                
                if "dependencies" in result.details:
                    strategy.dependencies = result.details["dependencies"]
                
                if "timeframes" in result.details:
                    strategy.supported_timeframes = result.details["timeframes"]
        
        # Save to database
        strategy_id = db.save_strategy(strategy)
        
        # Save validation results
        db.save_validation_results(strategy_id, validation_results)
        
        # Generate validation summary
        validation_summary = validator.get_validation_summary(validation_results)
        
        logger.info(f"Strategy uploaded successfully: {strategy_id}")
        
        return jsonify({
            'success': True,
            'strategy_id': strategy_id,
            'validation': validation_summary,
            'strategy': {
                'id': strategy_id,
                'name': strategy.name,
                'language': strategy.language.value,
                'validation_status': strategy.validation_status.value,
                'file_size': strategy.file_size,
                'parameters': strategy.parameters,
                'dependencies': strategy.dependencies,
                'tags': strategy.tags
            }
        })
        
    except Exception as e:
        logger.error(f"Strategy upload failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('', methods=['GET'])
def list_strategies():
    """
    List strategies with filtering and pagination
    
    Query Parameters:
    - author: Filter by author
    - language: Filter by language (python|pine)
    - tags: Comma-separated tags to filter by
    - search: Search in name, description, and code
    - limit: Number of results (default 50, max 100)
    - offset: Pagination offset (default 0)
    - validation_status: Filter by validation status
    """
    try:
        # Parse query parameters
        author = request.args.get('author')
        language_param = request.args.get('language')
        tags_param = request.args.get('tags')
        search_query = request.args.get('search')
        validation_status_param = request.args.get('validation_status')
        limit = min(request.args.get('limit', 50, type=int), 100)
        offset = max(request.args.get('offset', 0, type=int), 0)
        
        # Parse language
        language = None
        if language_param:
            try:
                language = LanguageType(language_param.lower())
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Invalid language: {language_param}'
                }), 400
        
        # Parse tags
        tags = None
        if tags_param:
            tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
        
        # Get strategies from database
        strategies = db.list_strategies(
            author=author,
            language=language,
            tags=tags,
            search_query=search_query,
            limit=limit,
            offset=offset
        )
        
        # Filter by validation status if specified
        if validation_status_param:
            try:
                status_filter = ValidationStatus(validation_status_param.lower())
                strategies = [s for s in strategies if s.validation_status == status_filter]
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Invalid validation status: {validation_status_param}'
                }), 400
        
        # Convert to response format
        strategy_list = []
        for strategy in strategies:
            strategy_list.append({
                'id': strategy.id,
                'name': strategy.name,
                'description': strategy.description,
                'author': strategy.author,
                'version': strategy.version,
                'language': strategy.language.value,
                'validation_status': strategy.validation_status.value,
                'file_size': strategy.file_size,
                'parameters_count': len(strategy.parameters),
                'dependencies_count': len(strategy.dependencies),
                'tags': strategy.tags,
                'upload_count': strategy.upload_count,
                'backtest_count': strategy.backtest_count,
                'created_at': strategy.created_at.isoformat() if strategy.created_at else None,
                'updated_at': strategy.updated_at.isoformat() if strategy.updated_at else None,
                'last_used': strategy.last_used.isoformat() if strategy.last_used else None
            })
        
        return jsonify({
            'success': True,
            'strategies': strategy_list,
            'count': len(strategy_list),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(strategy_list) == limit
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to list strategies: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/<strategy_id>', methods=['GET'])
def get_strategy(strategy_id: str):
    """Get detailed strategy information"""
    try:
        strategy = db.get_strategy(strategy_id)
        if not strategy:
            return jsonify({
                'success': False,
                'error': 'Strategy not found'
            }), 404
        
        # Get validation results
        validation_results = db.get_validation_results(strategy_id)
        validation_summary = validator.get_validation_summary(validation_results)
        
        # Build response
        response = {
            'success': True,
            'strategy': {
                'id': strategy.id,
                'name': strategy.name,
                'description': strategy.description,
                'author': strategy.author,
                'version': strategy.version,
                'language': strategy.language.value,
                'original_filename': strategy.original_filename,
                'file_size': strategy.file_size,
                'source_code': strategy.source_code,
                'parameters': strategy.parameters,
                'dependencies': strategy.dependencies,
                'supported_timeframes': strategy.supported_timeframes,
                'supported_assets': strategy.supported_assets,
                'tags': strategy.tags,
                'validation_status': strategy.validation_status.value,
                'upload_count': strategy.upload_count,
                'backtest_count': strategy.backtest_count,
                'created_at': strategy.created_at.isoformat() if strategy.created_at else None,
                'updated_at': strategy.updated_at.isoformat() if strategy.updated_at else None,
                'last_used': strategy.last_used.isoformat() if strategy.last_used else None
            },
            'validation': validation_summary,
            'validation_details': [
                {
                    'type': r.type,
                    'status': r.status,
                    'message': r.message,
                    'line_number': r.line_number,
                    'column_number': r.column_number,
                    'details': r.details
                } for r in validation_results
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Failed to get strategy {strategy_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/<strategy_id>', methods=['PUT'])
def update_strategy(strategy_id: str):
    """Update strategy metadata"""
    try:
        strategy = db.get_strategy(strategy_id)
        if not strategy:
            return jsonify({
                'success': False,
                'error': 'Strategy not found'
            }), 404
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update allowed fields
        if 'name' in data:
            strategy.name = data['name']
        if 'description' in data:
            strategy.description = data['description']
        if 'author' in data:
            strategy.author = data['author']
        if 'version' in data:
            strategy.version = data['version']
        if 'tags' in data:
            strategy.tags = data['tags'] if isinstance(data['tags'], list) else []
        if 'parameters' in data:
            strategy.parameters = data['parameters']
        if 'supported_timeframes' in data:
            strategy.supported_timeframes = data['supported_timeframes']
        if 'supported_assets' in data:
            strategy.supported_assets = data['supported_assets']
        
        # Save updates
        db.save_strategy(strategy)
        
        return jsonify({
            'success': True,
            'message': 'Strategy updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to update strategy {strategy_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/<strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id: str):
    """Delete a strategy"""
    try:
        success = db.delete_strategy(strategy_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Strategy not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Strategy deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to delete strategy {strategy_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/<strategy_id>/validate', methods=['POST'])
def revalidate_strategy(strategy_id: str):
    """Re-validate a strategy"""
    try:
        strategy = db.get_strategy(strategy_id)
        if not strategy:
            return jsonify({
                'success': False,
                'error': 'Strategy not found'
            }), 404
        
        # Re-validate strategy
        validation_results = validator.validate_strategy(
            strategy.source_code,
            strategy.language,
            strategy.original_filename
        )
        
        # Update validation status
        has_errors = any(r.status == "fail" for r in validation_results)
        has_warnings = any(r.status == "warning" for r in validation_results)
        
        if has_errors:
            strategy.validation_status = ValidationStatus.INVALID
        elif has_warnings:
            strategy.validation_status = ValidationStatus.VALID
        else:
            strategy.validation_status = ValidationStatus.VALID
        
        strategy.validation_timestamp = datetime.utcnow()
        
        # Save updates
        db.save_strategy(strategy)
        db.save_validation_results(strategy_id, validation_results)
        
        # Generate summary
        validation_summary = validator.get_validation_summary(validation_results)
        
        return jsonify({
            'success': True,
            'validation': validation_summary,
            'validation_details': [
                {
                    'type': r.type,
                    'status': r.status,
                    'message': r.message,
                    'line_number': r.line_number,
                    'column_number': r.column_number,
                    'details': r.details
                } for r in validation_results
            ]
        })
        
    except Exception as e:
        logger.error(f"Failed to revalidate strategy {strategy_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/stats', methods=['GET'])
def get_strategy_stats():
    """Get strategy statistics"""
    try:
        stats = db.get_strategy_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get strategy stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/<strategy_id>/profile', methods=['POST'])
def generate_strategy_profile(strategy_id: str):
    """Generate AI-powered strategy analysis and profile"""
    try:
        strategy = db.get_strategy(strategy_id)
        
        if not strategy:
            return jsonify({
                'success': False,
                'error': 'Strategy not found'
            }), 404
        
        # Initialize strategy profiler
        profiler = StrategyProfiler()
        
        # Generate comprehensive profile
        profile = profiler.profile_strategy(
            strategy_id=strategy.id,
            name=strategy.name,
            source_code=strategy.source_code,
            language=strategy.language.value,
            author=strategy.author
        )
        
        # Convert profile to response format
        profile_data = {
            'strategy_id': profile.strategy_id,
            'analysis_summary': {
                'strategy_type': profile.strategy_type,
                'complexity_score': profile.complexity_score,
                'lines_of_code': profile.lines_of_code,
                'indicators_used': profile.indicators_used,
                'risk_level': profile.expected_risk_level,
                'trading_frequency': profile.expected_frequency
            },
            'technical_analysis': {
                'indicators_detected': profile.indicators_used,
                'signal_types': profile.signal_types,
                'has_risk_management': profile.has_risk_management,
                'has_stop_loss': profile.has_stop_loss,
                'has_position_sizing': profile.has_position_sizing
            },
            'ai_insights': {
                'summary': profile.ai_summary,
                'strengths': profile.ai_strengths,
                'weaknesses': profile.ai_weaknesses,
                'recommendations': profile.ai_recommendations,
                'market_suitability': profile.ai_market_suitability
            },
            'full_report': profile.full_report,
            'generated_at': profile.analysis_timestamp.isoformat()
        }
        
        return jsonify({
            'success': True,
            'profile': profile_data
        })
        
    except Exception as e:
        logger.error(f"Strategy profiling failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/health', methods=['GET'])
def health_check():
    """Strategy management health check"""
    try:
        # Test database connection
        stats = db.get_strategy_stats()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'services': {
                'database': 'online',
                'validator': 'online',
                'file_upload': 'online'
            },
            'stats': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Strategy management health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500