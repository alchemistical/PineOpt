"""
Epic 6: Strategy Validation and Alpha Finding Pipeline
Comprehensive testing framework for converted strategies
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

# Import our backtesting components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from research.backtest.backtest_engine import BacktestEngine, BacktestConfig, BacktestResult
from research.analysis.ai_strategy_analyzer import AIStrategyAnalyzer, StrategyFeatures

logger = logging.getLogger(__name__)

@dataclass
class ValidationTest:
    """Individual validation test configuration"""
    name: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    initial_capital: float = 100000
    commission_rate: float = 0.001
    slippage_rate: float = 0.0001
    parameter_set: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Results of a single validation test"""
    test_name: str
    success: bool
    backtest_result: Optional[BacktestResult] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    risk_metrics: Dict[str, float] = field(default_factory=dict)
    execution_time: float = 0.0
    error_message: Optional[str] = None

@dataclass
class AlphaFindings:
    """Alpha discovery results"""
    strategy_id: str
    strategy_name: str
    alpha_score: float  # 0-100 scale
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    market_regime_performance: Dict[str, float]
    parameter_sensitivity: Dict[str, Dict[str, float]]
    risk_adjusted_returns: Dict[str, float]
    alpha_sources: List[str]
    recommendations: List[str]

@dataclass
class ValidationSuite:
    """Complete validation test suite results"""
    strategy_id: str
    strategy_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_score: float
    validation_results: List[ValidationResult] = field(default_factory=list)
    alpha_findings: Optional[AlphaFindings] = None
    recommendations: List[str] = field(default_factory=list)
    execution_time: float = 0.0

