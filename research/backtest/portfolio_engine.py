"""
Epic 5 Sprint 2: Portfolio Simulation Engine
Advanced portfolio management with position tracking, risk management, and performance analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict

from .strategy_executor import Portfolio, Position, Order, OrderSide, OrderStatus, OrderType

logger = logging.getLogger(__name__)

@dataclass
class PortfolioMetrics:
    """Comprehensive portfolio performance metrics"""
    total_return_pct: float = 0.0
    annualized_return_pct: float = 0.0
    volatility_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown_pct: float = 0.0
    max_drawdown_duration_days: int = 0
    calmar_ratio: float = 0.0
    win_rate_pct: float = 0.0
    profit_factor: float = 0.0
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    largest_win_pct: float = 0.0
    largest_loss_pct: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_trade_duration_hours: float = 0.0
    avg_time_in_market_pct: float = 0.0

@dataclass
class RiskMetrics:
    """Risk management and exposure metrics"""
    var_95_pct: float = 0.0  # Value at Risk (95%)
    cvar_95_pct: float = 0.0  # Conditional VaR (95%)
    beta: float = 0.0
    alpha_pct: float = 0.0
    correlation_with_market: float = 0.0
    maximum_exposure_pct: float = 0.0
    current_exposure_pct: float = 0.0
    leverage_ratio: float = 0.0

@dataclass
class TradeAnalysis:
    """Individual trade analysis"""
    trade_id: str
    symbol: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    side: OrderSide
    duration_hours: Optional[float]
    pnl_absolute: float
    pnl_percentage: float
    commission: float
    slippage: float
    is_winner: bool
    is_open: bool

class PortfolioSimulator:
    """
    Advanced portfolio simulation engine with comprehensive
    performance tracking, risk management, and analytics
    """
    
    def __init__(self, 
                 initial_capital: float = 100000.0,
                 max_position_size_pct: float = 10.0,  # Max 10% per position
                 max_total_exposure_pct: float = 100.0,  # Max 100% exposure
                 commission_rate: float = 0.001,
                 slippage_rate: float = 0.0001,
                 risk_free_rate: float = 0.02):  # 2% annual risk-free rate
        
        self.initial_capital = initial_capital
        self.max_position_size_pct = max_position_size_pct
        self.max_total_exposure_pct = max_total_exposure_pct
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.risk_free_rate = risk_free_rate
        
        # Portfolio state
        self.portfolio = Portfolio(cash=initial_capital, initial_capital=initial_capital)
        self.portfolio_history: List[Dict[str, Any]] = []
        
        # Trade tracking
        self.open_trades: Dict[str, TradeAnalysis] = {}
        self.closed_trades: List[TradeAnalysis] = []
        self.orders_history: List[Order] = []
        
        # Performance tracking
        self.daily_values: List[Tuple[datetime, float]] = []
        self.daily_returns: List[float] = []
        self.drawdown_series: List[float] = []
        
        # Market data for benchmarking
        self.benchmark_returns: Optional[pd.Series] = None
        
    def set_benchmark(self, benchmark_data: pd.DataFrame):
        """Set benchmark data for comparison (e.g., BTC returns)"""
        if 'close' in benchmark_data.columns:
            self.benchmark_returns = benchmark_data['close'].pct_change().dropna()
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              risk_per_trade_pct: float = 2.0) -> float:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the position
            risk_per_trade_pct: Maximum risk per trade as % of portfolio
        
        Returns:
            Position size in base currency units
        """
        # Maximum position value based on position size limit
        max_position_value = self.portfolio.total_value * (self.max_position_size_pct / 100)
        
        # Risk-based position sizing (assumes 2% stop loss)
        risk_amount = self.portfolio.total_value * (risk_per_trade_pct / 100)
        stop_loss_distance_pct = 0.02  # 2% stop loss
        risk_based_value = risk_amount / stop_loss_distance_pct
        
        # Use smaller of the two approaches
        position_value = min(max_position_value, risk_based_value)
        
        # Convert to quantity
        quantity = position_value / entry_price
        
        # Check total exposure limit
        current_exposure = sum(abs(pos.market_value) for pos in self.portfolio.positions.values())
        if current_exposure + position_value > self.portfolio.total_value * (self.max_total_exposure_pct / 100):
            # Reduce position size to stay within exposure limit
            available_exposure = self.portfolio.total_value * (self.max_total_exposure_pct / 100) - current_exposure
            quantity = max(0, available_exposure / entry_price)
        
        return quantity
    
    def open_position(self, symbol: str, side: OrderSide, quantity: float, 
                     price: float, timestamp: datetime, 
                     strategy_id: Optional[str] = None) -> Optional[str]:
        """
        Open a new trading position
        
        Returns:
            Trade ID if successful, None if failed
        """
        try:
            # Create order
            order = Order(
                id=f"order_{len(self.orders_history) + 1}",
                timestamp=timestamp,
                symbol=symbol,
                side=side,
                order_type=OrderType.MARKET,
                quantity=quantity,
                strategy_id=strategy_id
            )
            
            # Apply slippage
            if side == OrderSide.BUY:
                execution_price = price * (1 + self.slippage_rate)
            else:
                execution_price = price * (1 - self.slippage_rate)
            
            # Calculate costs
            trade_value = quantity * execution_price
            commission = trade_value * self.commission_rate
            
            # Check available cash for buy orders
            if side == OrderSide.BUY and trade_value + commission > self.portfolio.cash:
                logger.warning(f"Insufficient cash for trade: need {trade_value + commission}, have {self.portfolio.cash}")
                return None
            
            # Update portfolio
            if symbol not in self.portfolio.positions:
                self.portfolio.positions[symbol] = Position(symbol=symbol)
            
            position = self.portfolio.positions[symbol]
            
            # Update position and cash
            if side == OrderSide.BUY:
                if position.quantity >= 0:  # Adding to long or opening long
                    total_cost = (position.quantity * position.avg_price) + (quantity * execution_price)
                    total_quantity = position.quantity + quantity
                    position.avg_price = total_cost / total_quantity if total_quantity > 0 else 0
                    position.quantity = total_quantity
                
                self.portfolio.cash -= (trade_value + commission)
                
            else:  # SELL
                if position.quantity <= 0:  # Adding to short or opening short
                    total_value = abs(position.quantity * position.avg_price) + (quantity * execution_price)
                    total_quantity = abs(position.quantity) + quantity
                    position.avg_price = total_value / total_quantity
                    position.quantity -= quantity
                
                self.portfolio.cash += (trade_value - commission)
            
            # Update order
            order.status = OrderStatus.FILLED
            order.filled_quantity = quantity
            order.filled_price = execution_price
            order.commission = commission
            
            self.orders_history.append(order)
            self.portfolio.total_commission += commission
            
            # Create trade analysis record
            trade_id = f"trade_{len(self.open_trades) + len(self.closed_trades) + 1}"
            trade = TradeAnalysis(
                trade_id=trade_id,
                symbol=symbol,
                entry_time=timestamp,
                exit_time=None,
                entry_price=execution_price,
                exit_price=None,
                quantity=quantity,
                side=side,
                duration_hours=None,
                pnl_absolute=0.0,
                pnl_percentage=0.0,
                commission=commission,
                slippage=abs(execution_price - price),
                is_winner=False,
                is_open=True
            )
            
            self.open_trades[trade_id] = trade
            
            logger.info(f"Opened position: {side.value} {quantity:.6f} {symbol} @ {execution_price:.4f}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to open position: {e}")
            return None
    
    def close_position(self, symbol: str, quantity: Optional[float], 
                      price: float, timestamp: datetime,
                      strategy_id: Optional[str] = None) -> List[str]:
        """
        Close position(s) for a symbol
        
        Returns:
            List of closed trade IDs
        """
        if symbol not in self.portfolio.positions:
            logger.warning(f"No position to close for {symbol}")
            return []
        
        position = self.portfolio.positions[symbol]
        if position.is_flat:
            logger.warning(f"Position for {symbol} is already flat")
            return []
        
        # Determine quantity to close
        if quantity is None:
            close_quantity = abs(position.quantity)  # Close entire position
        else:
            close_quantity = min(quantity, abs(position.quantity))
        
        # Determine side (opposite of current position)
        close_side = OrderSide.SELL if position.quantity > 0 else OrderSide.BUY
        
        try:
            # Apply slippage
            if close_side == OrderSide.SELL:
                execution_price = price * (1 - self.slippage_rate)
            else:
                execution_price = price * (1 + self.slippage_rate)
            
            # Calculate trade details
            trade_value = close_quantity * execution_price
            commission = trade_value * self.commission_rate
            
            # Calculate P&L
            if position.quantity > 0:  # Closing long position
                pnl_per_share = execution_price - position.avg_price
                total_pnl = pnl_per_share * close_quantity
                self.portfolio.cash += (trade_value - commission)
            else:  # Closing short position
                pnl_per_share = position.avg_price - execution_price
                total_pnl = pnl_per_share * close_quantity
                self.portfolio.cash -= (trade_value + commission)
            
            # Update position
            if position.quantity > 0:
                position.quantity -= close_quantity
            else:
                position.quantity += close_quantity
            
            # Add to realized P&L
            position.realized_pnl += total_pnl
            
            # Create close order
            order = Order(
                id=f"order_{len(self.orders_history) + 1}",
                timestamp=timestamp,
                symbol=symbol,
                side=close_side,
                order_type=OrderType.MARKET,
                quantity=close_quantity,
                status=OrderStatus.FILLED,
                filled_quantity=close_quantity,
                filled_price=execution_price,
                commission=commission,
                strategy_id=strategy_id
            )
            
            self.orders_history.append(order)
            self.portfolio.total_commission += commission
            
            # Update trade records
            closed_trade_ids = []
            for trade_id, trade in list(self.open_trades.items()):
                if trade.symbol == symbol and trade.is_open:
                    # Calculate trade metrics
                    trade.exit_time = timestamp
                    trade.exit_price = execution_price
                    trade.duration_hours = (timestamp - trade.entry_time).total_seconds() / 3600
                    
                    # Calculate P&L for this trade
                    if trade.side == OrderSide.BUY:
                        trade.pnl_absolute = (execution_price - trade.entry_price) * trade.quantity - trade.commission - commission
                        trade.pnl_percentage = ((execution_price - trade.entry_price) / trade.entry_price) * 100
                    else:
                        trade.pnl_absolute = (trade.entry_price - execution_price) * trade.quantity - trade.commission - commission
                        trade.pnl_percentage = ((trade.entry_price - execution_price) / trade.entry_price) * 100
                    
                    trade.is_winner = trade.pnl_absolute > 0
                    trade.is_open = False
                    trade.commission += commission
                    trade.slippage += abs(execution_price - price)
                    
                    # Move to closed trades
                    self.closed_trades.append(trade)
                    closed_trade_ids.append(trade_id)
                    del self.open_trades[trade_id]
                    
                    logger.info(f"Closed trade {trade_id}: P&L = {trade.pnl_absolute:.2f} ({trade.pnl_percentage:.2f}%)")
                    break  # Close one trade at a time for now
            
            return closed_trade_ids
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return []
    
    def update_portfolio_value(self, market_prices: Dict[str, float], timestamp: datetime):
        """Update portfolio valuation with current market prices"""
        # Update position values
        for symbol, position in self.portfolio.positions.items():
            if symbol in market_prices and not position.is_flat:
                current_price = market_prices[symbol]
                position.last_price = current_price
                position.market_value = position.quantity * current_price
                
                # Update unrealized P&L
                if position.quantity > 0:  # Long position
                    position.unrealized_pnl = (current_price - position.avg_price) * position.quantity
                else:  # Short position
                    position.unrealized_pnl = (position.avg_price - current_price) * abs(position.quantity)
        
        # Record portfolio history
        portfolio_snapshot = {
            'timestamp': timestamp,
            'total_value': self.portfolio.total_value,
            'cash': self.portfolio.cash,
            'positions_value': sum(pos.market_value for pos in self.portfolio.positions.values()),
            'unrealized_pnl': sum(pos.unrealized_pnl for pos in self.portfolio.positions.values()),
            'realized_pnl': sum(pos.realized_pnl for pos in self.portfolio.positions.values()),
            'total_commission': self.portfolio.total_commission,
            'return_pct': self.portfolio.return_pct
        }
        
        self.portfolio_history.append(portfolio_snapshot)
        
        # Update daily tracking
        self.daily_values.append((timestamp, self.portfolio.total_value))
        
        if len(self.daily_values) > 1:
            prev_value = self.daily_values[-2][1]
            daily_return = (self.portfolio.total_value - prev_value) / prev_value
            self.daily_returns.append(daily_return)
    
    def calculate_comprehensive_metrics(self) -> Tuple[PortfolioMetrics, RiskMetrics]:
        """Calculate comprehensive portfolio and risk metrics"""
        if len(self.portfolio_history) < 2:
            return PortfolioMetrics(), RiskMetrics()
        
        # Convert history to DataFrame for analysis
        df = pd.DataFrame(self.portfolio_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Basic metrics
        total_return = (self.portfolio.total_value - self.initial_capital) / self.initial_capital
        
        # Time-based metrics
        days_elapsed = (df.index[-1] - df.index[0]).days + 1
        years_elapsed = days_elapsed / 365.25
        annualized_return = (1 + total_return) ** (1 / max(years_elapsed, 1/365)) - 1 if years_elapsed > 0 else 0
        
        # Daily returns analysis
        if len(self.daily_returns) > 1:
            daily_returns_series = pd.Series(self.daily_returns)
            volatility = daily_returns_series.std() * np.sqrt(252)  # Annualized
            
            # Sharpe ratio
            excess_returns = daily_returns_series.mean() * 252 - self.risk_free_rate
            sharpe_ratio = excess_returns / volatility if volatility > 0 else 0
            
            # Sortino ratio (only downside volatility)
            downside_returns = daily_returns_series[daily_returns_series < 0]
            downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = excess_returns / downside_std if downside_std > 0 else 0
        else:
            volatility = 0
            sharpe_ratio = 0
            sortino_ratio = 0
        
        # Drawdown analysis
        portfolio_values = df['total_value']
        cumulative_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()
        
        # Find drawdown duration
        drawdown_duration = 0
        if not drawdown.empty:
            # Find periods where we're in drawdown
            in_drawdown = drawdown < -0.001  # More than 0.1% drawdown
            if in_drawdown.any():
                # Find longest consecutive drawdown period
                drawdown_periods = []
                start_date = None
                for date, is_dd in in_drawdown.items():
                    if is_dd and start_date is None:
                        start_date = date
                    elif not is_dd and start_date is not None:
                        drawdown_periods.append((date - start_date).days)
                        start_date = None
                
                if start_date is not None:  # Still in drawdown
                    drawdown_periods.append((df.index[-1] - start_date).days)
                
                drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
        
        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else 0
        
        # Trade analysis
        all_trades = self.closed_trades
        total_trades = len(all_trades)
        winning_trades = len([t for t in all_trades if t.is_winner])
        losing_trades = total_trades - winning_trades
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L analysis
        winning_pnls = [t.pnl_absolute for t in all_trades if t.is_winner]
        losing_pnls = [t.pnl_absolute for t in all_trades if not t.is_winner]
        
        avg_win = np.mean(winning_pnls) if winning_pnls else 0
        avg_loss = abs(np.mean(losing_pnls)) if losing_pnls else 0
        largest_win = max(winning_pnls) if winning_pnls else 0
        largest_loss = abs(min(losing_pnls)) if losing_pnls else 0
        
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Convert absolute P&L to percentages
        avg_win_pct = (avg_win / self.initial_capital * 100) if avg_win > 0 else 0
        avg_loss_pct = (avg_loss / self.initial_capital * 100) if avg_loss > 0 else 0
        largest_win_pct = (largest_win / self.initial_capital * 100) if largest_win > 0 else 0
        largest_loss_pct = (largest_loss / self.initial_capital * 100) if largest_loss > 0 else 0
        
        # Trade duration
        durations = [t.duration_hours for t in all_trades if t.duration_hours is not None]
        avg_trade_duration = np.mean(durations) if durations else 0
        
        # Time in market (approximate)
        total_time_hours = (df.index[-1] - df.index[0]).total_seconds() / 3600
        time_in_trades_hours = sum(durations) if durations else 0
        time_in_market_pct = (time_in_trades_hours / total_time_hours * 100) if total_time_hours > 0 else 0
        
        # Risk metrics
        risk_metrics = RiskMetrics()
        
        if len(self.daily_returns) > 10:
            returns_array = np.array(self.daily_returns)
            
            # VaR and CVaR (95% confidence)
            var_95 = np.percentile(returns_array, 5) * 100  # 5th percentile
            cvar_95 = np.mean(returns_array[returns_array <= np.percentile(returns_array, 5)]) * 100
            
            risk_metrics.var_95_pct = var_95
            risk_metrics.cvar_95_pct = cvar_95
            
            # Beta and Alpha (if benchmark available)
            if self.benchmark_returns is not None and len(self.benchmark_returns) > 10:
                # Align returns
                common_dates = df.index.intersection(self.benchmark_returns.index)
                if len(common_dates) > 10:
                    portfolio_returns = df.loc[common_dates]['return_pct'] / 100
                    benchmark_aligned = self.benchmark_returns.loc[common_dates]
                    
                    # Calculate beta
                    covariance = np.cov(portfolio_returns, benchmark_aligned)[0, 1]
                    benchmark_variance = np.var(benchmark_aligned)
                    beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
                    
                    # Calculate alpha
                    portfolio_mean_return = portfolio_returns.mean() * 252
                    benchmark_mean_return = benchmark_aligned.mean() * 252
                    alpha = portfolio_mean_return - (self.risk_free_rate + beta * (benchmark_mean_return - self.risk_free_rate))
                    
                    risk_metrics.beta = beta
                    risk_metrics.alpha_pct = alpha * 100
                    risk_metrics.correlation_with_market = np.corrcoef(portfolio_returns, benchmark_aligned)[0, 1]
        
        # Exposure metrics
        current_positions_value = sum(abs(pos.market_value) for pos in self.portfolio.positions.values())
        risk_metrics.current_exposure_pct = (current_positions_value / self.portfolio.total_value * 100) if self.portfolio.total_value > 0 else 0
        
        # Maximum exposure (from history)
        max_positions_value = max([sum(abs(pos.get('market_value', 0)) for pos in snapshot.get('positions', {}).values()) 
                                  for snapshot in self.portfolio_history] + [0])
        risk_metrics.maximum_exposure_pct = (max_positions_value / self.initial_capital * 100) if max_positions_value > 0 else 0
        
        # Leverage (borrowed money / equity)
        risk_metrics.leverage_ratio = max(0, (current_positions_value - self.portfolio.cash) / self.portfolio.total_value) if self.portfolio.total_value > 0 else 0
        
        # Create portfolio metrics
        portfolio_metrics = PortfolioMetrics(
            total_return_pct=total_return * 100,
            annualized_return_pct=annualized_return * 100,
            volatility_pct=volatility * 100,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown_pct=max_drawdown * 100,
            max_drawdown_duration_days=drawdown_duration,
            calmar_ratio=calmar_ratio,
            win_rate_pct=win_rate,
            profit_factor=profit_factor,
            avg_win_pct=avg_win_pct,
            avg_loss_pct=avg_loss_pct,
            largest_win_pct=largest_win_pct,
            largest_loss_pct=largest_loss_pct,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_trade_duration_hours=avg_trade_duration,
            avg_time_in_market_pct=time_in_market_pct
        )
        
        return portfolio_metrics, risk_metrics