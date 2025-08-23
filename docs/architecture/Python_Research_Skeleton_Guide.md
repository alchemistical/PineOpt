# Python Research Skeleton: Implementation Guide

This document describes how to set up a reproducible Python research skeleton to implement the PRD: env setup, requirements, repo structure, feature library, sweep engine, notebooks, and CLI.

## 1) Environment Setup

- **Option A (Conda/Mamba)**
  ```bash
  mamba create -n pineopt python=3.10 -y
  mamba activate pineopt
  ```
- **Option B (venv + uv/pip)**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  ```

- **Install requirements** (after creating `requirements.txt` below):
  ```bash
  pip install -r requirements.txt
  ```

- **Optional dev tools**
  ```bash
  pip install pre-commit black isort ruff mypy jupyterlab
  pre-commit install
  ```

## 2) Requirements

Create `requirements.txt` at repo root (pin or cap versions as preferred):

```
# Core
pandas>=2.0
numpy>=1.24
scipy>=1.10
scikit-learn>=1.3

# Technical analysis
ta>=0.11.0
# OR: TA-Lib (if system allows)
# TA-Lib==0.4.28

# Stats / time series
statsmodels>=0.14
empyrical-reloaded>=0.5
ffn>=0.3.6
arch>=6.3

# Backtesting / analysis
vectorbt>=0.25.4
zipline-reloaded>=3.0
quantstats>=0.0.62
pyfolio-reloaded>=0.9.6

# Optimization (optional)
cvxpy>=1.4
skfolio>=0.5

# Utilities
pyyaml>=6.0
joblib>=1.3
loguru>=0.7
tqdm>=4.66
matplotlib>=3.8
seaborn>=0.13
```

Notes:
- TA-Lib may require native deps; `ta` is pure-Python and sufficient for most indicators.
- `vectorbt` is recommended for fast parameter sweeps; `zipline-reloaded` for event-driven tests when needed.

## 3) Project Structure

Create the following structure under the project root (parallel to `Documentations/`):

```
research/
  __init__.py
  config/
    __init__.py
    defaults.yaml
  data/
    __init__.py
    loaders.py           # read CSV/Parquet, resample, QC
    quality.py           # validations: monotone time, price sanity
  features/
    __init__.py
    core.py              # returns, log-returns, realized vol, ATR, CLV
    proxies.py           # VWAP proxies (ohlc4, hl2, hlc3), composite sources
    ichimoku.py          # Tenkan/Kijun (mid(H,L) or MA/median variants)
    bollinger.py         # bands, %B, bandwidth
    tsv.py               # TSV proxy using CLV + EMA
    vidya.py             # variable index dynamic average
    utils.py             # rolling ops, slope, zscore, efficiency ratio
  regimes/
    __init__.py
    hurst.py             # Hurst exponent
    adx.py               # ADX-based regime flags
    classify.py          # regime labeling, thresholds
  backtest/
    __init__.py
    vectorbt_runner.py   # fast grid sweeps
    zipline_runner.py    # optional event-driven tests
  sweeps/
    __init__.py
    engine.py            # parameter grid, CV splits, metrics aggregation
    metrics.py           # Sharpe, Sortino, MAR, whipsaw, turnover
    reporting.py         # CSV/Parquet + plots + QuantStats/tearsheets
  cli/
    __init__.py
    run_sweep.py         # CLI entrypoint
    build_features.py    # CLI to generate/save features
  notebooks/
    01-explore-data.ipynb
    02-features-validation.ipynb
    03-regime-detection.ipynb
    04-parameter-sweeps.ipynb
    05-report-and-recommend.ipynb
outputs/
  datasets/             # cached cleaned datasets
  features/             # persisted feature matrices
  sweeps/               # sweep results
  reports/              # plots, html, csv
```

## 4) Data Loading and Quality Checks

Example `research/data/loaders.py` signatures:
```python
import pandas as pd
from pathlib import Path

def read_ohlc(path: str | Path, tz: str | None = None) -> pd.DataFrame:
    """Read OHLC from CSV/Parquet with columns [time, open, high, low, close, (volume)].
    Returns a DateTimeIndex DataFrame sorted ascending.
    """
    ...

