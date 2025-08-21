# PRD: Pine Script Strategy → Python Converter Module

## 1) Overview / Scope
Build a module to ingest Pine Script (v5-preferred) strategy/indicator files and generate equivalent, runnable Python that integrates with the research skeleton. The output should:
- Recreate logic (signals, entries/exits, core indicators) on OHLC data without repaint.
- Expose inputs defined via `input*()` as Python parameters for sweeps.
- Integrate with backtesting runners (e.g., vectorbt) and the feature library when applicable.

## 2) Goals
- Cover a practical Pine v5 subset (see §6) used in common strategies.
- Deterministic series semantics using pandas/NumPy; explicit handling of `x[1]`, `var`, `varip`.
- Clean, readable Python codegen with a thin runtime adapter for Pine idioms (`nz`, `na`, `ta.*`).
- CLI to convert .pine → .py and optionally execute a quick backtest.

## 3) Non-Goals (Phase 1)
- Full Pine language parity; complex plotting APIs.
- Multi-timeframe `request.security()` and multi-symbol strategies.
- Broker-specific features and live-trading integration.

## 4) Users / Stakeholders
- Quant researchers porting TradingView strategies for robust, regime-aware evaluation.
- Strategy engineers integrating converted modules into automated sweeps.

## 5) Functional Requirements
- Parse Pine v5 source and build an AST.
- Semantic analysis: infer series vs scalar, lifetimes, stateful vars (`var`, `varip`).
- Intermediate Representation (IR) normalizing Pine constructs.
- Mapper from IR to Python vector ops and runtime adapters.
- Code generation producing a Python module that exposes:
  - PARAMS metadata (defaults/ranges inferred from `input*`).
  - `build_signals(df: pd.DataFrame, **params)` returning entry/exit signals (+ optional stops/targets).
  - Optional `build_features(df, **params)` when indicators are reusable.
- CLI commands: convert, validate, run (quick backtest against CSV/Parquet).

## 6) Initial Pine v5 Subset Coverage
- Declarations: `indicator`, `strategy`, `//@version=5`, `input`, `input.int`, `input.float`, `input.bool`, `input.string`.
- Types: bool/int/float/string; series<T> vs T; `color` ignored.
- Vars: `var`, `varip`, default assignment, `:=` reassignment.
- Indexing & history: `x[1]`, `bar_index`, `na`, `nz`, `change`, `ta.change`.
- Math/logical ops; ternary `cond ? a : b`.
- Time series ops/indicators (runtime adapter): `ta.sma`, `ta.ema`, `ta.rsi`, `ta.stdev`, `ta.atr`, `ta.highest`, `ta.lowest`, `ta.crossover`, `ta.crossunder`, `ta.cross`.
- Strategy API: `strategy.entry`, `strategy.exit`, `strategy.close` (mapped to boolean signals; qty and stop/limit optional fields captured if present).
- Plot/shape functions ignored with warnings.
- `request.security` deferred with explicit error/warning.

## 7) Architecture & Flow
1) Parsing
- Use a formal grammar to produce AST.
  - Option A: ANTLR4 Pine grammar (community) → Python target.
  - Option B: Tree-sitter Pine grammar via Python bindings.
  - Option C: Pragmatic parser for the supported subset (faster to MVP).

2) AST → IR
- Normalize nodes (assignments, calls, conditionals, loops).
- Type annotate series vs scalar; lift `input*` into a param schema.
- Model `var`/`varip` as state with proper initialization semantics.

3) IR → Mapping
- Map Pine ops to pandas/NumPy:
  - `x[1]` → `x.shift(1)`
  - `nz(x, v)` → `x.fillna(v)`
  - `na(x)` → `x.isna()`
  - `crossover(a,b)` → `(a > b) & (a.shift(1) <= b.shift(1))`
- Map `ta.*` to adapter implementations.

4) Code Generation
- Emit structured Python:
  - Header imports, `PARAMS`, helper adapters from runtime.
  - `build_signals(df, **params)` computing Series[bool] for entries/exits.
  - Optional stops/targets Series if strategy used `strategy.exit` args.

