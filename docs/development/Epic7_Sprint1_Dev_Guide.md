# Epic 7 Sprint 1 - Developer Getting Started Guide

**Sprint Goal**: Foundation & Consolidation  
**Timeline**: Week 1 of Epic 7  
**Branch**: `epic-7-api-rationalization`  
**Status**: ✅ Ready for Development  

---

## 🎯 **Sprint 1 Objectives**

**Primary Goals:**
1. **Establish API Foundation** - Flask application factory pattern
2. **Consolidate Market Data Routes** - Merge 3 route files into 1 blueprint
3. **Consolidate Strategy Routes** - Merge 2 route files into 1 blueprint
4. **Basic Middleware Framework** - Foundation for Sprint 2

**Success Criteria:**
- All market data endpoints under `/api/v1/market/`
- All strategy endpoints under `/api/v1/strategies/`
- Health check endpoints functional
- No breaking changes to existing functionality
- All tests pass

---

## 🚀 **Quick Start**

### **1. Development Environment Setup**

```bash
# Switch to Epic 7 branch
git checkout epic-7-api-rationalization

# Verify you're in the right place
pwd  # Should show /Users/[username]/Projects/PineOpt
git branch  # Should show * epic-7-api-rationalization

# Install any missing dependencies
cd backend && pip install -r ../requirements_enhanced.txt

# Test the new API foundation
python api/app.py
```

### **2. Verify Setup**

When you run `python api/app.py`, you should see:
```
🚀 PineOpt API Server Starting
Epic 7: API Architecture Rationalization
    
Server Info:
  • Environment: DevelopmentConfig
  • Port: 5007
  • Debug: True
  • Database: sqlite:///backend/database/pineopt_unified.db
  
API Endpoints:
  • Health Check: http://localhost:5007/api/health
  • API Info: http://localhost:5007/api
```

### **3. Test Basic Endpoints**

```bash
# Test health check
curl http://localhost:5007/api/health

# Test API info
curl http://localhost:5007/api

# Test market data (placeholder)
curl http://localhost:5007/api/v1/market/

# Test strategies (placeholder) 
curl http://localhost:5007/api/v1/strategies/
```

---

## 📋 **Sprint 1 Development Tasks**

### **📦 Task 1: Complete Blueprint Registration** (Priority: HIGH)

**File**: `backend/api/app.py`

```python
# TODO: Uncomment and implement in register_blueprints()
def register_blueprints(app):
    from .routes.health import health_bp
    from .routes.market_data import market_bp  
    from .routes.strategies import strategy_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(strategy_bp)
```

**Acceptance Criteria:**
- [ ] Health endpoints accessible at `/api/v1/health/`
- [ ] Market endpoints accessible at `/api/v1/market/`
- [ ] Strategy endpoints accessible at `/api/v1/strategies/`

### **📊 Task 2: Complete Market Data Consolidation** (Priority: HIGH)

**File**: `backend/api/routes/market_data.py`

**Sub-tasks:**
- [ ] Review `backend/api/market_routes.py` for missing functionality
- [ ] Review `backend/api/futures_routes.py` for missing functionality
- [ ] Review `backend/api/enhanced_data_routes.py` for missing functionality
- [ ] Implement missing endpoints in consolidated blueprint
- [ ] Add proper error handling
- [ ] Add input validation

**Key Endpoints to Validate:**
- `GET /api/v1/market/overview` - Market overview with gainers/losers
- `GET /api/v1/market/symbols` - Available trading symbols  
- `GET /api/v1/market/tickers` - Real-time market tickers
- `GET /api/v1/market/ohlc/<symbol>` - OHLC data for symbol
- `GET /api/v1/market/futures/pairs` - Futures trading pairs

### **🧠 Task 3: Complete Strategy Consolidation** (Priority: HIGH)

**File**: `backend/api/routes/strategies.py`

**Sub-tasks:**
- [ ] Review `backend/api/strategy_routes.py` for missing functionality
- [ ] Review `backend/api/parameter_routes.py` for missing functionality
- [ ] Implement complete CRUD operations
- [ ] Add strategy parameter management
- [ ] Add input validation
- [ ] Add Pine Script validation

**Key Endpoints to Validate:**
- `GET /api/v1/strategies` - List strategies with filtering
- `POST /api/v1/strategies` - Create new strategy
- `GET /api/v1/strategies/<id>` - Get strategy details
- `PUT /api/v1/strategies/<id>` - Update strategy
- `DELETE /api/v1/strategies/<id>` - Delete strategy
- `GET /api/v1/strategies/<id>/parameters` - Get strategy parameters

### **⚕️ Task 4: Health Check Enhancements** (Priority: MEDIUM)

**File**: `backend/api/routes/health.py`

**Sub-tasks:**
- [ ] Add database connectivity checks
- [ ] Add system metrics (CPU, memory, disk)
- [ ] Add API performance metrics placeholder
- [ ] Ensure all health endpoints are functional

### **🔗 Task 5: Frontend API Migration** (Priority: HIGH)

**Sub-tasks:**
- [ ] Update `frontend/src/config/api.ts` with new endpoints
- [ ] Update market data components to use `/api/v1/market/`
- [ ] Update strategy components to use `/api/v1/strategies/`
- [ ] Test all frontend functionality
- [ ] Ensure no broken API calls

### **🧪 Task 6: Testing Implementation** (Priority: HIGH)

