"""
Epic 5: Strategy Management - Database Models
Handles strategy storage, validation, and metadata management
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class LanguageType(Enum):
    PYTHON = "python"
    PINE = "pine"

class ValidationStatus(Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"

class ParameterType(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "str"
    LIST = "list"

@dataclass
class StrategyParameter:
    name: str
    type: ParameterType
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: Optional[str] = None
    is_required: bool = True
    validation_rules: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = {}

@dataclass
class StrategyDependency:
    name: str
    type: str  # 'import', 'library', 'module'
    version_requirement: Optional[str] = None
    is_standard_library: bool = False
    is_available: bool = False
    installation_command: Optional[str] = None

@dataclass
class ValidationResult:
    type: str  # 'syntax', 'security', 'dependencies', 'parameters'
    status: str  # 'pass', 'fail', 'warning'
    message: str
    details: Dict[str, Any] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

@dataclass
class StrategyMetadata:
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    author: str = "Unknown"
    version: str = "1.0"
    language: LanguageType = LanguageType.PYTHON
    original_filename: Optional[str] = None
    file_size: int = 0
    source_code: str = ""
    parameters: Dict[str, Any] = None
    dependencies: List[str] = None
    supported_timeframes: List[str] = None
    supported_assets: List[str] = None
    tags: List[str] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_errors: List[Dict[str, Any]] = None
    validation_timestamp: Optional[datetime] = None
    upload_count: int = 1
    backtest_count: int = 0
    last_used: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.supported_timeframes is None:
            self.supported_timeframes = ["1h", "4h", "1d"]
        if self.supported_assets is None:
            self.supported_assets = ["BTCUSDT"]
        if self.tags is None:
            self.tags = []
        if self.validation_errors is None:
            self.validation_errors = []

class StrategyDatabase:
    """Database access layer for strategy management"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize strategy management tables"""
        try:
            # Read and execute schema
            import os
            schema_path = os.path.join(os.path.dirname(__file__), 'strategy_schema.sql')
            
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            with sqlite3.connect(self.db_path) as conn:
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Execute schema
                conn.executescript(schema_sql)
                conn.commit()
                
            logger.info("Strategy database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize strategy database: {e}")
            raise
    
    def save_strategy(self, strategy: StrategyMetadata) -> str:
        """Save or update a strategy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                if strategy.id:
                    # Update existing strategy
                    sql = """
                    UPDATE strategies SET
                        name = ?, description = ?, author = ?, version = ?,
                        language = ?, original_filename = ?, file_size = ?,
                        source_code = ?, parameters = ?, dependencies = ?,
                        supported_timeframes = ?, supported_assets = ?, tags = ?,
                        validation_status = ?, validation_errors = ?,
                        validation_timestamp = ?, upload_count = upload_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND is_deleted = FALSE
                    """
                    
                    params = (
                        strategy.name, strategy.description, strategy.author, strategy.version,
                        strategy.language.value, strategy.original_filename, strategy.file_size,
                        strategy.source_code, json.dumps(strategy.parameters), 
                        json.dumps(strategy.dependencies), json.dumps(strategy.supported_timeframes),
                        json.dumps(strategy.supported_assets), json.dumps(strategy.tags),
                        strategy.validation_status.value, json.dumps(strategy.validation_errors),
                        strategy.validation_timestamp, strategy.id
                    )
                    
                    conn.execute(sql, params)
                    strategy_id = strategy.id
                    
                else:
                    # Insert new strategy
                    sql = """
                    INSERT INTO strategies (
                        name, description, author, version, language,
                        original_filename, file_size, source_code, parameters,
                        dependencies, supported_timeframes, supported_assets, tags,
                        validation_status, validation_errors, validation_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    params = (
                        strategy.name, strategy.description, strategy.author, strategy.version,
                        strategy.language.value, strategy.original_filename, strategy.file_size,
                        strategy.source_code, json.dumps(strategy.parameters),
                        json.dumps(strategy.dependencies), json.dumps(strategy.supported_timeframes),
                        json.dumps(strategy.supported_assets), json.dumps(strategy.tags),
                        strategy.validation_status.value, json.dumps(strategy.validation_errors),
                        strategy.validation_timestamp
                    )
                    
                    cursor = conn.execute(sql, params)
                    strategy_id = cursor.lastrowid
                
                conn.commit()
                logger.info(f"Strategy saved successfully with ID: {strategy_id}")
                return str(strategy_id)
                
        except Exception as e:
            logger.error(f"Failed to save strategy: {e}")
            raise
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyMetadata]:
        """Get a strategy by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM strategies 
                    WHERE id = ? AND is_deleted = FALSE
                """, (strategy_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return self._row_to_strategy(row)
                
        except Exception as e:
            logger.error(f"Failed to get strategy {strategy_id}: {e}")
            return None
    
    def list_strategies(self, 
                       author: Optional[str] = None,
                       language: Optional[LanguageType] = None,
                       tags: Optional[List[str]] = None,
                       search_query: Optional[str] = None,
                       limit: int = 100,
                       offset: int = 0) -> List[StrategyMetadata]:
        """List strategies with filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Build dynamic query
                conditions = ["is_deleted = FALSE"]
                params = []
                
                if author:
                    conditions.append("author = ?")
                    params.append(author)
                
                if language:
                    conditions.append("language = ?")
                    params.append(language.value)
                
                if tags:
                    # Search in JSON tags array
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append("JSON_EXTRACT(tags, '$') LIKE ?")
                        params.append(f'%"{tag}"%')
                    if tag_conditions:
                        conditions.append(f"({' OR '.join(tag_conditions)})")
                
                if search_query:
                    search_condition = """(
                        name LIKE ? OR 
                        description LIKE ? OR 
                        source_code LIKE ?
                    )"""
                    conditions.append(search_condition)
                    search_param = f"%{search_query}%"
                    params.extend([search_param, search_param, search_param])
                
                where_clause = " AND ".join(conditions)
                
                sql = f"""
                    SELECT * FROM strategies 
                    WHERE {where_clause}
                    ORDER BY updated_at DESC 
                    LIMIT ? OFFSET ?
                """
                params.extend([limit, offset])
                
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                return [self._row_to_strategy(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to list strategies: {e}")
            return []
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Soft delete a strategy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE strategies 
                    SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (strategy_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to delete strategy {strategy_id}: {e}")
            return False
    
    def save_validation_results(self, strategy_id: str, results: List[ValidationResult]):
        """Save validation results for a strategy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Clear existing validation results
                conn.execute("""
                    DELETE FROM strategy_validations 
                    WHERE strategy_id = ?
                """, (strategy_id,))
                
                # Insert new results
                for result in results:
                    conn.execute("""
                        INSERT INTO strategy_validations (
                            strategy_id, validation_type, status, message,
                            details, line_number, column_number
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        strategy_id, result.type, result.status, result.message,
                        json.dumps(result.details), result.line_number, result.column_number
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save validation results: {e}")
            raise
    
    def get_validation_results(self, strategy_id: str) -> List[ValidationResult]:
        """Get validation results for a strategy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM strategy_validations 
                    WHERE strategy_id = ?
                    ORDER BY validated_at DESC
                """, (strategy_id,))
                
                rows = cursor.fetchall()
                results = []
                
                for row in rows:
                    result = ValidationResult(
                        type=row['validation_type'],
                        status=row['status'],
                        message=row['message'],
                        details=json.loads(row['details']) if row['details'] else {},
                        line_number=row['line_number'],
                        column_number=row['column_number']
                    )
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to get validation results: {e}")
            return []
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get overall strategy statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Total strategies
                cursor = conn.execute("SELECT COUNT(*) FROM strategies WHERE is_deleted = FALSE")
                stats['total_strategies'] = cursor.fetchone()[0]
                
                # By language
                cursor = conn.execute("""
                    SELECT language, COUNT(*) 
                    FROM strategies 
                    WHERE is_deleted = FALSE 
                    GROUP BY language
                """)
                stats['by_language'] = dict(cursor.fetchall())
                
                # By validation status
                cursor = conn.execute("""
                    SELECT validation_status, COUNT(*) 
                    FROM strategies 
                    WHERE is_deleted = FALSE 
                    GROUP BY validation_status
                """)
                stats['by_validation_status'] = dict(cursor.fetchall())
                
                # Most popular tags
                cursor = conn.execute("""
                    SELECT name, usage_count 
                    FROM strategy_tags 
                    ORDER BY usage_count DESC 
                    LIMIT 10
                """)
                stats['popular_tags'] = dict(cursor.fetchall())
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get strategy stats: {e}")
            return {}
    
    def _row_to_strategy(self, row: sqlite3.Row) -> StrategyMetadata:
        """Convert database row to StrategyMetadata"""
        return StrategyMetadata(
            id=row['id'],
            name=row['name'],
            description=row['description'] or "",
            author=row['author'],
            version=row['version'],
            language=LanguageType(row['language']),
            original_filename=row['original_filename'],
            file_size=row['file_size'],
            source_code=row['source_code'],
            parameters=json.loads(row['parameters']) if row['parameters'] else {},
            dependencies=json.loads(row['dependencies']) if row['dependencies'] else [],
            supported_timeframes=json.loads(row['supported_timeframes']) if row['supported_timeframes'] else [],
            supported_assets=json.loads(row['supported_assets']) if row['supported_assets'] else [],
            tags=json.loads(row['tags']) if row['tags'] else [],
            validation_status=ValidationStatus(row['validation_status']),
            validation_errors=json.loads(row['validation_errors']) if row['validation_errors'] else [],
            validation_timestamp=datetime.fromisoformat(row['validation_timestamp']) if row['validation_timestamp'] else None,
            upload_count=row['upload_count'],
            backtest_count=row['backtest_count'],
            last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            is_deleted=bool(row['is_deleted'])
        )