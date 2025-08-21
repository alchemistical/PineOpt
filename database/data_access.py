"""
PineOpt Data Access Layer
High-level database operations for the application
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import pandas as pd
from sqlalchemy import desc, asc, func, and_, or_
from sqlalchemy.orm import Session
import logging

from .models import (
    db_manager, Strategy, StrategyParameter, CryptoOHLCData, CryptoDataSource,
    BacktestConfig, BacktestResult, BacktestTrade, OptimizationCampaign,
    PineScriptFile, Conversion, DataSession, ActivityLog, SystemStat
)

logger = logging.getLogger(__name__)

class CryptoDataAccess:
    """Data access operations for crypto market data."""
    
    @staticmethod
    def store_ohlc_data(
        symbol: str, 
        exchange: str, 
        timeframe: str,
        ohlc_data: List[Dict],
        source_type: str = "binance_api"
    ) -> int:
        """Store OHLC data efficiently with batch insert."""
        session = db_manager.get_session()
        try:
            records_inserted = 0
            
            for data_point in ohlc_data:
                # Convert to CryptoOHLCData object
                ohlc_record = CryptoOHLCData(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    timestamp_utc=data_point['timestamp_utc'],
                    datetime_str=data_point['datetime_str'],
                    open_price=data_point['open_price'],
                    high_price=data_point['high_price'],
                    low_price=data_point['low_price'],
                    close_price=data_point['close_price'],
                    volume=data_point.get('volume', 0),
                    trades_count=data_point.get('trades_count', 0),
                    source_type=source_type,
                    ohlcv_json=json.dumps({
                        "Open": float(data_point['open_price']),
                        "High": float(data_point['high_price']),
                        "Low": float(data_point['low_price']),
                        "Close": float(data_point['close_price']),
                        "Volume": float(data_point.get('volume', 0))
                    })
                )
                
                # Handle duplicates
                existing = session.query(CryptoOHLCData).filter(
                    CryptoOHLCData.symbol == symbol,
                    CryptoOHLCData.exchange == exchange,
                    CryptoOHLCData.timeframe == timeframe,
                    CryptoOHLCData.timestamp_utc == data_point['timestamp_utc']
                ).first()
                
                if not existing:
                    session.add(ohlc_record)
                    records_inserted += 1
            
            # Update or create data source
            CryptoDataAccess.update_data_source(session, symbol, exchange, timeframe)
            
            session.commit()
            logger.info(f"Stored {records_inserted} new OHLC records for {symbol}-{exchange}-{timeframe}")
            return records_inserted
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing OHLC data: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def update_data_source(session: Session, symbol: str, exchange: str, timeframe: str):
        """Update data source metadata."""
        # Get existing or create new
        data_source = session.query(CryptoDataSource).filter(
            CryptoDataSource.symbol == symbol,
            CryptoDataSource.exchange == exchange,
            CryptoDataSource.timeframe == timeframe
        ).first()
        
        if not data_source:
            data_source = CryptoDataSource(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                pandas_freq='H' if timeframe == '1h' else 'D',
                ccxt_timeframe=timeframe,
                backtrader_compression=1
            )
            session.add(data_source)
        
        # Calculate stats
        stats = session.query(
            func.count(CryptoOHLCData.id).label('total'),
            func.min(CryptoOHLCData.timestamp_utc).label('first_ts'),
            func.max(CryptoOHLCData.timestamp_utc).label('last_ts'),
            func.min(CryptoOHLCData.low_price).label('min_price'),
            func.max(CryptoOHLCData.high_price).label('max_price')
        ).filter(
            CryptoOHLCData.symbol == symbol,
            CryptoOHLCData.exchange == exchange,
            CryptoOHLCData.timeframe == timeframe
        ).first()
        
        # Update metadata
        data_source.total_records = stats.total or 0
        data_source.first_timestamp_utc = stats.first_ts
        data_source.last_timestamp_utc = stats.last_ts
        data_source.price_min = stats.min_price
        data_source.price_max = stats.max_price
        data_source.last_updated = datetime.utcnow()
    
    @staticmethod
    def get_ohlc_data_as_dataframe(
        symbol: str,
        exchange: str, 
        timeframe: str,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Get OHLC data as pandas DataFrame for analysis."""
        session = db_manager.get_session()
        try:
            query = session.query(CryptoOHLCData).filter(
                CryptoOHLCData.symbol == symbol,
                CryptoOHLCData.exchange == exchange,
                CryptoOHLCData.timeframe == timeframe
            )
            
            if start_timestamp:
                query = query.filter(CryptoOHLCData.timestamp_utc >= start_timestamp)
            if end_timestamp:
                query = query.filter(CryptoOHLCData.timestamp_utc <= end_timestamp)
            
            query = query.order_by(CryptoOHLCData.timestamp_utc)
            
            if limit:
                query = query.limit(limit)
            
            data = query.all()
            
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df_data = []
            for record in data:
                df_data.append({
                    'timestamp': pd.to_datetime(record.timestamp_utc, unit='us', utc=True),
                    'open': float(record.open_price),
                    'high': float(record.high_price),
                    'low': float(record.low_price),
                    'close': float(record.close_price),
                    'volume': float(record.volume) if record.volume else 0
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            
            return df
            
        finally:
            session.close()
    
    @staticmethod
    def get_available_data_sources() -> List[Dict]:
        """Get all available crypto data sources."""
        session = db_manager.get_session()
        try:
            sources = session.query(CryptoDataSource).filter(
                CryptoDataSource.status == 'active'
            ).all()
            
            return [
                {
                    'symbol': source.symbol,
                    'exchange': source.exchange,
                    'timeframe': source.timeframe,
                    'total_records': source.total_records,
                    'date_range': {
                        'start': source.first_timestamp_utc,
                        'end': source.last_timestamp_utc
                    },
                    'price_range': {
                        'min': float(source.price_min) if source.price_min else None,
                        'max': float(source.price_max) if source.price_max else None
                    }
                }
                for source in sources
            ]
        finally:
            session.close()

class StrategyDataAccess:
    """Data access operations for trading strategies."""
    
    @staticmethod
    def create_strategy(
        name: str,
        description: str,
        pine_script_content: str,
        category: str = "Custom"
    ) -> int:
        """Create a new strategy with Pine Script."""
        session = db_manager.get_session()
        try:
            # Store Pine Script file
            pine_file = PineScriptFile(
                filename=f"{name.lower().replace(' ', '_')}.pine",
                file_content=pine_script_content,
                file_size=len(pine_script_content),
                file_hash=hash(pine_script_content)
            )
            session.add(pine_file)
            session.flush()  # Get ID
            
            # Create strategy
            strategy = Strategy(
                name=name,
                description=description,
                category=category,
                pine_script_file_id=pine_file.id,
                status='draft'
            )
            session.add(strategy)
            session.flush()
            
            # Log activity
            ActivityDataAccess.log_activity(
                session, "strategy_created", "strategy", strategy.id,
                {"name": name, "category": category}
            )
            
            session.commit()
            logger.info(f"Created strategy: {name} (ID: {strategy.id})")
            return strategy.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating strategy: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def add_strategy_parameter(
        strategy_id: int,
        param_name: str,
        param_type: str,
        constraints: Dict,
        default_value: Any,
        pine_input_name: str = None
    ) -> int:
        """Add parameter to strategy."""
        session = db_manager.get_session()
        try:
            param = StrategyParameter(
                strategy_id=strategy_id,
                parameter_name=param_name,
                parameter_type=param_type,
                constraints_json=json.dumps(constraints),
                pine_input_name=pine_input_name or param_name,
                optuna_suggest_type=f"suggest_{param_type}"
            )
            
            # Set default value based on type
            if param_type in ['int', 'float']:
                param.default_value_num = float(default_value)
            elif param_type == 'bool':
                param.default_value_bool = bool(default_value)
            else:
                param.default_value_str = str(default_value)
            
            session.add(param)
            session.commit()
            
            return param.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding parameter: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_strategies(status: str = None) -> List[Dict]:
        """Get all strategies with metadata."""
        session = db_manager.get_session()
        try:
            query = session.query(Strategy)
            if status:
                query = query.filter(Strategy.status == status)
            
            strategies = query.order_by(desc(Strategy.created_at)).all()
            
            result = []
            for strategy in strategies:
                param_count = session.query(StrategyParameter).filter(
                    StrategyParameter.strategy_id == strategy.id
                ).count()
                
                result.append({
                    'id': strategy.id,
                    'name': strategy.name,
                    'description': strategy.description,
                    'category': strategy.category,
                    'status': strategy.status,
                    'parameter_count': param_count,
                    'created_at': strategy.created_at.isoformat(),
                    'updated_at': strategy.updated_at.isoformat()
                })
            
            return result
            
        finally:
            session.close()
    
    @staticmethod
    def get_strategy_with_parameters(strategy_id: int) -> Optional[Dict]:
        """Get complete strategy information including parameters."""
        session = db_manager.get_session()
        try:
            strategy = session.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                return None
            
            parameters = session.query(StrategyParameter).filter(
                StrategyParameter.strategy_id == strategy_id
            ).all()
            
            return {
                'id': strategy.id,
                'name': strategy.name,
                'description': strategy.description,
                'category': strategy.category,
                'status': strategy.status,
                'python_code': strategy.python_code,
                'pine_script_content': strategy.pine_script_file.file_content if strategy.pine_script_file else None,
                'parameters': [
                    {
                        'id': param.id,
                        'name': param.parameter_name,
                        'type': param.parameter_type,
                        'constraints': param.get_constraints(),
                        'default_value': param.get_default_value(),
                        'is_optimizable': param.is_optimizable
                    }
                    for param in parameters
                ],
                'created_at': strategy.created_at.isoformat(),
                'updated_at': strategy.updated_at.isoformat()
            }
            
        finally:
            session.close()

class BacktestDataAccess:
    """Data access operations for backtesting."""
    
    @staticmethod
    def create_backtest_config(
        name: str,
        strategy_id: int,
        symbol: str,
        exchange: str,
        timeframe: str,
        start_timestamp: int,
        end_timestamp: int,
        initial_capital: float = 10000,
        commission_rate: float = 0.001
    ) -> int:
        """Create backtest configuration."""
        session = db_manager.get_session()
        try:
            config = BacktestConfig(
                name=name,
                strategy_id=strategy_id,
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                start_timestamp_utc=start_timestamp,
                end_timestamp_utc=end_timestamp,
                initial_capital=initial_capital,
                commission_rate=commission_rate
            )
            
            session.add(config)
            session.commit()
            
            logger.info(f"Created backtest config: {name} (ID: {config.id})")
            return config.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating backtest config: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_backtest_results(
        strategy_id: int = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get backtest results with summary information."""
        session = db_manager.get_session()
        try:
            query = session.query(BacktestResult).join(BacktestConfig)
            
            if strategy_id:
                query = query.filter(BacktestConfig.strategy_id == strategy_id)
            
            results = query.order_by(desc(BacktestResult.created_at)).limit(limit).all()
            
            return [
                {
                    'id': result.id,
                    'config_name': result.backtest_config.name,
                    'strategy_name': result.backtest_config.strategy.name,
                    'symbol': result.backtest_config.symbol,
                    'timeframe': result.backtest_config.timeframe,
                    'execution_status': result.execution_status,
                    'total_return_pct': float(result.total_return_pct) if result.total_return_pct else None,
                    'sharpe_ratio': float(result.sharpe_ratio) if result.sharpe_ratio else None,
                    'max_drawdown_pct': float(result.max_drawdown_pct) if result.max_drawdown_pct else None,
                    'total_trades': result.total_trades,
                    'win_rate_pct': float(result.win_rate_pct) if result.win_rate_pct else None,
                    'execution_time_ms': result.execution_time_ms,
                    'created_at': result.created_at.isoformat()
                }
                for result in results
            ]
            
        finally:
            session.close()

class ActivityDataAccess:
    """Data access for system activity and monitoring."""
    
    @staticmethod
    def log_activity(
        session: Session,
        activity_type: str,
        entity_type: str = None,
        entity_id: int = None,
        details: Dict = None
    ):
        """Log system activity."""
        activity = ActivityLog(
            activity_type=activity_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=json.dumps(details) if details else None
        )
        session.add(activity)
    
    @staticmethod
    def get_recent_activity(limit: int = 50) -> List[Dict]:
        """Get recent system activity."""
        session = db_manager.get_session()
        try:
            activities = session.query(ActivityLog).order_by(
                desc(ActivityLog.created_at)
            ).limit(limit).all()
            
            return [
                {
                    'activity_type': activity.activity_type,
                    'entity_type': activity.entity_type,
                    'entity_id': activity.entity_id,
                    'details': json.loads(activity.details) if activity.details else None,
                    'created_at': activity.created_at.isoformat()
                }
                for activity in activities
            ]
            
        finally:
            session.close()
    
    @staticmethod
    def update_system_stat(stat_name: str, stat_value: str, category: str = None):
        """Update system statistic."""
        session = db_manager.get_session()
        try:
            stat = session.query(SystemStat).filter(
                SystemStat.stat_name == stat_name
            ).first()
            
            if stat:
                stat.stat_value = stat_value
                stat.updated_at = datetime.utcnow()
            else:
                stat = SystemStat(
                    stat_name=stat_name,
                    stat_value=stat_value,
                    stat_category=category
                )
                session.add(stat)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating system stat: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_system_stats() -> Dict[str, str]:
        """Get all system statistics."""
        session = db_manager.get_session()
        try:
            stats = session.query(SystemStat).all()
            return {stat.stat_name: stat.stat_value for stat in stats}
        finally:
            session.close()

# Global data access instances
crypto_data = CryptoDataAccess()
strategy_data = StrategyDataAccess()
backtest_data = BacktestDataAccess()
activity_data = ActivityDataAccess()