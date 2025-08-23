# Strategy Analysis Report: Source

## Overview
- **Strategy Type**: hybrid
- **Description**: 
- **Complexity Score**: 10/10

## Indicators Analysis (93 found)

### rsi (RSI)
- **Type**: momentum
- **Purpose**: Momentum oscillator for overbought/oversold conditions
- **Parameters**: {'source': 'source', 'length': 'rsiPeriod'}
- **Inputs**: close

### sma (SMA)
- **Type**: trend
- **Purpose**: Simple moving average for trend identification
- **Parameters**: {'source': 'BBleadLine', 'length': 'BBlength'}
- **Inputs**: source

### ema (EMA)
- **Type**: trend
- **Purpose**: Exponential moving average for trend identification
- **Parameters**: {'source': 'rsiValue', 'length': 'rsiEmaPeriod'}
- **Inputs**: source

### ema_1 (EMA)
- **Type**: trend
- **Purpose**: Exponential moving average for trend identification
- **Parameters**: {'source': 'tsv', 'length': 'tsvemaperiod'}
- **Inputs**: source

### tsv (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_1 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_2 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_3 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_4 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_5 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_6 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_7 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_8 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_9 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_10 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### tsv_11 (TSV)
- **Type**: volume
- **Purpose**: Time Series Volume for trend confirmation
- **Parameters**: {}
- **Inputs**: close, volume

### source (source)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### smallcumulativePeriod (smallcumulativePeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### bigcumulativePeriod (bigcumulativePeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### meancumulativePeriod (meancumulativePeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### percentBelowToBuy (percentBelowToBuy)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### rsiPeriod (rsiPeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### rsiEmaPeriod (rsiEmaPeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### rsiLevelforBuy (rsiLevelforBuy)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### slowtenkansenPeriod (slowtenkansenPeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### slowkijunsenPeriod (slowkijunsenPeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### fasttenkansenPeriod (fasttenkansenPeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### fastkijunsenPeriod (fastkijunsenPeriod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### BBlength (BBlength)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### BBmult (BBmult)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### tsvlength (tsvlength)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### tsvemaperiod (tsvemaperiod)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### length (length)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### src (src)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### mom (mom)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### upSum (upSum)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### downSum (downSum)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cmo (cmo)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### startDate (startDate)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### startMonth (startMonth)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### startYear (startYear)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### endDate (endDate)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### endMonth (endMonth)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### endYear (endYear)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeTypicalPriceVolumeS (cumulativeTypicalPriceVolumeS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeVolumeS (cumulativeVolumeS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeTypicalPriceVolumeB (cumulativeTypicalPriceVolumeB)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeVolumeB (cumulativeVolumeB)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeTypicalPriceVolumeM (cumulativeTypicalPriceVolumeM)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeVolumeM (cumulativeVolumeM)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### rsiValue (rsiValue)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### rsiEMA (rsiEMA)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeTypicalPriceVolumeTS (cumulativeTypicalPriceVolumeTS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeVolumeTS (cumulativeVolumeTS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeTypicalPriceVolumeKS (cumulativeTypicalPriceVolumeKS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeVolumeKS (cumulativeVolumeKS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeTypicalPriceVolumeTF (cumulativeTypicalPriceVolumeTF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeVolumeTF (cumulativeVolumeTF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeTypicalPriceVolumeKF (cumulativeTypicalPriceVolumeKF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### cumulativeVolumeKF (cumulativeVolumeKF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### lowesttenkansen_s (lowesttenkansen_s)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### highesttenkansen_s (highesttenkansen_s)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### lowestkijunsen_s (lowestkijunsen_s)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### highestkijunsen_s (highestkijunsen_s)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### slowtenkansen (slowtenkansen)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### slowkijunsen (slowkijunsen)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### slowleadLine (slowleadLine)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### lowesttenkansen_f (lowesttenkansen_f)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### highesttenkansen_f (highesttenkansen_f)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### lowestkijunsen_f (lowestkijunsen_f)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### highestkijunsen_f (highestkijunsen_f)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### fasttenkansen (fasttenkansen)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### fastkijunsen (fastkijunsen)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### fastleadLine (fastleadLine)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### BBleadLine (BBleadLine)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### basis (basis)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### tsvema (tsvema)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceS (typicalPriceS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceVolumeS (typicalPriceVolumeS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceB (typicalPriceB)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceVolumeB (typicalPriceVolumeB)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceM (typicalPriceM)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceVolumeM (typicalPriceVolumeM)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### buyMA (buyMA)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceTS (typicalPriceTS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceVolumeTS (typicalPriceVolumeTS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceKS (typicalPriceKS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceVolumeKS (typicalPriceVolumeKS)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceTF (typicalPriceTF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceVolumeTF (typicalPriceVolumeTF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceKF (typicalPriceKF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### typicalPriceVolumeKF (typicalPriceVolumeKF)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

### title (title)
- **Type**: custom
- **Purpose**: Custom calculation or indicator
- **Parameters**: {}
- **Inputs**: unknown

## Parameters (24 found)
- **source**: string = title = "Source (general)
- **smallcumulativePeriod**: string = title = "Small VWAP (indicator)
- **bigcumulativePeriod**: string = title = "Big VWAP (indicator)
- **meancumulativePeriod**: string = title = "Mean VWAP (indicator)
- **percentBelowToBuy**: string = title = "Percent below to buy % (general)
- **rsiPeriod**: string = title = "Rsi Period (indicator)
- **rsiEmaPeriod**: string = title = "Rsi Ema Period (indicator)
- **rsiLevelforBuy**: string = title = "Maximum Rsi Level for Buy (general)
- **slowtenkansenPeriod**: int = 9 (indicator)
- **slowkijunsenPeriod**: int = 13 (indicator)
- **fasttenkansenPeriod**: int = 3 (indicator)
- **fastkijunsenPeriod**: int = 7 (indicator)
- **BBlength**: int = 20 (indicator)
- **BBmult**: float = 2.0 (general)
- **tsvlength**: int = 20 (indicator)
- **tsvemaperiod**: int = 7 (indicator)
- **length**: string = title="Vidya Length (indicator)
- **src**: string = title="Vidya Source (general)
- **startDate**: string = title="Start Date (general)
- **startMonth**: string = title="Start Month (general)
- **startYear**: string = title="Start Year (general)
- **endDate**: string = title="End Date (general)
- **endMonth**: string = title="End Month (general)
- **endYear**: string = title="End Year (general)

## Logic Flow
- **Type**: trend_following
- **Entry Conditions**: 0
- **Exit Conditions**: 0
- **Complexity**: 10/10

## Data Requirements
close, source, unknown, volume

## Conversion Challenges
- Multiple custom indicators (77)

## Timeframe Compatibility
5m, 15m, 1h, 4h

---
*Analysis completed at 2025-08-22T16:19:18.712316*