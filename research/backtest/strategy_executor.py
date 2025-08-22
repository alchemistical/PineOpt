"""
Epic 5 Sprint 2: Strategy Execution Engine
Core framework for executing trading strategies with portfolio simulation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types for strategy execution"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    """Order side (buy/sell)"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """Order execution status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    """Represents a trading order"""
    id: str
    timestamp: datetime
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    filled_price: Optional[float] = None
    commission: float = 0.0
    strategy_id: Optional[str] = None

@dataclass
class Position:
    """Represents a trading position"""
    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    market_value: float = 0.0
    last_price: float = 0.0
    
    @property
    def is_long(self) -> bool:
        return self.quantity > 0
    
    @property
    def is_short(self) -> bool:
        return self.quantity < 0
    
    @property
    def is_flat(self) -> bool:
        return abs(self.quantity) < 1e-8

@dataclass
class Portfolio:
    """Portfolio state with positions and cash"""
    cash: float = 100000.0
    positions: Dict[str, Position] = field(default_factory=dict)
    initial_capital: float = 100000.0
    total_commission: float = 0.0
    
    @property
    def total_value(self) -> float:
        """Total portfolio value (cash + positions market value)"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)"""
        total_realized = sum(pos.realized_pnl for pos in self.positions.values())
        total_unrealized = sum(pos.unrealized_pnl for pos in self.positions.values())
        return total_realized + total_unrealized
    
    @property
    def return_pct(self) -> float:
        """Portfolio return percentage"""
        return (self.total_value - self.initial_capital) / self.initial_capital * 100

@dataclass
class ExecutionResult:
    """Result of strategy execution"""
    success: bool
    message: str
    orders: List[Order] = field(default_factory=list)
    portfolio_snapshot: Optional[Portfolio] = None
    execution_time: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

