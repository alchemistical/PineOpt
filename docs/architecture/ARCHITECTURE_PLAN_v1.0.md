# 📋 PineOpt Research Lab: Building Plan & Milestones
**Version: 1.0**  
**Date: August 21, 2025**  
**Status: Master Architecture Plan**

Based on the PRD and Python Research Skeleton Guide, here's the comprehensive building plan:

## 🎯 **Project Overview**
Build a research lab that:
- Derives robust features from OHLC-only data
- Performs parameter sweeps for trading strategies (VWAP-Ichimoku, Bollinger, TSV proxy, Vidya)
- Provides regime-aware validation and backtesting
- Delivers actionable parameter ranges for production strategies

---

## 🏗️ **Phase 1: Foundation & Infrastructure (Week 1)**

### **Milestone 1.1: Environment Setup**
- [ ] Create Python virtual environment (`pineopt`)
- [ ] Install core dependencies (pandas, numpy, scipy, sklearn)
- [ ] Install technical analysis tools (ta library, statsmodels)
- [ ] Install backtesting frameworks (vectorbt, quantstats)
- [ ] Set up dev tools (pytest, black, ruff, jupyterlab)

### **Milestone 1.2: Project Structure**
- [ ] Create `research/` package with modular structure:
  - `config/` - YAML configurations
  - `data/` - loaders and quality checks
  - `features/` - feature engineering modules
  - `regimes/` - regime detection
  - `backtest/` - backtesting runners
  - `sweeps/` - parameter sweep engine
  - `cli/` - command line interfaces
  - `notebooks/` - Jupyter analysis notebooks

### **Milestone 1.3: Data Pipeline**
- [ ] Build OHLC data loader (`research/data/loaders.py`)
- [ ] Implement quality checks (`research/data/quality.py`):
  - Timestamp monotonicity validation
  - Price sanity checks (high ≥ max(open,close), etc.)
  - Gap detection and handling
- [ ] Create data resampling utilities
- [ ] Test with existing Excel OHLC data

---

## 🔧 **Phase 2: Feature Engineering Library (Week 2)**

### **Milestone 2.1: Core Features**
- [ ] `research/features/core.py`:
  - Returns & log returns (1,2,4,8,12,24 periods)
  - Realized volatility (rolling std over 10-60 bars)
  - True Range and ATR calculations
  - Close Location Value (CLV) for range positioning

### **Milestone 2.2: VWAP Proxies**
- [ ] `research/features/proxies.py`:
  - OHLC4 = (O+H+L+C)/4
  - HL2 = (H+L)/2  
  - HLC3 = (H+L+C)/3
  - Rolling EMA of proxies as VWAP analogs

### **Milestone 2.3: Ichimoku Components**
- [ ] `research/features/ichimoku.py`:
  - Tenkan/Kijun via rolling medians of high/low midpoints
  - Fast (5-30 bars) and slow (20-120 bars) components
  - Trend bias indicators

### **Milestone 2.4: Bollinger Bands & Indicators**
- [ ] `research/features/bollinger.py`:
  - Bollinger Bands (length: 20-50, stdDev: 1.5-2.5)
  - %B (position within bands)
  - Bandwidth (band width relative to center)
- [ ] `research/features/tsv.py`:
  - TSV proxy using CLV + EMA smoothing
  - Length: 10-30 bars, EMA: 5-20 bars
- [ ] `research/features/vidya.py`:
  - Variable Index Dynamic Average
  - Efficiency ratio calculation
  - Adaptive smoothing (20-60 bars)

### **Milestone 2.5: Derived Features**
- [ ] `research/features/utils.py`:
  - MA slopes and curvature
  - Z-scores and standardization
  - Efficiency ratios
- [ ] Unit tests for all feature calculations

---

## 📊 **Phase 3: Regime Detection & Classification (Week 3)**

### **Milestone 3.1: Regime Detection Methods**
- [ ] `research/regimes/hurst.py`:
  - Hurst exponent calculation (rolling window ~200)
  - Trending: H > 0.55, Ranging: H < 0.45
- [ ] `research/regimes/adx.py`:
  - ADX-based regime classification
  - Trending: ADX > threshold_high, Ranging: ADX < threshold_low
