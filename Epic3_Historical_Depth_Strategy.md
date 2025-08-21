# Epic 3: Historical Depth Maximization Strategy

## Revised Focus: Maximum Historical Data Collection

**Goal**: Collect the deepest possible historical dataset for all Binance USDT pairs, optimized for crypto strategy lab backtesting.

## Binance API Historical Data Limits

### Klines Endpoint Limits:
- **Max bars per request**: 1,000 bars
- **Max historical depth**: Varies by timeframe
- **Rate limits**: 1,200 requests/minute, 5,000 requests/10 minutes
- **No authentication required** for historical data

### Historical Depth by Timeframe:
```
1m:  ~2 years max (limited by storage/performance)
5m:  ~3 years max  
15m: ~4 years max
30m: ~4 years max
1h:  ~4 years max (most reliable)
4h:  ~4 years max
1d:  ~5+ years max (longest history)
1w:  ~5+ years max
1M:  ~5+ years max
```

## Revised Collection Strategy

### Phase 1: Maximum Depth Collection (Priority Focus)
**Target**: Get the deepest possible historical data for each timeframe

1. **Daily Data (1d)**: 5+ years for all USDT pairs
2. **Hourly Data (1h)**: 4 years for all USDT pairs  
3. **4-Hour Data (4h)**: 4 years for all USDT pairs
4. **Weekly Data (1w)**: 5+ years for all USDT pairs

### Phase 2: Medium-Term Granular Data
**Target**: 2-3 years of higher frequency data

5. **30-Minute Data (30m)**: 2 years for top pairs
6. **15-Minute Data (15m)**: 2 years for top pairs

### Phase 3: Short-Term Granular Data (Optional)
**Target**: 1 year of very high frequency data

7. **5-Minute Data (5m)**: 1 year for BTC/ETH only
8. **1-Minute Data (1m)**: 6 months for BTC/ETH only

## Target USDT Pairs (Expanded)
**Top Tier (Priority 1)**:
- BTCUSDT, ETHUSDT

**Major Tier (Priority 2)**:  
- BNBUSDT, ADAUSDT, SOLUSDT, XRPUSDT, DOTUSDT

**Popular Tier (Priority 3)**:
- DOGEUSDT, AVAXUSDT, MATICUSDT, LINKUSDT, LTCUSDT

**Total**: 12 USDT pairs × 4 core timeframes = 48 comprehensive datasets

## Storage Optimization
- **Estimated Volume**: 50,000-100,000+ OHLC records
- **High-Precision Storage**: DECIMAL(30,15) for accurate backtesting
- **Indexed Queries**: Optimized for pandas/backtrader access
- **No Real-time Updates**: Static historical dataset

## Success Metrics
- ✅ Maximum historical depth achieved for each timeframe
- ✅ Complete 4-year dataset for major pairs (1h, 4h, 1d, 1w)
- ✅ 48+ comprehensive datasets covering crypto market
- ✅ Ready for extensive backtesting and strategy development

## Benefits of This Approach
1. **Deep Historical Context**: 4-5 years captures multiple market cycles
2. **No Complexity**: Static data, no live streaming infrastructure  
3. **Research Ready**: Comprehensive dataset for academic-level analysis
4. **Strategy Lab Optimized**: Perfect for Pine2Py conversion testing