class StrategyExecutor:
    """
    Core strategy execution engine that runs trading strategies
    against historical or live data with portfolio simulation
    """
    
    def __init__(self, 
                 initial_capital: float = 100000.0,
                 commission_rate: float = 0.001,  # 0.1% commission
                 slippage_rate: float = 0.0001):  # 0.01% slippage
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        # Initialize portfolio
        self.portfolio = Portfolio(
            cash=initial_capital,
            initial_capital=initial_capital
        )
        
        # Order and execution tracking
        self.orders: List[Order] = []
        self.execution_log: List[Dict[str, Any]] = []
        self.current_prices: Dict[str, float] = {}
        
        # Strategy state
        self.strategy_function: Optional[Callable] = None
        self.strategy_metadata: Dict[str, Any] = {}
        
    def load_strategy(self, strategy_code: str, strategy_metadata: Dict[str, Any] = None):
        """Load and compile a strategy from code"""
        try:
            # Import professional TA library
            try:
                import ta
            except ImportError:
                ta = None
                logger.warning("Professional TA library not available")
            
            # Create a safe execution environment with professional libraries
            strategy_globals = {
                'pd': pd,
                'np': np,
                'ta': ta,  # Professional technical analysis library
                '__builtins__': {
                    'len': len, 'range': range, 'enumerate': enumerate,
                    'zip': zip, 'abs': abs, 'min': min, 'max': max,
                    'round': round, 'sum': sum, 'any': any, 'all': all,
                    '__import__': __import__, 'hasattr': hasattr, 'getattr': getattr,
                    'isinstance': isinstance, 'type': type, 'str': str, 'int': int,
                    'float': float, 'bool': bool, 'dict': dict, 'list': list
                }
            }
            
            # Execute strategy code
            exec(strategy_code, strategy_globals)
            
            # Extract strategy function
            if 'build_signals' in strategy_globals:
                self.strategy_function = strategy_globals['build_signals']
                self.strategy_metadata = strategy_metadata or {}
                logger.info(f"Strategy loaded successfully: {self.strategy_metadata.get('name', 'Unknown')}")
                return True
            else:
                raise ValueError("Strategy must contain a 'build_signals' function")
                
        except Exception as e:
            logger.error(f"Failed to load strategy: {e}")
            return False
    
    def update_market_prices(self, prices: Dict[str, float]):
        """Update current market prices for portfolio valuation"""
        self.current_prices.update(prices)
        
        # Update position market values and unrealized P&L
        for symbol, position in self.portfolio.positions.items():
            if symbol in self.current_prices and not position.is_flat:
                current_price = self.current_prices[symbol]
                position.last_price = current_price
                position.market_value = position.quantity * current_price
                
                # Calculate unrealized P&L
                if position.quantity != 0:
                    position.unrealized_pnl = (current_price - position.avg_price) * position.quantity
    
    def execute_order(self, order: Order, current_price: float) -> bool:
        """Execute a single order against current market conditions"""
        try:
            # Apply slippage
            if order.side == OrderSide.BUY:
                execution_price = current_price * (1 + self.slippage_rate)
            else:
                execution_price = current_price * (1 - self.slippage_rate)
            
            # Calculate commission
            trade_value = order.quantity * execution_price
            commission = trade_value * self.commission_rate
            
            # Check if we have enough cash for buy orders
            if order.side == OrderSide.BUY:
                total_cost = trade_value + commission
                if total_cost > self.portfolio.cash:
                    order.status = OrderStatus.REJECTED
                    logger.warning(f"Order rejected: insufficient cash. Need {total_cost}, have {self.portfolio.cash}")
                    return False
            
            # Update portfolio
            symbol = order.symbol
            if symbol not in self.portfolio.positions:
                self.portfolio.positions[symbol] = Position(symbol=symbol)
            
            position = self.portfolio.positions[symbol]
            
            if order.side == OrderSide.BUY:
                # Update average price for long positions
                if position.quantity >= 0:  # Adding to long or opening long
                    total_cost = (position.quantity * position.avg_price) + (order.quantity * execution_price)
                    total_quantity = position.quantity + order.quantity
                    position.avg_price = total_cost / total_quantity if total_quantity > 0 else 0
                    position.quantity = total_quantity
                else:  # Covering short position
                    # Realize P&L for covered portion
                    covered_quantity = min(abs(position.quantity), order.quantity)
                    pnl = (position.avg_price - execution_price) * covered_quantity
                    position.realized_pnl += pnl
                    
                    # Update position
                    position.quantity += order.quantity
                    if position.quantity > 0:  # Now long
                        remaining_long = position.quantity
                        position.avg_price = execution_price  # New average for long portion
                
                # Update cash
                self.portfolio.cash -= (trade_value + commission)
                
            else:  # SELL
                if position.quantity > 0:  # Closing/reducing long position
                    # Realize P&L for sold portion
                    sold_quantity = min(position.quantity, order.quantity)
                    pnl = (execution_price - position.avg_price) * sold_quantity
                    position.realized_pnl += pnl
                    
                    # Update position
                    position.quantity -= order.quantity
                    if position.quantity < 0:  # Now short
                        position.avg_price = execution_price  # New average for short portion
                        
                else:  # Opening/adding to short position
                    if position.quantity <= 0:  # Adding to short or opening short
                        total_value = abs(position.quantity * position.avg_price) + (order.quantity * execution_price)
                        total_quantity = abs(position.quantity) + order.quantity
                        position.avg_price = total_value / total_quantity
                        position.quantity -= order.quantity
                    
                # Update cash
                self.portfolio.cash += (trade_value - commission)
            
            # Update order status
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.filled_price = execution_price
            order.commission = commission
            
            # Update portfolio commission
            self.portfolio.total_commission += commission
            
            # Log execution
            self.execution_log.append({
                'timestamp': order.timestamp,
                'symbol': order.symbol,
                'side': order.side.value,
                'quantity': order.quantity,
                'price': execution_price,
                'commission': commission,
                'portfolio_value': self.portfolio.total_value,
                'cash': self.portfolio.cash
            })
            
            logger.info(f"Order executed: {order.side.value} {order.quantity} {order.symbol} @ {execution_price:.4f}")
            return True
            
        except Exception as e:
            order.status = OrderStatus.REJECTED
            logger.error(f"Order execution failed: {e}")
            return False
    
    def run_backtest(self, data: pd.DataFrame, strategy_params: Dict[str, Any] = None) -> ExecutionResult:
        """
        Run a complete backtest on historical data
        
        Args:
            data: OHLC DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
            strategy_params: Parameters to pass to the strategy function
        
        Returns:
            ExecutionResult with orders, portfolio state, and metrics
        """
        if not self.strategy_function:
            return ExecutionResult(False, "No strategy loaded")
        
        try:
            start_time = datetime.now()
            strategy_params = strategy_params or {}
            
            # Run strategy to generate signals
            signals = self.strategy_function(data, **strategy_params)
            
            # Handle both StrategySignals objects and dict returns
            if hasattr(signals, 'entries') and hasattr(signals, 'exits'):
                # StrategySignals object
                entries = signals.entries
                exits = signals.exits
            elif isinstance(signals, dict) and 'entries' in signals:
                # Dict format
                entries = signals['entries']
                exits = signals.get('exits', pd.Series(False, index=data.index))
            else:
                return ExecutionResult(False, "Strategy must return StrategySignals object or dict with 'entries' key")
            
            # Ensure signals are boolean Series
            if not isinstance(entries, pd.Series):
                entries = pd.Series(entries, index=data.index)
            if not isinstance(exits, pd.Series):
                exits = pd.Series(exits, index=data.index)
            
            symbol = self.strategy_metadata.get('symbol', 'BTC/USDT')
            order_id_counter = 1
            
            # Execute strategy signals
            for i, (timestamp, row) in enumerate(data.iterrows()):
                current_price = row['close']
                self.update_market_prices({symbol: current_price})
                
                # Check for entry signals
                if i < len(entries) and entries.iloc[i]:
                    # Create buy order
                    order = Order(
                        id=f"order_{order_id_counter}",
                        timestamp=timestamp,
                        symbol=symbol,
                        side=OrderSide.BUY,
                        order_type=OrderType.MARKET,
                        quantity=1000 / current_price,  # $1000 position size
                        strategy_id=self.strategy_metadata.get('id')
                    )
                    
                    if self.execute_order(order, current_price):
                        self.orders.append(order)
                    order_id_counter += 1
                
                # Check for exit signals
                if i < len(exits) and exits.iloc[i]:
                    # Check if we have a position to close
                    if symbol in self.portfolio.positions and not self.portfolio.positions[symbol].is_flat:
                        position = self.portfolio.positions[symbol]
                        
                        # Create sell order to close position
                        order = Order(
                            id=f"order_{order_id_counter}",
                            timestamp=timestamp,
                            symbol=symbol,
                            side=OrderSide.SELL,
                            order_type=OrderType.MARKET,
                            quantity=abs(position.quantity),
                            strategy_id=self.strategy_metadata.get('id')
                        )
                        
                        if self.execute_order(order, current_price):
                            self.orders.append(order)
                        order_id_counter += 1
            
            # Final portfolio update
            if symbol in self.current_prices:
                self.update_market_prices(self.current_prices)
            
            # Calculate performance metrics
            metrics = self._calculate_metrics(data)
            
            execution_time = datetime.now() - start_time
            
            return ExecutionResult(
                success=True,
                message=f"Backtest completed successfully in {execution_time.total_seconds():.2f}s",
                orders=self.orders,
                portfolio_snapshot=self.portfolio,
                execution_time=start_time,
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Backtest execution failed: {e}")
            return ExecutionResult(False, f"Backtest failed: {str(e)}")
    
    def _calculate_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        if len(self.execution_log) == 0:
            return {}
        
        # Convert execution log to DataFrame
        trades_df = pd.DataFrame(self.execution_log)
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df.set_index('timestamp', inplace=True)
        
        # Basic metrics
        total_return = (self.portfolio.total_value - self.initial_capital) / self.initial_capital
        total_trades = len([o for o in self.orders if o.status == OrderStatus.FILLED])
        
        # Calculate daily returns for advanced metrics
        daily_values = trades_df['portfolio_value'].resample('D').last().fillna(method='ffill')
        daily_returns = daily_values.pct_change().dropna()
        
        # Risk metrics
        volatility = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 1 else 0
        sharpe_ratio = (daily_returns.mean() * 252) / volatility if volatility > 0 else 0
        
        # Drawdown calculation
        cumulative = (1 + daily_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
        
        # Win rate calculation
        winning_trades = 0
        total_trade_pnl = 0
        if len(self.orders) >= 2:
            # Simple P&L calculation from filled orders
            buy_orders = [o for o in self.orders if o.side == OrderSide.BUY and o.status == OrderStatus.FILLED]
            sell_orders = [o for o in self.orders if o.side == OrderSide.SELL and o.status == OrderStatus.FILLED]
            
            for i in range(min(len(buy_orders), len(sell_orders))):
                buy_price = buy_orders[i].filled_price
                sell_price = sell_orders[i].filled_price
                quantity = buy_orders[i].filled_quantity
                trade_pnl = (sell_price - buy_price) * quantity
                total_trade_pnl += trade_pnl
                if trade_pnl > 0:
                    winning_trades += 1
        
        win_rate = (winning_trades / max(1, min(len([o for o in self.orders if o.side == OrderSide.BUY]), 
                                                len([o for o in self.orders if o.side == OrderSide.SELL])))) * 100
        
        return {
            'total_return_pct': total_return * 100,
            'total_trades': total_trades,
            'win_rate_pct': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown * 100,
            'volatility_pct': volatility * 100,
            'final_portfolio_value': self.portfolio.total_value,
            'total_commission': self.portfolio.total_commission,
            'total_pnl': self.portfolio.total_pnl,
            'cash_remaining': self.portfolio.cash,
            'positions': {symbol: {
                'quantity': pos.quantity,
                'market_value': pos.market_value,
                'unrealized_pnl': pos.unrealized_pnl,
                'realized_pnl': pos.realized_pnl
            } for symbol, pos in self.portfolio.positions.items()},
            'execution_log_entries': len(self.execution_log)
        }
    
    def reset(self):
        """Reset executor state for new backtest"""
        self.portfolio = Portfolio(
            cash=self.initial_capital,
            initial_capital=self.initial_capital
        )
        self.orders.clear()
        self.execution_log.clear()
        self.current_prices.clear()