class StrategyValidationPipeline:
    """
    Comprehensive strategy validation and alpha finding pipeline
    
    Tests converted strategies across multiple market conditions,
    timeframes, and parameter sets to find alpha and validate robustness.
    """
    
    def __init__(self, database_path: str = None):
        self.backtest_engine = BacktestEngine(database_path)
        self.analyzer = AIStrategyAnalyzer()
        self.validation_configs = self._create_validation_configs()
        self.alpha_thresholds = self._create_alpha_thresholds()
    
    def _create_validation_configs(self) -> List[ValidationTest]:
        """Create comprehensive validation test configurations"""
        
        base_tests = []
        
        # Multi-timeframe tests
        timeframes = ['1h', '4h', '1d']
        symbols = ['BTCUSDT', 'ETHUSDT']
        
        # Market regime tests
        market_periods = [
            # Bull market period
            {
                'name': 'Bull_Market_2024',
                'start': '2024-01-01',
                'end': '2024-06-30',
                'regime': 'bull'
            },
            # Bear market period  
            {
                'name': 'Bear_Market_2024',
                'start': '2024-07-01',
                'end': '2024-12-31',
                'regime': 'bear'
            },
            # Volatile period
            {
                'name': 'High_Volatility_2025',
                'start': '2025-01-01',
                'end': '2025-08-22',
                'regime': 'volatile'
            }
        ]
        
        # Generate test combinations
        for symbol in symbols:
            for tf in timeframes:
                for period in market_periods:
                    base_tests.append(ValidationTest(
                        name=f"{symbol}_{tf}_{period['name']}",
                        symbol=symbol,
                        timeframe=tf,
                        start_date=period['start'],
                        end_date=period['end'],
                        parameter_set={'regime': period['regime']}
                    ))
        
        # Stress tests
        stress_tests = [
            ValidationTest(
                name='High_Commission_Stress',
                symbol='BTCUSDT',
                timeframe='1h',
                start_date='2024-01-01',
                end_date='2025-08-22',
                commission_rate=0.005,  # 0.5% commission
                parameter_set={'stress_type': 'high_commission'}
            ),
            ValidationTest(
                name='High_Slippage_Stress',
                symbol='BTCUSDT',
                timeframe='1h',
                start_date='2024-01-01',
                end_date='2025-08-22',
                slippage_rate=0.001,   # 0.1% slippage
                parameter_set={'stress_type': 'high_slippage'}
            ),
            ValidationTest(
                name='Low_Capital_Test',
                symbol='BTCUSDT',
                timeframe='1h',
                start_date='2025-01-01',
                end_date='2025-08-22',
                initial_capital=10000,  # $10K instead of $100K
                parameter_set={'stress_type': 'low_capital'}
            )
        ]
        
        return base_tests + stress_tests
    
    def _create_alpha_thresholds(self) -> Dict[str, float]:
        """Define alpha detection thresholds"""
        return {
            'min_sharpe_ratio': 0.5,
            'max_drawdown_pct': 20.0,
            'min_win_rate_pct': 40.0,
            'min_profit_factor': 1.2,
            'min_total_trades': 10,
            'alpha_score_threshold': 60.0  # Minimum for alpha classification
        }
    
    async def run_validation_suite(self, strategy_id: str, 
                                 custom_tests: Optional[List[ValidationTest]] = None,
                                 max_concurrent: int = 4) -> ValidationSuite:
        """
        Run complete validation suite for a strategy
        
        Args:
            strategy_id: Strategy ID to validate
            custom_tests: Optional custom test configurations
            max_concurrent: Maximum concurrent backtests
            
        Returns:
            ValidationSuite: Complete validation results
        """
        start_time = datetime.now()
        logger.info(f"Starting validation suite for strategy {strategy_id}")
        
        # Get strategy details
        strategy = self.backtest_engine.strategy_db.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        strategy_name = strategy.name
        
        # Use custom tests or default validation configs
        tests = custom_tests if custom_tests else self.validation_configs
        
        # Initialize validation suite
        suite = ValidationSuite(
            strategy_id=strategy_id,
            strategy_name=strategy_name,
            total_tests=len(tests),
            passed_tests=0,
            failed_tests=0,
            overall_score=0.0
        )
        
        # Run tests concurrently
        validation_results = []
        
        with ProcessPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all tests
            future_to_test = {
                executor.submit(self._run_single_validation, strategy_id, test): test
                for test in tests
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test = future_to_test[future]
                try:
                    result = future.result()
                    validation_results.append(result)
                    
                    if result.success:
                        suite.passed_tests += 1
                    else:
                        suite.failed_tests += 1
                        
                    logger.info(f"Test {test.name} {'passed' if result.success else 'failed'}")
                    
                except Exception as e:
                    logger.error(f"Test {test.name} crashed: {e}")
                    validation_results.append(ValidationResult(
                        test_name=test.name,
                        success=False,
                        error_message=str(e)
                    ))
                    suite.failed_tests += 1
        
        suite.validation_results = validation_results
        
        # Calculate overall score
        suite.overall_score = self._calculate_overall_score(validation_results)
        
        # Perform alpha analysis if enough tests passed
        if suite.passed_tests >= len(tests) * 0.5:  # At least 50% passed
            suite.alpha_findings = await self._find_alpha(strategy_id, validation_results)
        
        # Generate recommendations
        suite.recommendations = self._generate_recommendations(suite)
        
        suite.execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Validation suite complete: {suite.passed_tests}/{suite.total_tests} tests passed, "
                   f"Overall score: {suite.overall_score:.1f}, Alpha score: "
                   f"{suite.alpha_findings.alpha_score if suite.alpha_findings else 0:.1f}")
        
        return suite
    
    def _run_single_validation(self, strategy_id: str, test: ValidationTest) -> ValidationResult:
        """Run a single validation test"""
        try:
            start_time = datetime.now()
            
            # Create backtest configuration
            config = BacktestConfig(
                strategy_id=strategy_id,
                symbol=test.symbol,
                timeframe=test.timeframe,
                start_date=test.start_date,
                end_date=test.end_date,
                initial_capital=test.initial_capital,
                commission_rate=test.commission_rate,
                slippage_rate=test.slippage_rate,
                strategy_params=test.parameter_set
            )
            
            # Run backtest
            backtest_result = self.backtest_engine.run_backtest(config)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if backtest_result.success:
                # Extract key metrics
                portfolio_metrics = backtest_result.portfolio_metrics
                risk_metrics = backtest_result.risk_metrics
                
                performance_metrics = {
                    'total_return_pct': portfolio_metrics.total_return_pct,
                    'annualized_return_pct': portfolio_metrics.annualized_return_pct,
                    'sharpe_ratio': portfolio_metrics.sharpe_ratio,
                    'sortino_ratio': portfolio_metrics.sortino_ratio,
                    'calmar_ratio': portfolio_metrics.calmar_ratio,
                    'win_rate_pct': portfolio_metrics.win_rate_pct,
                    'profit_factor': portfolio_metrics.profit_factor,
                    'total_trades': portfolio_metrics.total_trades
                }
                
                risk_metrics_dict = {
                    'max_drawdown_pct': portfolio_metrics.max_drawdown_pct,
                    'max_drawdown_duration_days': portfolio_metrics.max_drawdown_duration_days,
                    'var_95_pct': risk_metrics.var_95_pct,
                    'current_exposure_pct': risk_metrics.current_exposure_pct,
                    'volatility_pct': portfolio_metrics.volatility_pct
                }
                
                return ValidationResult(
                    test_name=test.name,
                    success=True,
                    backtest_result=backtest_result,
                    performance_metrics=performance_metrics,
                    risk_metrics=risk_metrics_dict,
                    execution_time=execution_time
                )
            else:
                return ValidationResult(
                    test_name=test.name,
                    success=False,
                    execution_time=execution_time,
                    error_message=backtest_result.message
                )
                
        except Exception as e:
            return ValidationResult(
                test_name=test.name,
                success=False,
                execution_time=0.0,
                error_message=str(e)
            )
    
    def _calculate_overall_score(self, results: List[ValidationResult]) -> float:
        """Calculate overall validation score"""
        if not results:
            return 0.0
        
        total_score = 0.0
        valid_results = [r for r in results if r.success]
        
        if not valid_results:
            return 0.0
        
        # Weight different aspects
        weights = {
            'pass_rate': 0.3,
            'performance': 0.4,
            'risk': 0.3
        }
        
        # Pass rate score
        pass_rate = len(valid_results) / len(results)
        total_score += weights['pass_rate'] * pass_rate * 100
        
        # Average performance score
        avg_sharpe = np.mean([r.performance_metrics.get('sharpe_ratio', 0) for r in valid_results])
        avg_return = np.mean([r.performance_metrics.get('annualized_return_pct', 0) for r in valid_results])
        
        performance_score = min((max(avg_sharpe, 0) / 2.0) * 100, 100)  # Normalize Sharpe to 0-100
        total_score += weights['performance'] * performance_score
        
        # Risk score (lower drawdown = higher score)
        avg_drawdown = np.mean([abs(r.risk_metrics.get('max_drawdown_pct', 50)) for r in valid_results])
        risk_score = max(0, 100 - avg_drawdown * 2)  # Normalize drawdown to score
        total_score += weights['risk'] * risk_score
        
        return min(total_score, 100.0)
    
    async def _find_alpha(self, strategy_id: str, results: List[ValidationResult]) -> AlphaFindings:
        """Analyze results to find alpha sources and calculate alpha score"""
        
        strategy = self.backtest_engine.strategy_db.get_strategy(strategy_id)
        valid_results = [r for r in results if r.success]
        
        if not valid_results:
            return AlphaFindings(
                strategy_id=strategy_id,
                strategy_name=strategy.name,
                alpha_score=0.0,
                sharpe_ratio=0.0,
                max_drawdown=100.0,
                win_rate=0.0,
                profit_factor=0.0,
                market_regime_performance={},
                parameter_sensitivity={},
                risk_adjusted_returns={},
                alpha_sources=[],
                recommendations=["No valid backtest results for alpha analysis"]
            )
        
        # Calculate aggregate metrics
        sharpe_ratios = [r.performance_metrics.get('sharpe_ratio', 0) for r in valid_results]
        returns = [r.performance_metrics.get('annualized_return_pct', 0) for r in valid_results]
        drawdowns = [abs(r.risk_metrics.get('max_drawdown_pct', 50)) for r in valid_results]
        win_rates = [r.performance_metrics.get('win_rate_pct', 0) for r in valid_results]
        profit_factors = [r.performance_metrics.get('profit_factor', 0) for r in valid_results]
        
        avg_sharpe = np.mean(sharpe_ratios)
        avg_return = np.mean(returns)
        avg_drawdown = np.mean(drawdowns)
        avg_win_rate = np.mean(win_rates)
        avg_profit_factor = np.mean(profit_factors)
        
        # Calculate alpha score
        alpha_score = 0.0
        
        # Sharpe ratio component (0-30 points)
        if avg_sharpe >= self.alpha_thresholds['min_sharpe_ratio']:
            alpha_score += min(avg_sharpe / 2.0 * 30, 30)
        
        # Drawdown component (0-25 points)
        if avg_drawdown <= self.alpha_thresholds['max_drawdown_pct']:
            drawdown_score = (1 - avg_drawdown / 50.0) * 25
            alpha_score += max(drawdown_score, 0)
        
        # Win rate component (0-20 points)
        if avg_win_rate >= self.alpha_thresholds['min_win_rate_pct']:
            win_rate_score = (avg_win_rate / 100.0) * 20
            alpha_score += win_rate_score
        
        # Profit factor component (0-15 points)
        if avg_profit_factor >= self.alpha_thresholds['min_profit_factor']:
            pf_score = min((avg_profit_factor - 1.0) / 2.0 * 15, 15)
            alpha_score += pf_score
        
        # Consistency component (0-10 points)
        sharpe_std = np.std(sharpe_ratios)
        consistency_score = max(0, 10 - sharpe_std * 5)  # Lower std = higher score
        alpha_score += consistency_score
        
        # Analyze market regime performance
        regime_performance = {}
        for result in valid_results:
            regime = result.backtest_result.config.strategy_params.get('regime', 'unknown')
            if regime != 'unknown':
                if regime not in regime_performance:
                    regime_performance[regime] = []
                regime_performance[regime].append(result.performance_metrics.get('sharpe_ratio', 0))
        
        # Average performance by regime
        for regime, sharpes in regime_performance.items():
            regime_performance[regime] = np.mean(sharpes)
        
        # Risk-adjusted returns analysis
        risk_adjusted_returns = {
            'sharpe_ratio': avg_sharpe,
            'sortino_ratio': np.mean([r.performance_metrics.get('sortino_ratio', 0) for r in valid_results]),
            'calmar_ratio': np.mean([r.performance_metrics.get('calmar_ratio', 0) for r in valid_results]),
            'risk_return_ratio': avg_return / max(avg_drawdown, 1.0)
        }
        
        # Identify alpha sources
        alpha_sources = []
        
        if avg_sharpe > 1.0:
            alpha_sources.append("High risk-adjusted returns")
        if avg_drawdown < 10.0:
            alpha_sources.append("Low drawdown profile")
        if avg_win_rate > 60.0:
            alpha_sources.append("High win rate consistency")
        if len(set(regime_performance.values())) > 1 and min(regime_performance.values()) > 0:
            alpha_sources.append("Multi-regime robustness")
        if consistency_score > 7:
            alpha_sources.append("Consistent performance across tests")
        
        # Generate alpha-specific recommendations
        recommendations = []
        
        if alpha_score >= self.alpha_thresholds['alpha_score_threshold']:
            recommendations.append("✅ Alpha detected - strategy shows potential edge")
            recommendations.append("Consider live testing with small position sizes")
        else:
            recommendations.append("⚠️ Limited alpha potential - optimization needed")
        
        if avg_sharpe < 1.0:
            recommendations.append("Focus on improving risk-adjusted returns")
        if avg_drawdown > 15.0:
            recommendations.append("Implement stronger risk management")
        if avg_win_rate < 50.0:
            recommendations.append("Review entry/exit logic for better hit rate")
        
        return AlphaFindings(
            strategy_id=strategy_id,
            strategy_name=strategy.name,
            alpha_score=alpha_score,
            sharpe_ratio=avg_sharpe,
            max_drawdown=avg_drawdown,
            win_rate=avg_win_rate,
            profit_factor=avg_profit_factor,
            market_regime_performance=regime_performance,
            parameter_sensitivity={},  # TODO: Implement parameter optimization
            risk_adjusted_returns=risk_adjusted_returns,
            alpha_sources=alpha_sources,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, suite: ValidationSuite) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Overall performance recommendations
        if suite.overall_score >= 80:
            recommendations.append("🎉 Excellent validation results - strategy ready for live testing")
        elif suite.overall_score >= 60:
            recommendations.append("✅ Good validation results - minor optimizations recommended")
        elif suite.overall_score >= 40:
            recommendations.append("⚠️ Average performance - significant improvements needed")
        else:
            recommendations.append("❌ Poor validation results - major revision required")
        
        # Pass rate analysis
        pass_rate = suite.passed_tests / suite.total_tests
        if pass_rate < 0.5:
            recommendations.append("🔧 Low test pass rate - check strategy logic and error handling")
        
        # Performance analysis
        valid_results = [r for r in suite.validation_results if r.success]
        if valid_results:
            avg_sharpe = np.mean([r.performance_metrics.get('sharpe_ratio', 0) for r in valid_results])
            if avg_sharpe < 0.5:
                recommendations.append("📈 Low Sharpe ratio - focus on risk-adjusted returns")
            
            avg_drawdown = np.mean([abs(r.risk_metrics.get('max_drawdown_pct', 50)) for r in valid_results])
            if avg_drawdown > 20:
                recommendations.append("🛡️ High drawdown - strengthen risk management")
        
        # Alpha-specific recommendations
        if suite.alpha_findings:
            if suite.alpha_findings.alpha_score >= 70:
                recommendations.append("⭐ Strong alpha potential detected")
            elif suite.alpha_findings.alpha_score >= 50:
                recommendations.append("💫 Moderate alpha potential - optimization opportunity")
            else:
                recommendations.append("🔍 Limited alpha - consider strategy redesign")
        
        return recommendations
    
    def generate_validation_report(self, suite: ValidationSuite) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        valid_results = [r for r in suite.validation_results if r.success]
        
        report = {
            "strategy_info": {
                "id": suite.strategy_id,
                "name": suite.strategy_name,
                "validation_date": datetime.now().isoformat()
            },
            
            "summary": {
                "total_tests": suite.total_tests,
                "passed_tests": suite.passed_tests,
                "failed_tests": suite.failed_tests,
                "pass_rate_pct": (suite.passed_tests / suite.total_tests) * 100,
                "overall_score": suite.overall_score,
                "execution_time_minutes": suite.execution_time / 60
            },
            
            "performance_analysis": {},
            "risk_analysis": {},
            "alpha_analysis": {},
            "test_results": [],
            "recommendations": suite.recommendations
        }
        
        if valid_results:
            # Performance metrics
            sharpe_ratios = [r.performance_metrics.get('sharpe_ratio', 0) for r in valid_results]
            returns = [r.performance_metrics.get('annualized_return_pct', 0) for r in valid_results]
            win_rates = [r.performance_metrics.get('win_rate_pct', 0) for r in valid_results]
            
            report["performance_analysis"] = {
                "avg_sharpe_ratio": np.mean(sharpe_ratios),
                "sharpe_ratio_std": np.std(sharpe_ratios),
                "avg_annual_return_pct": np.mean(returns),
                "return_consistency": 1 / (1 + np.std(returns)),  # Higher = more consistent
                "avg_win_rate_pct": np.mean(win_rates),
                "best_sharpe_ratio": max(sharpe_ratios),
                "worst_sharpe_ratio": min(sharpe_ratios)
            }
            
            # Risk metrics
            drawdowns = [abs(r.risk_metrics.get('max_drawdown_pct', 50)) for r in valid_results]
            volatilities = [r.risk_metrics.get('volatility_pct', 0) for r in valid_results]
            
            report["risk_analysis"] = {
                "avg_max_drawdown_pct": np.mean(drawdowns),
                "max_drawdown_pct": max(drawdowns),
                "drawdown_consistency": 1 / (1 + np.std(drawdowns)),
                "avg_volatility_pct": np.mean(volatilities),
                "risk_adjusted_return": np.mean(returns) / max(np.mean(volatilities), 1.0)
            }
        
        # Alpha analysis
        if suite.alpha_findings:
            report["alpha_analysis"] = {
                "alpha_score": suite.alpha_findings.alpha_score,
                "alpha_detected": suite.alpha_findings.alpha_score >= 60,
                "alpha_sources": suite.alpha_findings.alpha_sources,
                "regime_performance": suite.alpha_findings.market_regime_performance,
                "risk_adjusted_metrics": suite.alpha_findings.risk_adjusted_returns
            }
        
        # Individual test results
        for result in suite.validation_results:
            test_data = {
                "test_name": result.test_name,
                "success": result.success,
                "execution_time": result.execution_time
            }
            
            if result.success:
                test_data.update({
                    "sharpe_ratio": result.performance_metrics.get('sharpe_ratio', 0),
                    "annual_return_pct": result.performance_metrics.get('annualized_return_pct', 0),
                    "max_drawdown_pct": result.risk_metrics.get('max_drawdown_pct', 0),
                    "win_rate_pct": result.performance_metrics.get('win_rate_pct', 0),
                    "total_trades": result.performance_metrics.get('total_trades', 0)
                })
            else:
                test_data["error_message"] = result.error_message
            
            report["test_results"].append(test_data)
        
        return report

# Example usage and testing
async def main():
    pipeline = StrategyValidationPipeline()
    
    # Example: Run validation suite for a strategy
    strategy_id = "test_strategy_id"
    
    # Create custom test for demonstration
    custom_tests = [
        ValidationTest(
            name="BTC_1H_Recent",
            symbol="BTCUSDT",
            timeframe="1h",
            start_date="2025-08-01",
            end_date="2025-08-22",
            parameter_set={"rsi_length": 14}
        )
    ]
    
    try:
        suite = await pipeline.run_validation_suite(strategy_id, custom_tests)
        report = pipeline.generate_validation_report(suite)
        
        print("Validation Results:")
        print(f"Overall Score: {suite.overall_score:.1f}")
        print(f"Tests Passed: {suite.passed_tests}/{suite.total_tests}")
        if suite.alpha_findings:
            print(f"Alpha Score: {suite.alpha_findings.alpha_score:.1f}")
            print(f"Alpha Sources: {suite.alpha_findings.alpha_sources}")
        
    except Exception as e:
        print(f"Validation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())