**Sub-tasks:**
- [ ] Create unit tests for health routes
- [ ] Create unit tests for market data routes
- [ ] Create unit tests for strategy routes
- [ ] Create integration tests with database
- [ ] Ensure >80% test coverage for Sprint 1

---

## 📂 **File Structure Reference**

```
backend/api/
├── app.py                    # ✅ Flask application factory (READY)
├── routes/
│   ├── __init__.py          # ✅ Package init (READY)
│   ├── health.py            # ✅ Health checks (READY)
│   ├── market_data.py       # 🔄 Market consolidation (IN PROGRESS)
│   └── strategies.py        # 🔄 Strategy consolidation (IN PROGRESS)
└── middleware/              # ⏳ Sprint 2 (PLANNED)
    ├── __init__.py
    ├── error_handling.py
    ├── rate_limiting.py
    └── logging.py
```

---

## 🧪 **Testing Strategy**

### **Unit Tests** (Sprint 1)
```bash
# Test individual route functions
python -m pytest backend/tests/test_health_routes.py -v
python -m pytest backend/tests/test_market_routes.py -v  
python -m pytest backend/tests/test_strategy_routes.py -v
```

### **Integration Tests** (Sprint 1)
```bash
# Test full API workflows
python -m pytest backend/tests/test_api_integration.py -v
```

### **Manual Testing Checklist** (Sprint 1)
- [ ] Health check endpoints return proper JSON
- [ ] Market data endpoints return actual data from unified database
- [ ] Strategy CRUD operations work end-to-end
- [ ] Error handling returns proper HTTP status codes
- [ ] All endpoints include standardized response format

---

## 🔧 **Development Tips**

### **Working with the Unified Database**
```python
# Import pattern for routes
from backend.database.unified_data_access import UnifiedDataAccess

# Usage pattern
da = UnifiedDataAccess()
data = da.get_market_data('BTCUSDT', '1h', limit=100)
```

### **Standardized Response Format**
All endpoints should return this format:
```python
return jsonify({
    'timestamp': datetime.utcnow().isoformat(),
    'epic': 'Epic 7 Sprint 1',
    'data': actual_data,
    'count': len(data) if applicable,
    'status': 'success'
})
```

### **Error Response Format**
All errors should return this format:
```python
return jsonify({
    'error': 'Error type',
    'message': 'Detailed error message',
    'status': 'error'
}), status_code
```

### **Debug and Troubleshooting**
```bash
# Check what routes are registered
python -c "from backend.api.app import create_app; app = create_app(); [print(f'{rule.methods} {rule.rule}') for rule in app.url_map.iter_rules()]"

# Test database connectivity
python -c "from backend.database.unified_data_access import UnifiedDataAccess; da = UnifiedDataAccess(); print(da.get_database_stats())"

# Check application startup
python backend/api/app.py
```

---

## 📊 **Sprint 1 Definition of Done**

### **Technical Requirements**
- [ ] Flask application factory pattern implemented and working
- [ ] All Sprint 1 blueprints registered and functional  
- [ ] Health check endpoints operational
- [ ] Market data consolidation complete (3 files → 1 blueprint)
- [ ] Strategy consolidation complete (2 files → 1 blueprint)
- [ ] All endpoints return standardized response format
- [ ] Basic error handling implemented
- [ ] Database integration working through unified access layer

### **Testing Requirements**  
- [ ] Unit tests written for all new routes
- [ ] Integration tests passing
- [ ] Manual testing checklist completed
- [ ] No regression in existing functionality
- [ ] >80% test coverage for Sprint 1 code

### **Documentation Requirements**
- [ ] All new endpoints documented with docstrings
- [ ] Development guide updated
- [ ] Frontend migration documented
- [ ] Testing procedures documented

### **Migration Requirements**
- [ ] Frontend updated to use new API endpoints
- [ ] No breaking changes to existing functionality
- [ ] Old route files can be deprecated (not deleted yet)
- [ ] All original functionality preserved

---

## 🚨 **Common Issues & Solutions**

### **Issue: ImportError when running app.py**
```bash
# Solution: Ensure you're in the project root
cd /Users/[username]/Projects/PineOpt
python backend/api/app.py
```

### **Issue: Database not found**
```bash
# Solution: Verify unified database exists
ls -la backend/database/pineopt_unified.db

# If missing, run migration
python backend/database/migrate_data_only.py
```

### **Issue: Port already in use**
```bash
# Solution: Kill process using port 5007
lsof -ti:5007 | xargs kill -9
```

### **Issue: Blueprint not registering**
```bash
# Solution: Check import paths in app.py
# Ensure relative imports work from backend/api/app.py
```

---

## 📞 **Support & Resources**

### **Key Files Reference**
- **Epic Document**: `docs/architecture/Epic7_API_Architecture_Rationalization.md`
- **Application Factory**: `backend/api/app.py`
- **Database Access**: `backend/database/unified_data_access.py`
- **Original Routes**: `backend/api/` (old files for reference)

### **Testing Resources**
- **Test Framework**: `backend/tests/`
- **Database Testing**: Use `testing` config with in-memory SQLite
- **API Testing**: Use Flask test client

### **Migration Resources**
- **Frontend Config**: `frontend/src/config/api.ts`
- **Response Format**: Check existing frontend components for expected format

---

**Epic 7 Sprint 1 is ready for development! 🚀**

*Start with Task 1 (Blueprint Registration) and work through the checklist systematically.*