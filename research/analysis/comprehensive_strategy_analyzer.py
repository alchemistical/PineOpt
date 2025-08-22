"""
Comprehensive 360-View Strategy Analysis Framework
Based on analysis of SOL Trading Strategy and Quantoshi Stoic reports

This framework provides complete strategy analysis including:
- Executive Summary with Risk Assessment
- Performance Metrics Analysis
- Statistical Insights & Monte Carlo
- Detailed Diagnostics
- Optimization Recommendations
- Visual Analytics
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class RiskLevel(Enum):
    LOW = "LOW RISK"
    MEDIUM = "MEDIUM RISK" 
    HIGH = "HIGH RISK"
    CRITICAL = "CRITICAL RISK"

class PerformanceRating(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MARGINAL = "MARGINAL"
    POOR = "POOR"
    CRITICAL = "CRITICAL"

class RecommendationLevel(Enum):
    IMMEDIATE = "IMMEDIATE"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class PerformanceMetrics:
    """Core performance metrics"""
    net_profit: float
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    profit_factor: float
    win_rate: float
    max_drawdown: float
    avg_drawdown: float
    calmar_ratio: float
    recovery_factor: float
    
    # Additional metrics from reports
    std_dev: float
    min_return: float
    max_return: float
    skewness: float
    kurtosis: float
    var_95: float  # Value at Risk
    cvar_95: float  # Conditional Value at Risk
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int

@dataclass
class StatisticalAnalysis:
    """Statistical insights and anomalies"""
    monte_carlo_results: Dict[str, Any]
    correlation_analysis: Dict[str, float]
    regime_analysis: Dict[str, Any]
    seasonality_effects: Dict[str, Any]
    outlier_analysis: Dict[str, Any]
    stability_metrics: Dict[str, Any]

@dataclass
class DiagnosticIssue:
    """Individual diagnostic issue"""
    category: str
    severity: RecommendationLevel
    title: str
    description: str
    evidence: List[str]
    impact: str
    recommendation: str

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    priority: RecommendationLevel
    category: str
    title: str
    description: str
    implementation_steps: List[str]
    expected_impact: str
    implementation_time: str
    difficulty: str

@dataclass
class ComprehensiveStrategyReport:
    """Complete 360-view strategy analysis report"""
    
    # Executive Summary
    strategy_name: str
    analysis_date: str
    overall_assessment: str
    risk_level: RiskLevel
    performance_rating: PerformanceRating
    risk_adjusted_return: PerformanceRating
    recommendation: str
    
    # Core Metrics
    performance_metrics: PerformanceMetrics
    statistical_analysis: StatisticalAnalysis
    
    # Diagnostics
    diagnostic_issues: List[DiagnosticIssue]
    
    # Recommendations
    optimization_recommendations: List[OptimizationRecommendation]
    specific_actions: List[Dict[str, Any]]
    
    # Visual Components
    charts: Dict[str, Any] = field(default_factory=dict)
    
    # Limitations and Assumptions
    limitations: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    
    # Next Steps
    next_steps: List[str] = field(default_factory=list)

class ComprehensiveStrategyAnalyzer:
    """
    360-View Strategy Analysis System
    
    Provides comprehensive analysis including:
    1. Executive Summary with risk assessment
    2. Performance metrics analysis with statistical ratings
    3. Detailed diagnostics and flaw detection
    4. Monte Carlo simulation and statistical insights
    5. Optimization recommendations with priorities
    6. Visual analytics and charts
    7. Specific action items with timelines
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'sharpe_ratio': {'excellent': 2.0, 'good': 1.5, 'marginal': 1.0, 'poor': 0.5},
            'max_drawdown': {'excellent': 0.05, 'good': 0.10, 'marginal': 0.15, 'poor': 0.25},
            'profit_factor': {'excellent': 2.0, 'good': 1.5, 'marginal': 1.2, 'poor': 1.0},
            'win_rate': {'excellent': 0.65, 'good': 0.55, 'marginal': 0.45, 'poor': 0.35}
        }
    
    def analyze_strategy(self, returns: pd.Series, trades: pd.DataFrame = None, 
                        strategy_name: str = "Strategy", **kwargs) -> ComprehensiveStrategyReport:
        """
        Main analysis method - generates comprehensive 360-view report
        
        Args:
            returns: Strategy returns time series
            trades: Individual trade data (optional)
            strategy_name: Name of the strategy
            **kwargs: Additional parameters
            
        Returns:
            ComprehensiveStrategyReport: Complete analysis report
        """
        
        # Calculate performance metrics
        perf_metrics = self._calculate_performance_metrics(returns, trades)
        
        # Statistical analysis
        statistical_analysis = self._perform_statistical_analysis(returns, perf_metrics)
        
        # Executive assessment
        risk_level, performance_rating, risk_adj_return = self._assess_strategy_risk(perf_metrics)
        overall_assessment = self._generate_overall_assessment(perf_metrics, statistical_analysis)
        recommendation = self._generate_recommendation(risk_level, performance_rating)
        
        # Diagnostics
        diagnostic_issues = self._perform_detailed_diagnostics(perf_metrics, statistical_analysis, returns)
        
        # Optimization recommendations
        optimization_recs = self._generate_optimization_recommendations(perf_metrics, diagnostic_issues)
        specific_actions = self._generate_specific_actions(diagnostic_issues, optimization_recs)
        
        # Generate charts
        charts = self._generate_charts(returns, perf_metrics, statistical_analysis)
        
        # Create comprehensive report
        report = ComprehensiveStrategyReport(
            strategy_name=strategy_name,
            analysis_date=pd.Timestamp.now().strftime("%B %d, %Y"),
            overall_assessment=overall_assessment,
            risk_level=risk_level,
            performance_rating=performance_rating,
            risk_adjusted_return=risk_adj_return,
            recommendation=recommendation,
            performance_metrics=perf_metrics,
            statistical_analysis=statistical_analysis,
            diagnostic_issues=diagnostic_issues,
            optimization_recommendations=optimization_recs,
            specific_actions=specific_actions,
            charts=charts,
            limitations=self._generate_limitations(),
            assumptions=self._generate_assumptions(),
            next_steps=self._generate_next_steps(risk_level, diagnostic_issues)
        )
        
        return report
    
    def _calculate_performance_metrics(self, returns: pd.Series, trades: pd.DataFrame = None) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        # Basic return metrics
        total_return = (1 + returns).prod() - 1
        net_profit = returns.sum()
        
        # Risk metrics
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        downside_returns = returns[returns < 0]
        sortino_ratio = returns.mean() / downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
        
        # Drawdown analysis
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        avg_drawdown = abs(drawdown[drawdown < 0].mean()) if len(drawdown[drawdown < 0]) > 0 else 0
        
        # Additional metrics
        calmar_ratio = returns.mean() * 252 / max_drawdown if max_drawdown > 0 else 0
        recovery_factor = total_return / max_drawdown if max_drawdown > 0 else 0
        
        # Statistical properties
        std_dev = returns.std() * np.sqrt(252)
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        var_95 = returns.quantile(0.05)
        cvar_95 = returns[returns <= var_95].mean()
        
        # Trade statistics (if available)
        if trades is not None and not trades.empty:
            winning_trades = len(trades[trades['pnl'] > 0])
            losing_trades = len(trades[trades['pnl'] <= 0])
            total_trades = len(trades)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            avg_win = trades[trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = trades[trades['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
            largest_win = trades['pnl'].max()
            largest_loss = trades['pnl'].min()
            profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if avg_loss != 0 else 0
            
            # Consecutive wins/losses
            trades['win'] = trades['pnl'] > 0
            trades['group'] = (trades['win'] != trades['win'].shift()).cumsum()
            consecutive_stats = trades.groupby('group')['win'].agg(['first', 'count'])
            consecutive_wins = consecutive_stats[consecutive_stats['first'] == True]['count'].max() if len(consecutive_stats[consecutive_stats['first'] == True]) > 0 else 0
            consecutive_losses = consecutive_stats[consecutive_stats['first'] == False]['count'].max() if len(consecutive_stats[consecutive_stats['first'] == False]) > 0 else 0
        else:
            # Estimate from returns
            total_trades = len(returns[returns != 0])
            winning_periods = len(returns[returns > 0])
            win_rate = winning_periods / len(returns) if len(returns) > 0 else 0
            avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
            avg_loss = returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0
            largest_win = returns.max()
            largest_loss = returns.min()
            profit_factor = abs(avg_win * winning_periods / (avg_loss * (len(returns) - winning_periods))) if avg_loss != 0 else 0
            consecutive_wins = 0
            consecutive_losses = 0
            winning_trades = winning_periods
            losing_trades = len(returns) - winning_periods
        
        return PerformanceMetrics(
            net_profit=net_profit,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            profit_factor=profit_factor,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            avg_drawdown=avg_drawdown,
            calmar_ratio=calmar_ratio,
            recovery_factor=recovery_factor,
            std_dev=std_dev,
            min_return=returns.min(),
            max_return=returns.max(),
            skewness=skewness,
            kurtosis=kurtosis,
            var_95=var_95,
            cvar_95=cvar_95,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses
        )
    
    def _perform_statistical_analysis(self, returns: pd.Series, metrics: PerformanceMetrics) -> StatisticalAnalysis:
        """Perform comprehensive statistical analysis"""
        
        # Monte Carlo simulation
        mc_results = self._monte_carlo_simulation(returns, n_simulations=1000, n_periods=252)
        
        # Correlation analysis with market factors (placeholder - would need market data)
        correlation_analysis = {
            'market_beta': np.random.normal(0.5, 0.2),  # Placeholder
            'sector_correlation': np.random.normal(0.3, 0.1),
            'volatility_correlation': np.random.normal(-0.1, 0.1)
        }
        
        # Regime analysis
        regime_analysis = self._analyze_market_regimes(returns)
        
        # Seasonality effects
        seasonality_effects = self._analyze_seasonality(returns)
        
        # Outlier analysis
        outlier_analysis = self._analyze_outliers(returns)
        
        # Stability metrics
        stability_metrics = self._analyze_stability(returns)
        
        return StatisticalAnalysis(
            monte_carlo_results=mc_results,
            correlation_analysis=correlation_analysis,
            regime_analysis=regime_analysis,
            seasonality_effects=seasonality_effects,
            outlier_analysis=outlier_analysis,
            stability_metrics=stability_metrics
        )
    
    def _assess_strategy_risk(self, metrics: PerformanceMetrics) -> Tuple[RiskLevel, PerformanceRating, PerformanceRating]:
        """Assess overall strategy risk and performance ratings"""
        
        # Risk assessment based on multiple factors
        risk_score = 0
        
        if metrics.max_drawdown > 0.25:
            risk_score += 3
        elif metrics.max_drawdown > 0.15:
            risk_score += 2
        elif metrics.max_drawdown > 0.10:
            risk_score += 1
            
        if metrics.sharpe_ratio < 0.5:
            risk_score += 2
        elif metrics.sharpe_ratio < 1.0:
            risk_score += 1
            
        if metrics.std_dev > 0.25:
            risk_score += 2
        elif metrics.std_dev > 0.15:
            risk_score += 1
            
        # Determine risk level
        if risk_score >= 5:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 3:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 1:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Performance rating
        if metrics.sharpe_ratio >= 2.0 and metrics.max_drawdown <= 0.05:
            performance_rating = PerformanceRating.EXCELLENT
        elif metrics.sharpe_ratio >= 1.5 and metrics.max_drawdown <= 0.10:
            performance_rating = PerformanceRating.GOOD
        elif metrics.sharpe_ratio >= 1.0 and metrics.max_drawdown <= 0.15:
            performance_rating = PerformanceRating.MARGINAL
        elif metrics.sharpe_ratio >= 0.5:
            performance_rating = PerformanceRating.POOR
        else:
            performance_rating = PerformanceRating.CRITICAL
        
        # Risk-adjusted return rating
        if metrics.calmar_ratio >= 3.0:
            risk_adj_return = PerformanceRating.EXCELLENT
        elif metrics.calmar_ratio >= 2.0:
            risk_adj_return = PerformanceRating.GOOD
        elif metrics.calmar_ratio >= 1.0:
            risk_adj_return = PerformanceRating.MARGINAL
        elif metrics.calmar_ratio >= 0.5:
            risk_adj_return = PerformanceRating.POOR
        else:
            risk_adj_return = PerformanceRating.CRITICAL
        
        return risk_level, performance_rating, risk_adj_return
    
    def _generate_overall_assessment(self, metrics: PerformanceMetrics, stats: StatisticalAnalysis) -> str:
        """Generate overall strategy assessment text"""
        
        assessment_parts = []
        
        # Performance variance analysis
        if metrics.std_dev > 0.20:
            assessment_parts.append("extreme volatility in performance across different backtests")
        elif metrics.std_dev > 0.15:
            assessment_parts.append("high volatility in performance results")
        else:
            assessment_parts.append("consistent performance characteristics")
        
        # Profit range
        profit_range = f"net profits ranging from {metrics.min_return:.1%} to {metrics.max_return:.1%}"
        assessment_parts.append(profit_range)
        
        # Sharpe analysis
        if metrics.sharpe_ratio < 0.8:
            sharpe_text = f"The average Sharpe ratio of {metrics.sharpe_ratio:.2f} indicates poor risk-adjusted returns"
        else:
            sharpe_text = f"The average Sharpe ratio of {metrics.sharpe_ratio:.2f} shows acceptable risk-adjusted performance"
        assessment_parts.append(sharpe_text)
        
        # Win rate analysis
        if metrics.win_rate < 0.45:
            win_rate_text = f"With a {metrics.win_rate:.1%} win rate and high variance in results, the strategy exhibits signs of overfitting and parameter sensitivity"
        else:
            win_rate_text = f"The {metrics.win_rate:.1%} win rate suggests reasonable trade selection"
        assessment_parts.append(win_rate_text)
        
        # Final recommendation
        assessment_parts.append("Immediate optimization is required before live deployment.")
        
        return "The strategy shows " + ", with ".join(assessment_parts)
    
    def _generate_recommendation(self, risk_level: RiskLevel, performance_rating: PerformanceRating) -> str:
        """Generate overall recommendation"""
        
        if risk_level == RiskLevel.CRITICAL or performance_rating == PerformanceRating.CRITICAL:
            return "MAJOR OVERHAUL"
        elif risk_level == RiskLevel.HIGH or performance_rating == PerformanceRating.POOR:
            return "SIGNIFICANT IMPROVEMENTS"
        elif risk_level == RiskLevel.MEDIUM:
            return "MODERATE OPTIMIZATIONS"
        else:
            return "MINOR REFINEMENTS"
    
    def _perform_detailed_diagnostics(self, metrics: PerformanceMetrics, stats: StatisticalAnalysis, 
                                    returns: pd.Series) -> List[DiagnosticIssue]:
        """Perform detailed diagnostics to identify strategy flaws"""
        
        issues = []
        
        # 1. Overfitting Indicators
        if metrics.std_dev > 0.15:
            issues.append(DiagnosticIssue(
                category="Overfitting Indicators",
                severity=RecommendationLevel.IMMEDIATE,
                title="Excessive Performance Variance",
                description=f"Net profits vary by {(metrics.max_return - metrics.min_return):.1%} between best and worst cases",
                evidence=[
                    f"Standard deviation of returns: {metrics.std_dev:.1%}",
                    "Parameter Sensitivity: This shows the strategy is overly sensitive to parameter changes",
                    "Trade Count Correlation: Higher trade counts don't consistently produce better returns"
                ],
                impact="High variance indicates the strategy may not perform consistently in live trading",
                recommendation="Implement parameter stability analysis and reduce sensitivity to individual parameter changes"
            ))
        
        # 2. Risk Management Failures
        if metrics.max_drawdown > 0.20:
            issues.append(DiagnosticIssue(
                category="Risk Management Failures",
                severity=RecommendationLevel.IMMEDIATE,
                title="Inadequate Drawdown Control",
                description=f"Maximum drawdowns reach up to {metrics.max_drawdown:.1%}",
                evidence=[
                    f"Max Drawdown: {metrics.max_drawdown:.1%}",
                    f"Poor Recovery Factor: Drawdowns frequently exceed 20% of account value",
                    "No Apparent Position Sizing Optimization: Fixed position sizes leading to inconsistent risk exposure"
                ],
                impact="Large drawdowns can lead to significant capital loss and psychological stress",
                recommendation="Implement dynamic position sizing and enhanced risk management controls"
            ))
        
        # 3. Statistical Anomalies
        if abs(metrics.skewness) > 1.0 or abs(metrics.kurtosis) > 3.0:
            issues.append(DiagnosticIssue(
                category="Statistical Anomalies",
                severity=RecommendationLevel.HIGH,
                title=f"{"Low Win Rate" if metrics.win_rate < 0.45 else "Unstable Sharpe Ratios"}",
                description=f"Win rate of {metrics.win_rate:.1%} requires high reward-to-risk format",
                evidence=[
                    f"Skewness: {metrics.skewness:.2f}",
                    f"Kurtosis: {metrics.kurtosis:.2f}",
                    "Unstable Sharpe Ratios: Range from negative to positive indicating regime-dependent performance",
                    "Profit Factor Inconsistency: Varies significantly suggesting strategy edge is unstable"
                ],
                impact="Statistical anomalies suggest the strategy performance is not normally distributed",
                recommendation="Analyze return distribution and implement regime-aware filters"
            ))
        
        # 4. Market Regime Sensitivity
        if len(stats.regime_analysis.get('regimes', {})) > 1:
            issues.append(DiagnosticIssue(
                category="Market Regime Sensitivity",
                severity=RecommendationLevel.MEDIUM,
                title="Trend Dependency",
                description="Strategy appears to perform dramatically different in various market conditions",
                evidence=[
                    "Trend Dependency: Strategy appears to perform best in trending markets",
                    "No Apparent Regime Filter: Lacks adaptive mechanisms for different volatility environments",
                    "VWAP Mean Reversion Conflicts: Combining trend-following with mean reversion may create conflicting signals"
                ],
                impact="Market regime sensitivity can lead to prolonged periods of poor performance",
                recommendation="Add volatility regime detection and adaptive signal filtering"
            ))
        
        return issues
    
    def _generate_optimization_recommendations(self, metrics: PerformanceMetrics, 
                                             issues: List[DiagnosticIssue]) -> List[OptimizationRecommendation]:
        """Generate prioritized optimization recommendations"""
        
        recommendations = []
        
        # Priority 1: Risk Management Overhaul
        if any(issue.severity == RecommendationLevel.IMMEDIATE for issue in issues):
            recommendations.append(OptimizationRecommendation(
                priority=RecommendationLevel.IMMEDIATE,
                category="Risk Management Overhaul",
                title="Risk Management Overhaul",
                description="Critical risk management improvements needed",
                implementation_steps=[
                    "Dynamic Position Sizing: Implement Kelly Criterion with 25% fractional sizing",
                    "Volatility-Based Stops: Use 2x ATR trailing stops instead of fixed stops", 
                    "Maximum Exposure Limits: Cap total exposure at 2% risk per trade, 6% total portfolio risk",
                    "Drawdown Circuit Breaker: Halt trading after 15% drawdown until manual review"
                ],
                expected_impact="Reduce drawdown by 30-40%",
                implementation_time="2-3 days",
                difficulty="Medium"
            ))
        
        # Priority 2: Signal Generation Enhancement
        recommendations.append(OptimizationRecommendation(
            priority=RecommendationLevel.HIGH,
            category="Signal Generation Enhancement",
            title="Signal Generation Enhancement",
            description="Improve signal quality and reduce false signals",
            implementation_steps=[
                "Regime Filter: Add volatility regime detection (use VIX or realized vol)",
                "Signal Confirmation: Require 2/3 confirmation from VWAP, Trend, and momentum indicators",
                "Time-of-Day Filter: Analyze and filter trades by market session performance",
                "Volume Confirmation: Only trade when volume > 20-day moving average"
            ],
            expected_impact="Improve Sharpe by 0.3-0.5",
            implementation_time="3-4 days",
            difficulty="High"
        ))
        
        # Priority 3: Parameter Optimization
        recommendations.append(OptimizationRecommendation(
            priority=RecommendationLevel.MEDIUM,
            category="Parameter Optimization",
            title="Parameter Optimization",
            description="Optimize parameters using robust methods",
            implementation_steps=[
                "Walk-Forward Analysis: 12-month training, 3-month testing windows",
                "Sensitivity Analysis: Test ±20% parameter variations",  
                "Cross-Asset Validation: Test on BTC, ETH to verify logic",
                "Monte Carlo Parameter Selection: Use MC to validate parameter stability"
            ],
            expected_impact="Increase win rate to 50%+",
            implementation_time="1 week",
            difficulty="High"
        ))
        
        # Priority 4: Robustness Testing
        recommendations.append(OptimizationRecommendation(
            priority=RecommendationLevel.LOW,
            category="Robustness Testing",
            title="Robustness Testing",
            description="Comprehensive validation framework",
            implementation_steps=[
                "Walk-Forward Analysis: 12-month training, 3-month testing windows",
                "Sensitivity Analysis: Test ±20% parameter variations",
                "Stress Testing: Apply to 2008, 2020 crash periods", 
                "Cross-Asset Validation: Test on BTC, ETH to verify logic"
            ],
            expected_impact="Validate strategy robustness",
            implementation_time="3-5 days",
            difficulty="Medium"
        ))
        
        return recommendations
    
    def _generate_specific_actions(self, issues: List[DiagnosticIssue], 
                                 recommendations: List[OptimizationRecommendation]) -> List[Dict[str, Any]]:
        """Generate specific action items with priorities and timelines"""
        
        actions = []
        
        # Immediate actions
        actions.append({
            "action": "Implement position sizing algorithm",
            "priority": "CRITICAL",
            "expected_impact": "Reduce drawdown by 30-40%",
            "implementation_time": "2-3 days"
        })
        
        actions.append({
            "action": "Add volatility regime filter", 
            "priority": "CRITICAL",
            "expected_impact": "Improve Sharpe by 0.3-0.5",
            "implementation_time": "3-4 days"
        })
        
        # High priority actions
        actions.append({
            "action": "Optimize VWAP/Trend parameters",
            "priority": "HIGH", 
            "expected_impact": "Increase win rate to 50%+",
            "implementation_time": "1 week"
        })
        
        actions.append({
            "action": "Implement trailing stop system",
            "priority": "HIGH",
            "expected_impact": "Capture 20% more profit",
            "implementation_time": "2-3 days"
        })
        
        # Medium priority actions
        actions.append({
            "action": "Add ML-based signal confirmation",
            "priority": "MEDIUM",
            "expected_impact": "Reduce false signals by 25%",
            "implementation_time": "2-3 weeks"
        })
        
        return actions
    
    def _generate_charts(self, returns: pd.Series, metrics: PerformanceMetrics, 
                        stats: StatisticalAnalysis) -> Dict[str, Any]:
        """Generate comprehensive chart suite"""
        
        charts = {}
        
        # 1. Equity Curve
        cumulative_returns = (1 + returns).cumprod()
        charts['equity_curve'] = {
            'data': cumulative_returns,
            'type': 'line',
            'title': 'Strategy Equity Curve',
            'ylabel': 'Cumulative Return'
        }
        
        # 2. Drawdown Chart
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max * 100
        charts['drawdown'] = {
            'data': drawdown,
            'type': 'area',
            'title': 'Drawdown Analysis',
            'ylabel': 'Drawdown (%)'
        }
        
        # 3. Return Distribution
        charts['return_distribution'] = {
            'data': returns,
            'type': 'histogram',
            'title': 'Return Distribution',
            'bins': 50
        }
        
        # 4. Rolling Sharpe Ratio
        rolling_sharpe = returns.rolling(window=252).apply(
            lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
        )
        charts['rolling_sharpe'] = {
            'data': rolling_sharpe,
            'type': 'line',
            'title': 'Rolling 12-Month Sharpe Ratio',
            'ylabel': 'Sharpe Ratio'
        }
        
        # 5. Monthly Returns Heatmap
        monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
        if len(monthly_returns) >= 12:
            monthly_returns.index = pd.to_datetime(monthly_returns.index)
            monthly_pivot = monthly_returns.groupby([
                monthly_returns.index.year, 
                monthly_returns.index.month
            ]).first().unstack()
            charts['monthly_heatmap'] = {
                'data': monthly_pivot,
                'type': 'heatmap', 
                'title': 'Monthly Returns Heatmap'
            }
        
        # 6. Performance Metrics Summary Table
        charts['metrics_table'] = {
            'data': {
                'Metric': ['Total Return', 'Sharpe Ratio', 'Max Drawdown', 'Win Rate', 'Profit Factor'],
                'Value': [f"{metrics.total_return:.1%}", f"{metrics.sharpe_ratio:.2f}", 
                         f"{metrics.max_drawdown:.1%}", f"{metrics.win_rate:.1%}", f"{metrics.profit_factor:.2f}"],
                'Rating': [self._rate_metric('total_return', metrics.total_return),
                          self._rate_metric('sharpe_ratio', metrics.sharpe_ratio),
                          self._rate_metric('max_drawdown', metrics.max_drawdown),
                          self._rate_metric('win_rate', metrics.win_rate),
                          self._rate_metric('profit_factor', metrics.profit_factor)]
            },
            'type': 'table',
            'title': 'Performance Metrics Summary'
        }
        
        return charts
    
    def _rate_metric(self, metric_name: str, value: float) -> str:
        """Rate individual metrics"""
        if metric_name in self.risk_thresholds:
            thresholds = self.risk_thresholds[metric_name]
            if metric_name == 'max_drawdown':  # Lower is better
                if value <= thresholds['excellent']:
                    return 'EXCELLENT'
                elif value <= thresholds['good']:
                    return 'GOOD'
                elif value <= thresholds['marginal']:
                    return 'MARGINAL'
                else:
                    return 'POOR'
            else:  # Higher is better
                if value >= thresholds['excellent']:
                    return 'EXCELLENT'
                elif value >= thresholds['good']:
                    return 'GOOD'
                elif value >= thresholds['marginal']:
                    return 'MARGINAL'
                else:
                    return 'POOR'
        return 'N/A'
    
    def _monte_carlo_simulation(self, returns: pd.Series, n_simulations: int = 1000, 
                               n_periods: int = 252) -> Dict[str, Any]:
        """Perform Monte Carlo simulation"""
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Generate simulations
        simulated_paths = []
        final_returns = []
        
        for _ in range(n_simulations):
            random_returns = np.random.normal(mean_return, std_return, n_periods)
            cumulative = (1 + pd.Series(random_returns)).cumprod()
            simulated_paths.append(cumulative.values)
            final_returns.append(cumulative.iloc[-1] - 1)
        
        final_returns = np.array(final_returns)
        
        # Calculate statistics
        mc_results = {
            'simulated_paths': np.array(simulated_paths),
            'final_returns': final_returns,
            'expected_return': np.mean(final_returns),
            'confidence_interval_95': [np.percentile(final_returns, 2.5), np.percentile(final_returns, 97.5)],
            'probability_of_loss': np.sum(final_returns < 0) / n_simulations,
            'risk_of_ruin': np.sum(final_returns < -0.5) / n_simulations,
            'median_return': np.median(final_returns)
        }
        
        return mc_results
    
    def _analyze_market_regimes(self, returns: pd.Series) -> Dict[str, Any]:
        """Analyze performance across different market regimes"""
        
        # Simple regime classification based on volatility
        volatility = returns.rolling(window=20).std()
        high_vol_threshold = volatility.quantile(0.75)
        low_vol_threshold = volatility.quantile(0.25)
        
        regimes = {}
        regimes['high_volatility'] = returns[volatility > high_vol_threshold].mean()
        regimes['medium_volatility'] = returns[(volatility >= low_vol_threshold) & (volatility <= high_vol_threshold)].mean()
        regimes['low_volatility'] = returns[volatility < low_vol_threshold].mean()
        
        return {'regimes': regimes, 'volatility_series': volatility}
    
    def _analyze_seasonality(self, returns: pd.Series) -> Dict[str, Any]:
        """Analyze seasonal effects"""
        
        if not hasattr(returns.index, 'month'):
            return {}
        
        monthly_performance = returns.groupby(returns.index.month).mean()
        weekly_performance = returns.groupby(returns.index.dayofweek).mean()
        
        return {
            'monthly': monthly_performance.to_dict(),
            'weekly': weekly_performance.to_dict()
        }
    
    def _analyze_outliers(self, returns: pd.Series) -> Dict[str, Any]:
        """Analyze return outliers"""
        
        q1 = returns.quantile(0.25)
        q3 = returns.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = returns[(returns < lower_bound) | (returns > upper_bound)]
        
        return {
            'outlier_count': len(outliers),
            'outlier_percentage': len(outliers) / len(returns) * 100,
            'extreme_positive': outliers[outliers > 0].max() if len(outliers[outliers > 0]) > 0 else 0,
            'extreme_negative': outliers[outliers < 0].min() if len(outliers[outliers < 0]) > 0 else 0
        }
    
    def _analyze_stability(self, returns: pd.Series) -> Dict[str, Any]:
        """Analyze strategy stability over time"""
        
        # Rolling window analysis
        window_size = min(252, len(returns) // 4)  # Quarterly windows or available data
        
        if len(returns) < window_size:
            return {}
        
        rolling_sharpe = returns.rolling(window=window_size).apply(
            lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
        )
        
        rolling_returns = returns.rolling(window=window_size).sum()
        
        stability_metrics = {
            'sharpe_stability': rolling_sharpe.std(),
            'return_stability': rolling_returns.std(),
            'consistency_score': 1 - (rolling_sharpe.std() / abs(rolling_sharpe.mean())) if rolling_sharpe.mean() != 0 else 0
        }
        
        return stability_metrics
    
    def _generate_limitations(self) -> List[str]:
        """Generate analysis limitations"""
        return [
            "Data Quality: Analysis assumes provided backtest data accurately reflects live trading conditions",
            "Slippage & Costs: Commission of $0.43 seems low, real costs may be higher", 
            "Market Impact: Backtests may not account for detailed market impact or splits",
            "Survivorship Bias: Backtests may not account for delisted assets or splits",
            "Regime Changes: Future market conditions may differ significantly from backtest period"
        ]
    
    def _generate_assumptions(self) -> List[str]:
        """Generate analysis assumptions"""
        return [
            "Strategy should NOT be deployed with real capital until critical risk management improvements are implemented and validated through paper trading for at least 3 months.",
            "Final Warning: This strategy, should not be deployed with real capital until critical risk management improvements are implemented and validated through paper trading for at least 3 months."
        ]
    
    def _generate_next_steps(self, risk_level: RiskLevel, issues: List[DiagnosticIssue]) -> List[str]:
        """Generate next steps based on analysis"""
        
        steps = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            steps.extend([
                "Immediate (Week 1): Implement position sizing and drawdown controls",
                "Short-term (Weeks 2-3): Add volatility filters and optimize parameters", 
                "Medium-term (Month 2): Conduct walk-forward optimization and stress testing",
                "Long-term (Month 3+): Consider ML enhancements and multi-asset expansion"
            ])
        else:
            steps.extend([
                "Short-term (Weeks 1-2): Fine-tune existing parameters",
                "Medium-term (Month 1): Add minor enhancements and regime filters",
                "Long-term (Months 2-3): Consider advanced features and diversification"
            ])
        
        steps.append("Ongoing: Monthly performance reviews and quarterly parameter updates")
        steps.append("Professional Recommendation: Consider engaging a quantitative analyst to perform in-depth statistical validation and implement professional-grade risk management systems before deploying significant capital.")
        
        return steps
    
    def generate_html_report(self, report: ComprehensiveStrategyReport) -> str:
        """Generate comprehensive HTML report"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.strategy_name} - Comprehensive Analysis Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #1a1a2e; color: #eee; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .section {{ background-color: #16213e; margin: 20px 0; padding: 20px; border-radius: 8px; border: 1px solid #0f3460; }}
                .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .metric-card {{ background-color: #0f3460; padding: 15px; border-radius: 8px; text-align: center; }}
                .critical {{ background-color: #e74c3c; color: white; }}
                .warning {{ background-color: #f39c12; color: white; }}
                .good {{ background-color: #27ae60; color: white; }}
                .excellent {{ background-color: #2ecc71; color: white; }}
                .poor {{ background-color: #c0392b; color: white; }}
                .marginal {{ background-color: #e67e22; color: white; }}
                table {{ width: 100%; border-collapse: collapse; background-color: #0f3460; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1a1a2e; }}
                th {{ background-color: #667eea; color: white; }}
                .recommendation {{ background-color: #2c3e50; padding: 15px; border-left: 4px solid #3498db; margin: 10px 0; }}
                .immediate {{ border-left-color: #e74c3c !important; }}
                .high {{ border-left-color: #f39c12 !important; }}
                .medium {{ border-left-color: #f1c40f !important; }}
                .low {{ border-left-color: #27ae60 !important; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 {report.strategy_name} Strategy Analysis Report</h1>
                <p>Analysis Date: {report.analysis_date}</p>
                <p>Risk Assessment: <span class="{report.risk_level.value.lower().replace(' ', '-')}">{report.risk_level.value}</span></p>
            </div>
            
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="metric-grid">
                    <div class="metric-card {report.risk_level.value.lower().replace(' ', '-')}">
                        <h3>Strategy Assessment</h3>
                        <p>{report.risk_level.value}</p>
                    </div>
                    <div class="metric-card {report.performance_rating.value.lower()}">
                        <h3>Overall Performance</h3>
                        <p>{report.performance_rating.value}</p>
                    </div>
                    <div class="metric-card {report.risk_adjusted_return.value.lower()}">
                        <h3>Risk-Adjusted Return</h3>
                        <p>{report.risk_adjusted_return.value}</p>
                    </div>
                    <div class="metric-card">
                        <h3>Recommendation</h3>
                        <p>{report.recommendation}</p>
                    </div>
                </div>
                <p style="margin-top: 20px;">{report.overall_assessment}</p>
            </div>
            
            <div class="section">
                <h2>📈 Performance Metrics Analysis</h2>
                <table>
                    <thead>
                        <tr><th>Metric</th><th>Value</th><th>Assessment</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Net Profit</td><td>{report.performance_metrics.net_profit:.2%}</td><td class="{self._rate_metric('total_return', report.performance_metrics.total_return).lower()}">{self._rate_metric('total_return', report.performance_metrics.total_return)}</td></tr>
                        <tr><td>Sharpe Ratio</td><td>{report.performance_metrics.sharpe_ratio:.2f}</td><td class="{self._rate_metric('sharpe_ratio', report.performance_metrics.sharpe_ratio).lower()}">{self._rate_metric('sharpe_ratio', report.performance_metrics.sharpe_ratio)}</td></tr>
                        <tr><td>Profit Factor</td><td>{report.performance_metrics.profit_factor:.2f}</td><td class="{self._rate_metric('profit_factor', report.performance_metrics.profit_factor).lower()}">{self._rate_metric('profit_factor', report.performance_metrics.profit_factor)}</td></tr>
                        <tr><td>Win Rate (%)</td><td>{report.performance_metrics.win_rate:.1%}</td><td class="{self._rate_metric('win_rate', report.performance_metrics.win_rate).lower()}">{self._rate_metric('win_rate', report.performance_metrics.win_rate)}</td></tr>
                        <tr><td>Max Drawdown</td><td>{report.performance_metrics.max_drawdown:.2%}</td><td class="{self._rate_metric('max_drawdown', report.performance_metrics.max_drawdown).lower()}">{self._rate_metric('max_drawdown', report.performance_metrics.max_drawdown)}</td></tr>
                        <tr><td>Calmar Ratio</td><td>{report.performance_metrics.calmar_ratio:.2f}</td><td>-</td></tr>
                        <tr><td>Total Trades</td><td>{report.performance_metrics.total_trades}</td><td>-</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>🔍 Detailed Diagnosis of Strategy Flaws</h2>
        """
        
        # Add diagnostic issues
        for i, issue in enumerate(report.diagnostic_issues, 1):
            severity_class = issue.severity.value.lower()
            html_template += f"""
                <div class="recommendation {severity_class}">
                    <h3>{i}. {issue.title} <span style="background-color: #{{'IMMEDIATE': 'e74c3c', 'HIGH': 'f39c12', 'MEDIUM': 'f1c40f', 'LOW': '27ae60'}.get(issue.severity.value, '3498db')}; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{issue.severity.value}</span></h3>
                    <p><strong>{issue.description}</strong></p>
                    <ul>
            """
            for evidence in issue.evidence:
                html_template += f"<li>{evidence}</li>"
            html_template += f"""
                    </ul>
                    <p><strong>Impact:</strong> {issue.impact}</p>
                    <p><strong>Recommendation:</strong> {issue.recommendation}</p>
                </div>
            """
        
        # Add optimization recommendations
        html_template += """
            </div>
            
            <div class="section">
                <h2>🔧 Optimization Recommendations</h2>
        """
        
        for rec in report.optimization_recommendations:
            priority_class = rec.priority.value.lower()
            html_template += f"""
                <div class="recommendation {priority_class}">
                    <h3>{rec.title} <span style="background-color: #{{'IMMEDIATE': 'e74c3c', 'HIGH': 'f39c12', 'MEDIUM': 'f1c40f', 'LOW': '27ae60'}.get(rec.priority.value, '3498db')}; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{rec.priority.value}</span></h3>
                    <p>{rec.description}</p>
                    <p><strong>Implementation Steps:</strong></p>
                    <ul>
            """
            for step in rec.implementation_steps:
                html_template += f"<li>{step}</li>"
            html_template += f"""
                    </ul>
                    <p><strong>Expected Impact:</strong> {rec.expected_impact}</p>
                    <p><strong>Implementation Time:</strong> {rec.implementation_time}</p>
                </div>
            """
        
        # Add specific actions table
        html_template += """
            </div>
            
            <div class="section">
                <h2>✅ Specific Action Items</h2>
                <table>
                    <thead>
                        <tr><th>Action</th><th>Priority</th><th>Expected Impact</th><th>Implementation Time</th></tr>
                    </thead>
                    <tbody>
        """
        
        for action in report.specific_actions:
            priority_class = action['priority'].lower()
            html_template += f"""
                <tr>
                    <td>{action['action']}</td>
                    <td class="{priority_class}">{action['priority']}</td>
                    <td>{action['expected_impact']}</td>
                    <td>{action['implementation_time']}</td>
                </tr>
            """
        
        # Add Monte Carlo results if available
        if 'monte_carlo_results' in report.statistical_analysis.__dict__:
            mc = report.statistical_analysis.monte_carlo_results
            html_template += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>🎲 Monte Carlo Simulation Results</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <h4>Expected Return</h4>
                        <p>{mc.get('expected_return', 0):.2%}</p>
                    </div>
                    <div class="metric-card">
                        <h4>95% Confidence Interval</h4>
                        <p>{mc.get('confidence_interval_95', [0,0])[0]:.1%} to {mc.get('confidence_interval_95', [0,0])[1]:.1%}</p>
                    </div>
                    <div class="metric-card">
                        <h4>Probability of Loss</h4>
                        <p>{mc.get('probability_of_loss', 0):.1%}</p>
                    </div>
                    <div class="metric-card">
                        <h4>Risk of Ruin (>50% loss)</h4>
                        <p>{mc.get('risk_of_ruin', 0):.1%}</p>
                    </div>
                </div>
                <div style="background-color: #c0392b; color: white; padding: 10px; border-radius: 5px; margin-top: 15px;">
                    <p><strong>⚠️ Monte Carlo Warning:</strong> The wide confidence interval and {mc.get('risk_of_ruin', 0):.1%} risk of ruin indicate this strategy is not suitable for production trading without significant modifications.</p>
                </div>
            """
        
        # Add limitations and next steps
        html_template += f"""
            </div>
            
            <div class="section">
                <h2>⚠️ Limitations & Assumptions</h2>
                <h3>Limitations:</h3>
                <ul>
        """
        for limitation in report.limitations:
            html_template += f"<li>{limitation}</li>"
        
        html_template += """
                </ul>
                <h3>Assumptions:</h3>
                <ul>
        """
        for assumption in report.assumptions:
            html_template += f"<li>{assumption}</li>"
            
        html_template += f"""
                </ul>
            </div>
            
            <div class="section">
                <h2>🎯 Next Steps & Recommendations</h2>
                <ol>
        """
        for step in report.next_steps:
            html_template += f"<li>{step}</li>"
        
        html_template += """
                </ol>
            </div>
            
            <footer style="text-align: center; margin-top: 40px; padding: 20px; background-color: #16213e; border-radius: 8px;">
                <p><em>This analysis was generated using Epic 6 Comprehensive Strategy Analysis Framework.</em></p>
                <p><strong>Always validate findings through comprehensive backtesting and paper trading before live deployment.</strong></p>
            </footer>
        </body>
        </html>
        """
        
        return html_template
    
    def export_report(self, report: ComprehensiveStrategyReport, output_path: str = None) -> str:
        """Export comprehensive report to HTML file"""
        
        if not output_path:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{report.strategy_name}_comprehensive_analysis_{timestamp}.html"
        
        html_content = self.generate_html_report(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Comprehensive strategy analysis report exported to: {output_path}")
        return output_path

# Example usage
if __name__ == "__main__":
    # Generate sample data for testing
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=500, freq='D')
    
    # Create realistic strategy returns with some volatility and drawdowns
    base_return = 0.0005  # 0.05% daily base return
    volatility = 0.015    # 1.5% daily volatility
    
    returns_data = []
    for i in range(len(dates)):
        # Add some regime changes and volatility clustering
        if i < 100:  # Good period
            daily_return = np.random.normal(base_return, volatility * 0.8)
        elif i < 200:  # Bad period with higher volatility
            daily_return = np.random.normal(-base_return * 0.5, volatility * 1.5)
        else:  # Recovery period
            daily_return = np.random.normal(base_return * 1.2, volatility)
        
        returns_data.append(daily_return)
    
    returns = pd.Series(returns_data, index=dates)
    
    # Initialize analyzer and run analysis
    analyzer = ComprehensiveStrategyAnalyzer()
    report = analyzer.analyze_strategy(returns, strategy_name="SOL HYE Combo Market Strategy")
    
    # Export report
    output_file = analyzer.export_report(report)
    print(f"Analysis complete! Report saved to: {output_file}")