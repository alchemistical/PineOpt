# PineOpt - Crypto Strategy Lab (Current State)

## 🎯 **What This Application Actually Is:**
A **crypto-focused Pine script conversion platform** that transforms TradingView Pine Script strategies into executable Python code using **real live crypto market data**.

## 🚀 **Core Features (Working):**

### **1. Live Crypto Data Integration**
- **Primary**: Binance public API (real-time OHLC data)
- **Fallback**: Tardis.dev with realistic demo data
- **Symbols**: BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, etc.
- **Exchanges**: BINANCE, COINBASE, KRAKEN, BITSTAMP, BYBIT, BITFINEX
- **Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d
- **Data Quality**: Professional-grade OHLC with volume

### **2. Pine Script to Python Conversion**
- **Input**: TradingView Pine Script strategies
- **Output**: Executable Python backtesting code
- **Focus**: RSI, moving averages, crypto-specific indicators
- **Storage**: SQLite database for converted strategies

### **3. Interactive Crypto Charts**
- **Real-time visualization** of crypto price data
- **OHLC candlestick charts** using lightweight-charts
- **Live price updates** from Binance
- **Multi-timeframe analysis**

### **4. Strategy Management**
- **Save/Load** converted Pine strategies
- **Metadata storage** (creation date, description, etc.)
- **Strategy library** for crypto algorithms

## 🎨 **User Interface Sections:**

### **1. Overview Dashboard**
- Feature cards showing platform capabilities
- System status indicators
- Recent activity summary

### **2. Crypto Data Fetching** (Currently "Data Import")
- **Primary**: Live crypto data from Binance
- **Secondary**: File upload for historical data
- Real-time crypto price charts

### **3. Pine Script Converter** 
- Pine Script input editor
- Python code output generator
- Strategy parameter configuration

### **4. Strategy Library**
- Converted strategy management
- Strategy metadata and descriptions

## 🔧 **Technical Architecture:**

### **Backend (Python/Flask)**
- **API Server**: Port 5005
- **Data Providers**: 
  - `binance_provider.py` (primary - live data)
  - `tardis_provider.py` (fallback - demo data)
- **Database**: SQLite for strategy storage
- **Conversion Engine**: Pine2Py parser and code generator

### **Frontend (React/TypeScript)**
- **Dev Server**: Port 3001
- **UI Framework**: React + Tailwind CSS
- **Charts**: lightweight-charts library
- **Design**: Glass morphism with crypto-themed gradients

## 🎯 **Target Users:**
- **Crypto traders** wanting to convert TradingView strategies
- **Python developers** building crypto trading bots
- **Strategy developers** testing Pine Script algorithms with real crypto data

## 📊 **Current Capabilities:**
- ✅ Fetch real BTC price (~$112K current)
- ✅ Display live ETH, SOL, ADA prices
- ✅ Convert Pine Script RSI strategies
- ✅ Generate Python backtesting code
- ✅ Store converted strategies
- ✅ Real-time crypto charts

## 🚫 **What This Is NOT:**
- Not a general trading platform
- Not for stock/forex data (crypto-only)
- Not for live trading execution
- Not a TradingView replacement

## 🎨 **Brand Identity:**
- **Name**: PineOpt
- **Focus**: Crypto Strategy Optimization
- **Theme**: Professional crypto lab interface
- **Colors**: Blue/purple gradients with crypto accent colors

---

*Updated: August 21, 2025*
*Real crypto data powered by Binance API*