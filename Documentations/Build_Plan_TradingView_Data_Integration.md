# Build Plan: TradingView Data Integration (tvdatafeed)

## Overview
- Integrate TradingView OHLC retrieval using `tvdatafeed` to power:
  - Research data ingestion and caching
  - On-demand data fetch via API for the frontend charts
  - Reuse across backtesting, feature engineering, and sweeps

## Objectives
- Provide a reliable endpoint and provider for fetching normalized OHLC data by `symbol`, `exchange`, `timeframe`, `n_bars`.
- Cache datasets on disk for reuse and reproducibility.
- Return JSON OHLC for the UI, and persist parquet/CSV for research.

## Scope
- Backend Python provider wrapping `tvdatafeed`.
- Flask endpoint to request data and return normalized OHLC.
- Local caching under `outputs/datasets/tradingview/`.
- Optional: minimal rate-limiting and error handling.
- Frontend UI form to fetch & render.

Out of scope (now):
- Advanced auth workflows or secrets manager.
- Full data catalog UI.

## Dependencies
- `tvdatafeed` repo: https://github.com/rongardF/tvdatafeed
- Install via pip (preferred if available) or git:
  - `pip install tvdatafeed`
  - or `pip install "git+https://github.com/rongardF/tvdatafeed.git"`

Ensure `requirements.txt` updated accordingly.

## Configuration / Environment
- Support two auth methods via environment variables:
  - Username/password:
    - `TV_USERNAME`
    - `TV_PASSWORD`
  - Cookie-based (use with 2FA):
    - `TV_SESSION`
    - `TV_USER_ID`
- No credentials in source control.

## Directory and Files
- Provider (new): `research/data/providers/tradingview_provider.py`
- API (update): `api/server.py`
- Cache dir (new): `outputs/datasets/tradingview/`
- Optional frontend (update): `src/components/DataImportView.tsx` or new component `src/components/TVFetchPanel.tsx`

## Data Model / Normalization
- Input: DataFrame from `tvdatafeed`, typically columns [open, high, low, close, volume] and datetime index.
- Output schema (normalized):
  - Columns: `time` (ISO string), `open`, `high`, `low`, `close`, `volume`
- Persisted parquet/CSV file naming:
  - `outputs/datasets/tradingview/{exchange}_{symbol}_{timeframe}_{n_bars}.parquet`

## API Spec
- Endpoint: `GET /api/tv/ohlc`
- Query Params:
  - `symbol` (required) e.g., `BTCUSDT`
  - `exchange` (required) e.g., `BINANCE`
  - `timeframe` (default `1h`) e.g., `1`, `5`, `15`, `1h`, `4h`, `1D`, `1W`
  - `n_bars` (default `5000`)
- Response:
```json
{
  "symbol": "BTCUSDT",
  "exchange": "BINANCE",
  "timeframe": "1h",
  "count": 3000,
  "ohlc": [
    {"time": "2025-01-01T00:00:00", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 0},
    ...
  ]
}
```
- Errors: 400 for missing params; 500 with error message for fetch issues.

## Provider Implementation Outline (`tradingview_provider.py`)
- Create a factory `_tv_client()` that uses env vars for auth.
- Map timeframe strings to `Interval` enum.
- Fetch via `TvDatafeed.get_hist(...)`.
- Normalize columns and convert time to ISO string.
- Save to parquet in cache dir; read from cache if exists and `use_cache=True`.

## Caching Strategy
- Read-through cache by symbol/exchange/timeframe/n_bars.
- Optionally add TTL later; for now, manual invalidation by deleting files.

## Rate Limiting / Throttling (MVP)
- Simple per-process throttle (sleep) if rapid repeated calls.
- Future: token bucket with small burst capacity.

## Security & ToS
- Credentials only via env; never log secrets.
- Respect TradingView ToS; avoid high-frequency scraping.
- Add server-side validation and error messages for user clarity.

## Frontend Integration
- Add UI panel to request data with inputs: symbol, exchange, timeframe, n_bars.
- Call `/api/tv/ohlc` and display on `TradingChart`.
- Since API returns normalized OHLC, bypass CSV parser; just adapt `time` for chart (your pipeline supports ISO strings already).

## Implementation Steps (Tasks)
1) Dependencies & config
   - Add `tvdatafeed` to `requirements.txt` and install.
   - Document env vars in `README`/`PINE_UI_README.md`.

2) Provider module
   - Implement `research/data/providers/tradingview_provider.py` with fetch + cache + normalization.
   - Unit test on a public symbol (limited bars) guarded by `pytest -m tvdata`.

3) API route
   - Update `api/server.py`: add `GET /api/tv/ohlc` endpoint calling provider.
   - Handle errors (bad timeframe, auth, empty data) with informative messages.

4) Research ingestion
   - Add a utility to load cached parquet/CSV for backtests.
   - Example notebook/cell to demonstrate E2E from fetch → backtest.

5) Frontend
   - Add minimal UI (inputs + fetch button) and render candles via existing chart component.
   - Loading/error states.

6) Non-functional
   - Add basic rate limit and logs.
   - Add caching notes to docs.

## Mapping to Current TODOs
- tv-1: Add dependency + env vars
- tv-2: Create provider module
- tv-3: Expose Flask endpoint `/api/tv/ohlc`
- tv-4: Integrate with research ingestion (persist + loader)
- tv-5: Frontend integration to request & render
- tv-6: Caching, throttling, ToS safeguards

## Acceptance Criteria
- Backend: `/api/tv/ohlc` returns normalized OHLC JSON for valid requests; caches parquet to `outputs/datasets/tradingview/`.
- Provider: Unit test passes for at least one symbol/timeframe (skipped if no creds).
- Frontend: User can fetch and visualize a symbol from TradingView without uploading files.
- Documentation: Env vars and usage documented; error cases explained.

## Timeline (MVP ~1–2 days)
- Day 1: tv-1, tv-2, tv-3 (backend end-to-end working, cached)
- Day 2: tv-4, tv-5, tv-6 (ingestion, UI, polish)

## Testing Plan
- Unit: provider fetch with mock/timeframe map; cache read/write.
- Integration: API response shape and count; error cases.
- Manual: Frontend fetch and chart render for 1–2 symbols/timeframes.

## Rollback Plan
- Feature behind env flag; if issues, disable `/api/tv/ohlc` route and delete cache files.

## Open Questions
- Which symbols/exchanges must be supported first?
- Preferred default timeframe and bar count?
- Do we need authenticated-only mode or allow unauth attempts?