- [ ] `research/regimes/classify.py`:
  - Combine multiple regime signals
  - Configurable thresholds per instrument

### **Milestone 3.2: Parameter Sweep Engine**
- [ ] `research/sweeps/engine.py`:
  - Parameter grid expansion
  - Time-series cross-validation (expanding window)
  - Multi-processing support for parallel sweeps
- [ ] `research/sweeps/metrics.py`:
  - Sharpe, Sortino, Calmar ratios
  - Max drawdown, hit rate, turnover
  - Whipsaw rate calculation
- [ ] YAML configuration system for sweep parameters

---

## 🔄 **Phase 4: Backtesting & Validation (Week 4)**

### **Milestone 4.1: Backtesting Framework**
- [ ] `research/backtest/vectorbt_runner.py`:
  - Fast vectorized backtesting
  - Strategy signal generation from features
  - Portfolio metrics calculation
- [ ] Optional: `research/backtest/zipline_runner.py`:
  - Event-driven validation
  - Realistic slippage/commission modeling

### **Milestone 4.2: Cross-Validation System**
- [ ] Expanding window validation
- [ ] K-fold time-series splits
- [ ] In-sample vs out-of-sample robustness testing
- [ ] Regime-aware validation splits

### **Milestone 4.3: Parameter Optimization**
- [ ] Grid search implementation
- [ ] Parameter ranges per strategy:
  - Slow VWAP: 20-120 bars
  - Fast VWAP: 5-30 bars  
  - Bollinger: length 20-50, stdDev 1.5-2.5
  - TSV: length 10-30, EMA 5-20
  - Vidya: length 20-60, multiple sources

---

## 📈 **Phase 5: Reporting & Analysis (Week 5)**

### **Milestone 5.1: Analysis Notebooks**
- [ ] `01-explore-data.ipynb`: Data profiling and quality checks
- [ ] `02-features-validation.ipynb`: Feature computation and validation
- [ ] `03-regime-detection.ipynb`: Regime classification analysis
- [ ] `04-parameter-sweeps.ipynb`: Parameter optimization results
- [ ] `05-report-and-recommend.ipynb`: Final recommendations

### **Milestone 5.2: Reporting System**
- [ ] `research/sweeps/reporting.py`:
  - Automated report generation
  - Correlation heatmaps and PCA analysis
  - Feature importance summaries
  - Parameter stability analysis
- [ ] QuantStats integration for tearsheets
- [ ] HTML and PDF report outputs

### **Milestone 5.3: CLI Tools**
- [ ] `research/cli/build_features.py`: Feature generation CLI
- [ ] `research/cli/run_sweep.py`: Parameter sweep CLI
- [ ] Reproducible workflow scripts
- [ ] Configuration validation and defaults

---

## 🎯 **Phase 6: Integration & Production Ready (Week 6)**

### **Milestone 6.1: Dashboard Integration**
- [ ] Connect Python research backend to React dashboard
- [ ] API endpoints for feature visualization
- [ ] Real-time parameter recommendation display
- [ ] Strategy performance comparison charts

### **Milestone 6.2: Validation & Testing**
- [ ] Test on multiple instruments (≥3 instruments, ≥3 years data)
- [ ] Validate robustness criteria (≤10% IS/OOS Sharpe degradation)
- [ ] Performance benchmarking (runtime targets)
- [ ] Documentation and user guides

### **Milestone 6.3: Deliverables**
- [ ] Complete feature library with unit tests
- [ ] Parameter sweep reports with recommendations
- [ ] Regime-aware backtest results
- [ ] Reproducible CLI workflows
- [ ] Integration with existing OHLC dashboard

---

## 📊 **Success Metrics & KPIs**

### **Technical Metrics:**
- ✅ All features derivable from OHLC-only data
- ✅ Parameter recommendations with <10% IS/OOS degradation
- ✅ Regime detection validated across time periods
- ✅ Runtime performance targets met

### **Research Metrics:**
- ✅ Whipsaw rate reduction ≥Y% vs baseline
- ✅ Trend capture improvement ≥Z% vs baseline  
- ✅ Robust parameter ranges across instruments
- ✅ Noise reduction via feature selection

---

## 🚀 **Implementation Timeline**

