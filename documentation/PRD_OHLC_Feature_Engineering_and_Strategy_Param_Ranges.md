# PRD: OHLC Feature Engineering and Strategy Parameter Lab

## 1. Overview / Scope
- Build a research lab to derive robust features from OHLC-only data, select non-redundant features, and define parameter ranges for strategies (VWAP-Ichimoku, Bollinger, TSV proxy, Vidya). 
- Provide backtesting, regime-aware validation, and reporting to guide production strategy settings.

## 2. Goals
- Generate a rich feature set from OHLC (no volume) with defensible approximations where needed.
- Sweep parameter ranges for core components and identify stable zones via statistical evidence.
- Select features by reducing redundancy and aligning with functional roles (trend bias, timing, noise filter, exit/continuation).
- Evaluate performance across regimes (trending vs. ranging) and avoid overfitting via cross-validation.

## 3. Non-goals
- Live trading connectivity, order management, brokerage integration.
- Data vendor ingestion pipelines; assume data is already available locally.

## 4. Users / Stakeholders
- Quant researchers: iterate on feature sets and parameter sweeps.
- Strategy engineers: consume recommended parameter ranges and feature sets.
- PM/Stakeholders: review reports and acceptance criteria to greenlight production settings.

## 5. Data
- Input: OHLC time series (12H bars typical). Optional volume if available later.
- Required columns: time/date (parseable or Excel serial), open, high, low, close. Volume optional.
- Frequency: baseline 12H; design should be frequency-agnostic.
- Quality checks: monotonic timestamps, non-negative prices, high ≥ max(open, close), low ≤ min(open, close).

## 6. Feature Engineering (from OHLC)
- Returns & Volatility
  - Simple returns and log returns across windows (e.g., 1, 2, 4, 8, 12, 24 bars).
  - Realized volatility: rolling std of returns over windows (e.g., 10–60 bars).
  - Use to calibrate Bollinger length and stdDev.
- Rolling High–Low Dynamics
  - True Range and ATR (Average True Range) over multiple windows; breakout threshold calibration.
  - Range expansion/contraction flags; close location value (CLV) for position of close in bar range.
- VWAP Proxy (no volume)
  - Approximate VWAP using price proxies: ohlc4 = (O+H+L+C)/4, hl2 = (H+L)/2, hlc3 = (H+L+C)/3.
  - Rolling mean/EMA of proxy as volume-neutral VWAP analog; optionally blend with regime-weighted averages.
- Trend Proxies (Ichimoku-inspired)
  - Tenkan/Kijun via rolling medians/means of high/low midpoints: mid(H_n, L_n) or SMA/EMA of hl2.
  - Slow (bias) vs. fast (timing) components.
- Bollinger Bands
  - Bands over selected source (close/hl2/ohlc4) with rolling std; bandwidth and %B as features.
- TSV (proxy) using CLV
  - TSV ≈ cumulative sum of CLV or range-weighted direction; EMA-smooth for signal stability.
- Vidya (Variable Index Dynamic Avg)
  - Adaptive moving average using volatility/efficiency ratio as adaptive factor; tested on multiple sources.
- Derived Slopes/Curvature
  - First derivative (slope) of MAs/Vidya; changes in slope as timing features.

## 7. Strategy Parameter Ranges (sweeps)
- Slow Tenkan/Kijun “VWAP” lengths
  - Range: 20–120 bars (≈10–60 days on 12H).
  - Selection: maximize trend persistence (e.g., rolling Sharpe of trend-following signals).
- Fast Tenkan/Kijun “VWAP” lengths
  - Range: 5–30 bars (≈2.5–15 days).
  - Selection: minimize whipsaw frequency during sideways regimes.
- Bollinger Bands
  - Length: 20–50 bars; StdDev: 1.5–2.5.
  - Validation: breakout hit ratio vs. false signals; alignment with realized vol cycles.
- TSV (proxy) length & EMA
  - Length: 10–30 bars; EMA smoothing: 5–20 bars.
  - Objective: filter non-participated moves; confirm breaks only with participation.
- Vidya length & source
  - Length: 20–60 bars; sources tested: close, hl2, ohlc4.
  - Objective: maximize trend capture, minimize premature exits.