def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample to a new frequency (e.g., '12H') with OHLC aggregation."""
    ...
```

`research/data/quality.py` checks:
- **Timestamp monotonicity** and duplicate removal.
- **Price sanity**: `high >= max(open, close)`, `low <= min(open, close)`, all positive.
- **Gap flags** for missing bars; optional forward-fill policy for features only (not prices).

## 5) Feature Library

Key functions (sketches only):
```python
# research/features/core.py
import pandas as pd

def returns(df: pd.DataFrame, log: bool = True, periods=(1,2,4,8,12,24)) -> pd.DataFrame:
    ...

def realized_vol(df: pd.DataFrame, window: int) -> pd.Series:
    ...

# research/features/proxies.py

def source_close(df): return df["close"]

def source_hl2(df): return (df["high"] + df["low"]) / 2

def source_ohlc4(df): return (df[["open","high","low","close"]].sum(axis=1)) / 4

# research/features/ichimoku.py

def rolling_mid(high: pd.Series, low: pd.Series, n: int) -> pd.Series:
    mid_h = high.rolling(n).max()
    mid_l = low.rolling(n).min()
    return (mid_h + mid_l) / 2

# research/features/bollinger.py

def bollinger(src: pd.Series, length: int, k: float):
    ma = src.rolling(length).mean()
    sd = src.rolling(length).std(ddof=0)
    upper = ma + k*sd; lower = ma - k*sd
    pctb = (src - lower) / (upper - lower)
    bandwidth = (upper - lower) / ma
    return ma, upper, lower, pctb, bandwidth

# research/features/tsv.py

def clv(df: pd.DataFrame) -> pd.Series:
    rng = (df["high"] - df["low"]).replace(0, pd.NA)
    val = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / rng
    return val.fillna(0)

# research/features/vidya.py

def efficiency_ratio(src: pd.Series, n: int) -> pd.Series:
    change = (src - src.shift(n)).abs()
    volatility = src.diff().abs().rolling(n).sum()
    return (change / volatility).clip(lower=0, upper=1)
```

## 6) Regime Detection

- **Hurst-based**: rolling H (e.g., window 200); trending if H > 0.55, ranging if H < 0.45.
- **ADX-based**: compute ADX; trending if ADX > T_high; ranging if ADX < T_low.
- Store regime labels in a column (e.g., `regime ∈ {trend, range, neutral}`). Thresholds configurable.

## 7) Backtesting Runners

- **vectorbt approach** (`research/backtest/vectorbt_runner.py`):
  - Build entry/exit signals from engineered features.
  - Vectorize grid of parameters; compute metrics per grid point.
  - Persist equity curves and KPIs; optional QuantStats report.

- **zipline-reloaded** (optional):
  - Event-driven strategy to validate signal realism with slippage/commission models.

## 8) Sweep Engine

`research/sweeps/engine.py` responsibilities:
- Expand parameter grids (e.g., slow=[20..120], fast=[5..30], bb_len=[20..50], bb_k=[1.5..2.5], tsv_len=[10..30], tsv_ema=[5..20], vidya=[20..60]).
- Apply **time-series cross-validation**: expanding window or blocked k-fold.
- Compute metrics with `metrics.py` (Sharpe, Sortino, MAR, DD, whipsaw rate, turnover).
- Aggregate across splits; rank by robust objectives (mean-penalty*std).
- Save `CSV/Parquet` and plots to `outputs/sweeps/`.

Example YAML config (`research/config/defaults.yaml`):
```yaml
frequency: "12H"
source: ["close", "hl2", "ohlc4"]
params:
  slow: {start: 20, stop: 120, step: 5}
  fast: {start: 5,  stop: 30,  step: 1}
  bb_len: {start: 20, stop: 50, step: 5}
  bb_k: [1.5, 2.0, 2.5]
  tsv_len: {start: 10, stop: 30, step: 5}
  tsv_ema: {start: 5,  stop: 20, step: 5}
  vidya: {start: 20, stop: 60, step: 5}
cv:
  scheme: "expanding"
  splits: 4
  min_train_bars: 200
  test_bars: 200
metrics: ["sharpe", "sortino", "calmar", "whipsaw_rate", "max_dd", "hit_rate"]
rank:
  primary: "sharpe"
  penalty_std: 0.25
  regime_weighting: {trend: 0.7, range: 0.3}
```

## 9) CLI Entrypoints

- **Build features**
  ```bash
  python -m research.cli.build_features \
    --input data/BTCUSDT_12H.csv \
    --freq 12H \
    --output outputs/features/BTCUSDT_12H.parquet
  ```

- **Run parameter sweep**
  ```bash
  python -m research.cli.run_sweep \
    --features outputs/features/BTCUSDT_12H.parquet \
    --config research/config/defaults.yaml \
    --outdir outputs/sweeps/BTCUSDT_12H/
  ```

CLI options to include:
- Paths (`--input/--features/--outdir`), frequency, instrument label.
- Config override flags (e.g., `--slow 20 120 5`).
- CV scheme, number of workers (`--n-jobs` joblib), random seed.

## 10) Notebooks

- `01-explore-data.ipynb`: data profiling, quality checks, basic plots.
- `02-features-validation.ipynb`: compute and visualize features; sanity checks (e.g., ATR vs bandwidth correlation).
- `03-regime-detection.ipynb`: Hurst/ADX thresholds; label time; regime distribution.
- `04-parameter-sweeps.ipynb`: run a small grid; visualize robustness (IS/OOS, by regime).
- `05-report-and-recommend.ipynb`: summarize recommended ranges, stability, and risks.

## 11) Logging, Reproducibility, Testing

- **Logging**: `loguru` with run-specific log files in `outputs/`.
- **Seeds**: set `numpy.random.seed` and deterministic CV splits.
- **Artifacts**: version outputs by git commit hash and timestamp.
- **Unit tests** (suggest `pytest`):
  - Feature formulas (ATR, CLV, %B, Vidya ER) against known values.
  - Regime labeling stability across thresholds.
  - Sweep aggregation and ranking.

## 12) Example End-to-End Workflow

1. Load and QC data → `outputs/datasets/<symbol>_<freq>.parquet`.
2. Generate features → `outputs/features/...`.
3. Run sweeps with CV → `outputs/sweeps/...`.
4. Produce reports/plots → `outputs/reports/...`.
5. Read summary to select parameter ranges per regime; validate on a fresh holdout.

## 13) Performance Tips

- Prefer vectorized ops; avoid Python loops in feature functions.
- Cache intermediate artifacts (Parquet/Feather) and memoize expensive computations.
- Use `joblib.Parallel` and chunked grids; start with coarse sweeps, then refine around promising zones.
- Limit parameter combinations to what the PRD prescribes to control compute.

## 14) Acceptance Checklist (from PRD)

- All features derivable from OHLC-only inputs, with unit tests.
- Parameter recommendations robust (≤ 10% IS→OOS Sharpe degradation).
- Regime-aware reports generated for ≥ 3 instruments across ≥ 3 years.
- Reproducible CLI runs produce identical artifacts with same seed and config.

---

If you want, I can scaffold the `research/` package, starter modules, and a baseline `requirements.txt` now and commit them, so you can start running the first sweeps immediately.