### **Current Status: Phase 0 Complete ✅**
- [x] React OHLC Dashboard with working chart visualization
- [x] CSV/Excel data import functionality  
- [x] Basic chart controls (zoom, candlesticks/line toggle)
- [x] Clean codebase with production-ready frontend

### **Next Steps Prioritization:**

#### **Week 1 (Immediate)**
1. **Day 1-2**: Set up Python environment and project structure
2. **Day 3-4**: Implement data pipeline and quality checks
3. **Day 5-7**: Test data loading with existing Excel OHLC file

#### **Week 2 (Feature Engineering)**
1. **Day 1-3**: Build core features (returns, volatility, ATR, CLV)
2. **Day 4-5**: Implement VWAP proxies and Ichimoku components
3. **Day 6-7**: Add Bollinger, TSV, Vidya indicators with unit tests

#### **Week 3 (Regime Detection)**
1. **Day 1-3**: Implement Hurst and ADX-based regime detection
2. **Day 4-5**: Build parameter sweep engine framework
3. **Day 6-7**: Create metrics calculation and YAML configuration

#### **Week 4 (Backtesting)**
1. **Day 1-4**: Implement vectorbt backtesting framework
2. **Day 5-6**: Build cross-validation and parameter optimization
3. **Day 7**: Integration testing and performance validation

#### **Week 5 (Analysis & Reporting)**
1. **Day 1-3**: Create analysis notebooks (01-05)
2. **Day 4-5**: Build automated reporting system
3. **Day 6-7**: CLI tools and workflow scripts

#### **Week 6 (Integration)**
1. **Day 1-3**: Connect Python backend to React dashboard
2. **Day 4-5**: Multi-instrument validation and testing
3. **Day 6-7**: Documentation and final deliverables

---

## 🏗️ **Technical Architecture**

### **Current Stack:**
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Data Visualization**: Custom SVG charts with zoom/pan controls
- **Data Processing**: CSV/Excel parsing with XLSX and PapaParse

### **Planned Python Stack:**
- **Core**: pandas, numpy, scipy, scikit-learn
- **Technical Analysis**: ta library, custom implementations
- **Backtesting**: vectorbt (fast), zipline-reloaded (robust)
- **Statistics**: statsmodels, empyrical-reloaded, quantstats
- **Optimization**: cvxpy, joblib (parallel processing)
- **Visualization**: matplotlib, seaborn, plotly (for notebooks)

### **Integration Points:**
1. **Data Bridge**: Python CLI → JSON/Parquet → React dashboard
2. **API Layer**: FastAPI/Flask for real-time parameter recommendations
3. **File System**: Shared outputs/ directory for results exchange
4. **Configuration**: YAML configs shared between Python and React

---

## 📝 **Key Design Decisions**

### **1. OHLC-Only Approach**
- No volume dependency ensures broad applicability
- Volume proxies (CLV, TSV) provide participation estimates
- Focus on price action and technical patterns

### **2. Regime-Aware Validation**
- Separate parameter optimization for trending vs ranging markets
- Hurst exponent + ADX for robust regime classification
- Cross-validation respects regime boundaries

### **3. Feature Selection Strategy**
- Role-based partitioning (trend bias, timing, noise filter, exit signals)
- PCA and correlation analysis to reduce redundancy
- Statistical significance testing across regimes

### **4. Modular Architecture**
- Separate concerns: data → features → regimes → backtest → reports
- CLI-driven workflows for reproducibility
- Notebook-based analysis for exploration

---

## 🔄 **Version History**

### **v1.0 (August 21, 2025)**
- Initial architecture plan based on PRD and Python Research Skeleton
- Complete 6-phase implementation roadmap
- Technical specifications and success metrics
- Integration plan with existing React dashboard

### **Future Versions**
- v1.1: Refinements based on Phase 1 implementation learnings
- v1.2: Performance optimizations and additional features
- v2.0: Production deployment and scaling considerations

---

## 📞 **Reference Documents**
1. `Documentations/PRD_OHLC_Feature_Engineering_and_Strategy_Param_Ranges.md`
2. `Documentations/Python_Research_Skeleton_Guide.md`
3. Current React dashboard implementation in `src/`

---

**This document serves as the master reference for the PineOpt Research Lab implementation. All development decisions should align with this architecture plan.**