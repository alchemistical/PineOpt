# PineOpt API - Epic 7: API Architecture Rationalization

**Version:** 1.0.0  
**Generated:** 2025-08-23 15:21:42


# PineOpt API Documentation

**Epic 7: API Architecture Rationalization** - Complete API reference for the consolidated PineOpt trading strategy platform.

## Features
- **Consolidated Architecture**: 5 unified blueprints replacing 13+ scattered route files
- **Production Middleware**: Rate limiting, error handling, logging, and CORS
- **Standardized Responses**: Consistent JSON format across all endpoints
- **Health Monitoring**: Comprehensive service health checks
- **Strategy Management**: Pine Script conversion and backtesting

## Architecture Overview
This API follows a microservice-inspired blueprint architecture with production-ready middleware:
- **Health Services**: System monitoring and status
- **Market Data Services**: Real-time and historical market data
- **Strategy Services**: Strategy CRUD operations and validation
- **Conversion Services**: Pine Script to Python conversion
- **Backtesting Services**: Strategy performance analysis

## Authentication
Currently in development mode. Production authentication will be added in future sprints.

## Rate Limiting
- **Global Limits**: 100 requests/minute, 2000 requests/hour per client
- **Headers**: Rate limit info included in response headers
- **Bypass**: Health check endpoints excluded from rate limiting

## Error Handling
All errors return standardized JSON format with:
- **Timestamp**: ISO 8601 timestamp
- **Error Type**: Categorized error type
- **Request Info**: Method, path, and endpoint context
- **Epic Context**: Epic 7 project identification
            

## 🌐 Servers

- **Development Server**: `http://localhost:5007`
- **Production Server**: `https://api.pineopt.dev`
- **Staging Server**: `https://staging-api.pineopt.dev`

## 📡 API Endpoints

### Health

System health monitoring and status endpoints

#### `GET` /api/v1/health/

**Summary:** Basic health check

Returns basic service health status

**Responses:**
- `200`: Service is healthy

#### `GET` /api/v1/health/detailed

**Summary:** Detailed health check

Returns detailed system health metrics including CPU, memory, and database status

**Responses:**
- `200`: 
- `500`: 

#### `GET` /api/v1/health/metrics

**Summary:** Performance metrics

Returns API performance metrics (placeholder - will be implemented in Sprint 3)

**Responses:**
- `200`: 

---

### Market Data

Real-time and historical market data services

#### `GET` /api/v1/market/

**Summary:** Market data API information

Returns available market data endpoints and capabilities

**Responses:**
- `200`: 

---

### Strategies

Strategy management, validation, and CRUD operations

#### `GET` /api/v1/strategies/

**Summary:** Strategy management API information

Returns available strategy management endpoints

**Responses:**
- `200`: 

#### `GET` /api/v1/strategies/list

**Summary:** List all strategies

Returns paginated list of all strategies

**Responses:**
- `200`: 

#### `GET` /api/v1/strategies/{id}

**Summary:** Get strategy by ID

Returns detailed strategy information

**Responses:**
- `200`: 
- `404`: 

#### `PUT` /api/v1/strategies/{id}

**Summary:** Update strategy

Updates an existing strategy

**Responses:**
- `200`: 
- `400`: 
- `404`: 
- `422`: 

#### `DELETE` /api/v1/strategies/{id}

**Summary:** Delete strategy

Deletes a strategy by ID

**Responses:**
- `200`: 
- `404`: 

---

### Conversions

Pine Script to Python conversion services

#### `GET` /api/v1/conversions/

**Summary:** Conversion API information

Returns available Pine Script conversion endpoints and capabilities

**Responses:**
- `200`: 

#### `GET` /api/v1/conversions/health

**Summary:** Conversion service health

Returns health status of conversion services

**Responses:**
- `200`: 

#### `POST` /api/v1/conversions/analyze

**Summary:** Analyze Pine Script strategy

Analyzes Pine Script code and provides insights

**Responses:**
- `200`: 
- `400`: 
- `422`: 
- `503`: AI analysis service unavailable

#### `POST` /api/v1/conversions/convert/working

**Summary:** Convert Pine Script (working converter)

Converts Pine Script to Python using the working converter

**Responses:**
- `200`: 
- `400`: 
- `503`: Conversion service unavailable

#### `GET` /api/v1/conversions/indicators

**Summary:** List available indicators

Returns list of supported technical indicators for conversion

**Responses:**
- `200`: 

---

### Backtests

Strategy backtesting and performance analysis

#### `GET` /api/v1/backtests/

**Summary:** Backtest API information

Returns available backtesting endpoints and capabilities

**Responses:**
- `200`: 

#### `GET` /api/v1/backtests/health

**Summary:** Backtest service health

Returns health status of backtesting services

**Responses:**
- `200`: 

#### `POST` /api/v1/backtests/run

**Summary:** Run strategy backtest

Executes backtest for a given strategy

**Responses:**
- `200`: Backtest results
- `404`: Strategy not found
- `422`: 

#### `GET` /api/v1/backtests/pairs/available

**Summary:** List available trading pairs

Returns list of available trading pairs for backtesting

**Responses:**
- `200`: 

#### `GET` /api/v1/backtests/history

**Summary:** Backtest history

Returns history of previous backtests

**Responses:**
- `200`: 

---

### Middleware

Rate limiting, logging, and CORS configuration endpoints

#### `GET` /api/v1/rate-limit/status

**Summary:** Rate limit status

Returns current rate limiting status for the client

**Responses:**
- `200`: 

#### `GET` /api/v1/cors/config

**Summary:** CORS configuration

Returns current CORS configuration

**Responses:**
- `200`: 

#### `GET` /api/v1/cors/test

**Summary:** CORS functionality test

Test endpoint for CORS functionality validation

**Responses:**
- `200`: 

#### `GET` /api/v1/logs/config

**Summary:** Logging configuration

Returns current logging middleware configuration

**Responses:**
- `200`: 

---


## 📝 Additional Information

### Rate Limiting
- **Global Limits**: 100 requests/minute, 2000 requests/hour per client
- **Headers**: Rate limit info included in response headers
- **Bypass**: Health check endpoints excluded from rate limiting

### Error Handling
All errors return standardized JSON format with:
- **Timestamp**: ISO 8601 timestamp
- **Error Type**: Categorized error type  
- **Request Info**: Method, path, and endpoint context
- **Epic Context**: Epic 7 project identification

### Authentication
Currently in development mode. Production authentication will be added in future sprints.

---
*Generated by Epic 7 Sprint 3 Documentation Generator*