## 8. Feature Selection Process
1) Redundancy Check
- PCA and correlation heatmaps on returns, ATR, MA slopes, Bollinger bandwidth, TSV, etc.
- Drop highly collinear features (e.g., ATR and Bollinger bandwidth often overlap).
2) Role-based Partitioning
- Trend bias: slow VWAP-Ichimoku components.
- Timing: fast VWAP-Ichimoku components.
- Noise filter: Bollinger + TSV proxy.
- Exit/continuation: Vidya, MA slopes.
3) Regime-aware Validation
- Regime classification via Hurst exponent and/or ADX and rolling volatility.
- Cross-validate within regimes and across time; prefer features stable across regimes or gated by regime.

## 9. Objective Functions / Evaluation
- Catch trends: slow/fast VWAP-Ichimoku crossover persistence; run-length of profitable trends.
- Reduce noise: triggers require Bollinger + TSV agreement; penalize whipsaws.
- Stay adaptive: Vidya trailing’s responsiveness vs. drawdown; efficiency ratio targets.
- Portfolio metrics (per strategy): Sharpe, Sortino, Calmar, hit rate, average win/loss, max DD, turnover, whipsaw rate.

## 10. Dependencies
- Core: pandas, numpy, scipy, scikit-learn.
- Technical: ta or TA-Lib; custom implementations for VWAP proxy, Ichimoku lines, TSV (CLV-based), Vidya.
- Statistical: statsmodels (Hurst, time series models), empyrical/ffn for risk metrics.
- Backtesting/Analysis: vectorbt (speed), zipline-reloaded (robustness), quantstats/pyfolio-reloaded for tearsheets.
- Optimization (optional): cvxpy, skfolio for portfolio-level evaluation.

## 11. Data Processing & Experiments
- Parameter sweeps: 
  - Slow 20–120; Fast 5–30; Bollinger (L=20–50, K=1.5–2.5); TSV (L=10–30, EMA=5–20); Vidya (L=20–60).
- Rolling windows: 10–60 bars for vol/Sharpe; adaptive by frequency.
- Regime classification: trending vs. ranging via Hurst/ADX thresholds; store regime labels.
- Cross-validation: expanding window and k-fold by time blocks; report mean and variance of metrics.

## 12. Deliverables
- Feature library notebook/module generating all features from OHLC.
- Parameter sweep reports with recommended ranges per component and regime.
- Regime-aware backtest results and summary tables.
- Correlation heatmaps, PCA scree plots, feature importance summaries.
- Reproducible scripts (CLI) to run sweeps and produce artifacts.

## 13. Acceptance Criteria
- All features reproducible from OHLC-only inputs (no volume assumed) with unit tests for key calculations.
- Parameter recommendations backed by out-of-sample robustness (≤ 10% degradation between IS/OOS Sharpe).
- Regime detection validated; results segmented by regime with consistent behavior.
- Reports generated for a reference dataset (e.g., 3+ instruments, 3+ years) within target runtime.

## 14. KPIs / Success Metrics
- Research throughput: time to run a full sweep under X hours (define X based on data size).
- Robustness: stability of recommended ranges across time splits and instruments.
- Noise reduction: whipsaw rate reduction vs. baseline by ≥ Y% (set target).
- Trend capture: improvement in average trend run-length or MAR vs. baseline by ≥ Z%.

## 15. Milestones & Timeline
- M1: Data loaders, quality checks, baseline features (Week 1).
- M2: Full feature set + unit tests (Week 2).
- M3: Parameter sweep engine + regime classifier (Week 3).
- M4: Backtesting integration + reports (Week 4).
- M5: Recommendation synthesis + documentation (Week 5).

## 16. Risks & Mitigations
- Overfitting to specific periods/regimes → strict time-series CV, holdout periods, instrument diversity.
- Proxy inaccuracies (VWAP/TSV) → sensitivity analysis; compare multiple proxy definitions.
- Collinearity inflates variance → PCA/regularization and role-based selection.
- Compute cost → vectorized ops, caching, multiprocessing where safe.

## 17. Open Questions
- Which instruments/universes to prioritize for validation?
- Final metric weighting (Sharpe vs. MAR vs. whipsaw penalties)?
- Thresholds for regime classification (Hurst/ADX) per instrument or global?

## 18. Appendix: Implementation Notes
- Sources to test: close, hl2=(H+L)/2, ohlc4=(O+H+L+C)/4, hlc3=(H+L+C)/3.
- CLV = (C - L) - (H - C) / (H - L) with guards for zero range; accumulate/EMA for TSV proxy.
- Vidya: ER = |C - C_n| / Σ|C_i - C_{i-1}|; alpha = (ER*(2/(N+1)-2/(M+1)) + 2/(M+1))^p; tune N,M,p.
- Suggested evaluation: use vectorbt for fast grid sweeps, quantstats for tearsheets, statsmodels for Hurst.