5) Validation
- Static checks: subset usage, forbidden features, unbound variables.
- Dynamic checks: run over sample OHLC, ensure no runtime errors, outputs align with expectations.
- Optional golden tests: compare against expected signals from a reference CSV.

## 8) Module Skeleton

```
pine2py/
  __init__.py
  config/
    __init__.py
    defaults.yaml
  grammar/
    pine_v5.g4                # if ANTLR used
  parser/
    __init__.py
    lexer.py                  # generated or custom
    parser.py                 # generated or custom
    builder.py                # AST builder utilities
  ir/
    __init__.py
    nodes.py                  # IR node types
    typer.py                  # series/scalar inference
    normalize.py              # desugar/reshape AST
  mapper/
    __init__.py
    pine_to_py.py             # IR → Python mapping rules
  runtime/
    __init__.py
    series.py                 # nz, na, change, crossover, etc.
    ta_adapters.py            # sma, ema, rsi, atr, stdev, highest/lowest
  codegen/
    __init__.py
    emit.py                   # write Python module from IR mapping
  validate/
    __init__.py
    static.py                 # static checks
    dynamic.py                # sample data run, smoke tests
  cli/
    __init__.py
    convert.py                # pine → py
    run.py                    # run quick backtest on converted module
  tests/
    data/
      sample_ohlc.csv
    test_smoke.py
    test_ta_adapters.py
    test_mapping_signals.py
examples/
  rsi_strategy.pine
  supertrend_like.pine
  converted/
    rsi_strategy.py
```

## 9) CLI UX
- Convert only:
  ```bash
  python -m pine2py.cli.convert \
    --input examples/rsi_strategy.pine \
    --output examples/converted/rsi_strategy.py
  ```
- Convert + run quick test:
  ```bash
  python -m pine2py.cli.convert \
    --input examples/rsi_strategy.pine \
    --output examples/converted/rsi_strategy.py \
    --run --data tests/data/sample_ohlc.csv --freq 12H
  ```
- Run converted module directly:
  ```bash
  python -m pine2py.cli.run \
    --module examples/converted/rsi_strategy.py \
    --data tests/data/sample_ohlc.csv --freq 12H
  ```

## 10) Integration with Research Skeleton
- Generated module should expose `PARAMS` and `build_signals(df, **params)` so it can plug into:
  - `research/backtest/vectorbt_runner.py` as a strategy constructor.
  - `research/sweeps/engine.py` to sweep `PARAMS` ranges.
- Optionally emit a `build_features` that reuses our feature library where mappings are direct.

## 11) Acceptance Criteria
- Can convert and run at least 3 real Pine v5 strategies using only the supported subset.
- `PARAMS` inferred from `input*` and usable by sweeps.
- Deterministic signals (no repaint) on fixed datasets; unit tests pass.
- Clear warnings for unsupported constructs; graceful failure with actionable messages.

## 12) Milestones & Timeline
- M1 (Week 1): Subset grammar + AST; runtime adapters (sma/ema/rsi/atr/stdev/highest/lowest/cross).
- M2 (Week 2): IR + mapping + codegen for assignments/if/ternary/indexing; CLI convert.
- M3 (Week 3): Strategy API mapping (entry/exit/close) + validate; tests + examples.
- M4 (Week 4): Research skeleton integration + sweep on a converted strategy; docs.
- Optional M5: Tree-sitter/ANTLR hardening; partial `request.security` support.

## 13) Risks & Mitigations
- Language drift / corner cases → restrict to explicit subset, strong validator, example-based tests.
- Stateful semantics (`var`, `varip`) → model as Series with proper init; add fixtures covering edge cases.
- Indicator mismatch vs TradingView → verify formulas, offer compatibility modes where needed.
- MFT (`request.security`) → defer; provide stub with explicit error.

## 14) Documentation
- Developer guide: architecture, subset, mapping tables, adding new adapters.
- User guide: how to convert, run, and integrate with research sweeps.
- Examples: Pine files and their generated Python counterparts.
