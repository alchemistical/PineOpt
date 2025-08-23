"""
OpenAPI Specification Generator
Epic 7 Sprint 3 - Task 2: Generate API Documentation

Generates comprehensive OpenAPI 3.0 specification for Epic 7 API.
"""

from flask import Flask, current_app
from datetime import datetime
import json
import yaml


def generate_openapi_spec(app: Flask) -> dict:
    """Generate complete OpenAPI 3.0 specification for Epic 7 API"""
    
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "PineOpt API - Epic 7: API Architecture Rationalization",
            "version": "1.0.0",
            "description": """
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
            """,
            "termsOfService": "https://pineopt.dev/terms",
            "contact": {
                "name": "PineOpt API Support",
                "url": "https://pineopt.dev/support",
                "email": "support@pineopt.dev"
            },
            "license": {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5007",
                "description": "Development Server"
            },
            {
                "url": "https://api.pineopt.dev",
                "description": "Production Server"
            },
            {
                "url": "https://staging-api.pineopt.dev", 
                "description": "Staging Server"
            }
        ],
        "paths": {},
        "components": {
            "schemas": _get_component_schemas(),
            "responses": _get_standard_responses(),
            "parameters": _get_common_parameters(),
            "examples": _get_response_examples(),
            "headers": _get_response_headers()
        },
        "tags": [
            {
                "name": "Health",
                "description": "System health monitoring and status endpoints"
            },
            {
                "name": "Market Data", 
                "description": "Real-time and historical market data services"
            },
            {
                "name": "Strategies",
                "description": "Strategy management, validation, and CRUD operations"
            },
            {
                "name": "Conversions",
                "description": "Pine Script to Python conversion services"
            },
            {
                "name": "Backtests",
                "description": "Strategy backtesting and performance analysis"
            },
            {
                "name": "Middleware",
                "description": "Rate limiting, logging, and CORS configuration endpoints"
            }
        ]
    }
    
    # Add paths for each blueprint
    spec["paths"].update(_get_health_paths())
    spec["paths"].update(_get_market_paths()) 
    spec["paths"].update(_get_strategy_paths())
    spec["paths"].update(_get_conversion_paths())
    spec["paths"].update(_get_backtest_paths())
    spec["paths"].update(_get_middleware_paths())
    
    return spec


def _get_component_schemas() -> dict:
    """Define reusable schema components"""
    return {
        "StandardResponse": {
            "type": "object",
            "properties": {
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 timestamp of response"
                },
                "epic": {
                    "type": "string", 
                    "example": "Epic 7 - API Architecture Rationalization",
                    "description": "Epic project identifier"
                },
                "status": {
                    "type": "string",
                    "enum": ["success", "error", "healthy", "unhealthy"],
                    "description": "Response status"
                },
                "request_info": {
                    "$ref": "#/components/schemas/RequestInfo"
                }
            },
            "required": ["timestamp", "epic", "status"]
        },
        "SuccessResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/StandardResponse"},
                {
                    "type": "object",
                    "properties": {
                        "data": {
                            "description": "Response data"
                        },
                        "message": {
                            "type": "string",
                            "description": "Optional success message"
                        },
                        "meta": {
                            "type": "object",
                            "description": "Optional metadata"
                        }
                    },
                    "required": ["data"]
                }
            ]
        },
        "ErrorResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/StandardResponse"},
                {
                    "type": "object", 
                    "properties": {
                        "error": {
                            "$ref": "#/components/schemas/ErrorInfo"
                        }
                    },
                    "required": ["error"]
                }
            ]
        },
        "ErrorInfo": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Error type identifier"
                },
                "message": {
                    "type": "string",
                    "description": "Human-readable error message"
                },
                "status_code": {
                    "type": "integer",
                    "description": "HTTP status code"
                },
                "details": {
                    "description": "Additional error details"
                },
                "suggestion": {
                    "type": "string", 
                    "description": "Suggested resolution"
                }
            },
            "required": ["type", "message", "status_code"]
        },
        "RequestInfo": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "description": "HTTP method"
                },
                "path": {
                    "type": "string",
                    "description": "Request path"
                },
                "endpoint": {
                    "type": "string",
                    "description": "Flask endpoint name"
                }
            }
        },
        "HealthCheck": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name"
                },
                "status": {
                    "type": "string",
                    "enum": ["healthy", "unhealthy"],
                    "description": "Service health status"
                },
                "version": {
                    "type": "string",
                    "description": "Service version"
                },
                "health_checks": {
                    "type": "object",
                    "description": "Detailed health check results"
                }
            }
        },
        "Strategy": {
            "type": "object", 
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique strategy identifier"
                },
                "name": {
                    "type": "string",
                    "description": "Strategy name"
                },
                "description": {
                    "type": "string",
                    "description": "Strategy description"
                },
                "pine_code": {
                    "type": "string",
                    "description": "Pine Script source code"
                },
                "parameters": {
                    "type": "object",
                    "description": "Strategy parameters"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated_at": {
                    "type": "string", 
                    "format": "date-time"
                }
            }
        },
        "BacktestResult": {
            "type": "object",
            "properties": {
                "backtest_id": {
                    "type": "string",
                    "description": "Unique backtest identifier"
                },
                "strategy_id": {
                    "type": "string",
                    "description": "Strategy identifier"
                },
                "performance_metrics": {
                    "$ref": "#/components/schemas/PerformanceMetrics"
                },
                "equity_curve": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Equity curve data points"
                }
            }
        },
        "PerformanceMetrics": {
            "type": "object",
            "properties": {
                "total_return": {"type": "number", "description": "Total return percentage"},
                "annual_return": {"type": "number", "description": "Annualized return percentage"},
                "sharpe_ratio": {"type": "number", "description": "Risk-adjusted return ratio"},
                "max_drawdown": {"type": "number", "description": "Maximum drawdown percentage"},
                "win_rate": {"type": "number", "description": "Win rate (0-1)"},
                "total_trades": {"type": "integer", "description": "Total number of trades"},
                "profit_factor": {"type": "number", "description": "Profit factor ratio"}
            }
        }
    }


def _get_standard_responses() -> dict:
    """Define standard response templates"""
    return {
        "200Success": {
            "description": "Successful operation",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                }
            }
        },
        "400BadRequest": {
            "description": "Bad request - Invalid parameters",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "404NotFound": {
            "description": "Resource not found", 
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "422ValidationError": {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "429RateLimit": {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            },
            "headers": {
                "X-RateLimit-Limit-Minute": {
                    "$ref": "#/components/headers/RateLimitMinute"
                },
                "X-RateLimit-Remaining-Minute": {
                    "$ref": "#/components/headers/RateLimitRemaining"
                }
            }
        },
        "500InternalError": {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
    }


def _get_common_parameters() -> dict:
    """Define reusable parameters"""
    return {
        "StrategyId": {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "Strategy identifier",
            "schema": {"type": "string"}
        },
        "BacktestId": {
            "name": "id", 
            "in": "path",
            "required": True,
            "description": "Backtest identifier",
            "schema": {"type": "string"}
        }
    }


def _get_response_examples() -> dict:
    """Define response examples"""
    return {
        "HealthResponse": {
            "value": {
                "timestamp": "2025-08-23T10:53:24.509186",
                "epic": "Epic 7 - API Architecture Rationalization", 
                "status": "healthy",
                "service": "PineOpt API",
                "version": "v1",
                "request_info": {
                    "method": "GET",
                    "path": "/api/v1/health/",
                    "endpoint": "health.basic_health"
                }
            }
        },
        "ErrorResponse": {
            "value": {
                "timestamp": "2025-08-23T10:53:52.039846",
                "epic": "Epic 7 - API Architecture Rationalization",
                "status": "error", 
                "error": {
                    "type": "not_found",
                    "message": "Endpoint /nonexistent not found",
                    "status_code": 404
                },
                "request_info": {
                    "method": "GET",
                    "path": "/nonexistent",
                    "endpoint": None
                }
            }
        }
    }


def _get_response_headers() -> dict:
    """Define response headers"""
    return {
        "RateLimitMinute": {
            "description": "Requests allowed per minute",
            "schema": {"type": "integer"}
        },
        "RateLimitRemaining": {
            "description": "Requests remaining this minute", 
            "schema": {"type": "integer"}
        },
        "RequestId": {
            "description": "Unique request identifier",
            "schema": {"type": "string"}
        },
        "ResponseTime": {
            "description": "Response time in milliseconds",
            "schema": {"type": "string"}
        }
    }


def _get_health_paths() -> dict:
    """Define health endpoint paths"""
    return {
        "/api/v1/health/": {
            "get": {
                "tags": ["Health"],
                "summary": "Basic health check", 
                "description": "Returns basic service health status",
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthCheck"},
                                "example": {"$ref": "#/components/examples/HealthResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/health/detailed": {
            "get": {
                "tags": ["Health"],
                "summary": "Detailed health check",
                "description": "Returns detailed system health metrics including CPU, memory, and database status",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"},
                    "500": {"$ref": "#/components/responses/500InternalError"}
                }
            }
        },
        "/api/v1/health/metrics": {
            "get": {
                "tags": ["Health"],
                "summary": "Performance metrics",
                "description": "Returns API performance metrics (placeholder - will be implemented in Sprint 3)",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        }
    }


def _get_market_paths() -> dict:
    """Define market data endpoint paths"""  
    return {
        "/api/v1/market/": {
            "get": {
                "tags": ["Market Data"],
                "summary": "Market data API information",
                "description": "Returns available market data endpoints and capabilities",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        }
    }


def _get_strategy_paths() -> dict:
    """Define strategy management endpoint paths"""
    return {
        "/api/v1/strategies/": {
            "get": {
                "tags": ["Strategies"],
                "summary": "Strategy management API information", 
                "description": "Returns available strategy management endpoints",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/strategies/list": {
            "get": {
                "tags": ["Strategies"],
                "summary": "List all strategies",
                "description": "Returns paginated list of all strategies",
                "parameters": [
                    {
                        "name": "page",
                        "in": "query", 
                        "description": "Page number",
                        "schema": {"type": "integer", "default": 1}
                    },
                    {
                        "name": "per_page",
                        "in": "query",
                        "description": "Items per page",
                        "schema": {"type": "integer", "default": 20}
                    }
                ],
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/strategies/{id}": {
            "get": {
                "tags": ["Strategies"],
                "summary": "Get strategy by ID",
                "description": "Returns detailed strategy information",
                "parameters": [{"$ref": "#/components/parameters/StrategyId"}],
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"},
                    "404": {"$ref": "#/components/responses/404NotFound"}
                }
            },
            "put": {
                "tags": ["Strategies"],
                "summary": "Update strategy",
                "description": "Updates an existing strategy",
                "parameters": [{"$ref": "#/components/parameters/StrategyId"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Strategy"}
                        }
                    }
                },
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"},
                    "400": {"$ref": "#/components/responses/400BadRequest"},
                    "404": {"$ref": "#/components/responses/404NotFound"},
                    "422": {"$ref": "#/components/responses/422ValidationError"}
                }
            },
            "delete": {
                "tags": ["Strategies"],
                "summary": "Delete strategy",
                "description": "Deletes a strategy by ID",
                "parameters": [{"$ref": "#/components/parameters/StrategyId"}],
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"},
                    "404": {"$ref": "#/components/responses/404NotFound"}
                }
            }
        }
    }


def _get_conversion_paths() -> dict:
    """Define conversion service endpoint paths"""
    return {
        "/api/v1/conversions/": {
            "get": {
                "tags": ["Conversions"],
                "summary": "Conversion API information",
                "description": "Returns available Pine Script conversion endpoints and capabilities", 
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/conversions/health": {
            "get": {
                "tags": ["Conversions"],
                "summary": "Conversion service health",
                "description": "Returns health status of conversion services",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/conversions/analyze": {
            "post": {
                "tags": ["Conversions"],
                "summary": "Analyze Pine Script strategy",
                "description": "Analyzes Pine Script code and provides insights",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "pine_code": {
                                        "type": "string",
                                        "description": "Pine Script source code"
                                    }
                                },
                                "required": ["pine_code"]
                            },
                            "example": {
                                "pine_code": "//@version=5\nstrategy(\"Test Strategy\", overlay=true)\nsma = ta.sma(close, 20)\nif close > sma\n    strategy.entry(\"Long\", strategy.long)"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"},
                    "400": {"$ref": "#/components/responses/400BadRequest"},
                    "422": {"$ref": "#/components/responses/422ValidationError"},
                    "503": {
                        "description": "AI analysis service unavailable",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/conversions/convert/working": {
            "post": {
                "tags": ["Conversions"],
                "summary": "Convert Pine Script (working converter)",
                "description": "Converts Pine Script to Python using the working converter",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "pine_code": {"type": "string"},
                                    "target_format": {"type": "string", "default": "python"}
                                },
                                "required": ["pine_code"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"},
                    "400": {"$ref": "#/components/responses/400BadRequest"},
                    "503": {
                        "description": "Conversion service unavailable"
                    }
                }
            }
        },
        "/api/v1/conversions/indicators": {
            "get": {
                "tags": ["Conversions"],
                "summary": "List available indicators",
                "description": "Returns list of supported technical indicators for conversion",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        }
    }


def _get_backtest_paths() -> dict:
    """Define backtesting endpoint paths"""
    return {
        "/api/v1/backtests/": {
            "get": {
                "tags": ["Backtests"], 
                "summary": "Backtest API information",
                "description": "Returns available backtesting endpoints and capabilities",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/backtests/health": {
            "get": {
                "tags": ["Backtests"],
                "summary": "Backtest service health",
                "description": "Returns health status of backtesting services",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/backtests/run": {
            "post": {
                "tags": ["Backtests"],
                "summary": "Run strategy backtest",
                "description": "Executes backtest for a given strategy",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object", 
                                "properties": {
                                    "strategy_id": {"type": "string", "description": "Strategy identifier"},
                                    "symbol": {"type": "string", "description": "Trading pair symbol"},
                                    "timeframe": {"type": "string", "description": "Timeframe (1m, 5m, 1h, 1d, etc.)"},
                                    "start_date": {"type": "string", "format": "date", "description": "Backtest start date"},
                                    "end_date": {"type": "string", "format": "date", "description": "Backtest end date"},
                                    "initial_capital": {"type": "number", "description": "Initial capital amount"}
                                },
                                "required": ["strategy_id", "symbol", "timeframe"]
                            },
                            "example": {
                                "strategy_id": "test_strategy",
                                "symbol": "BTCUSDT", 
                                "timeframe": "1h",
                                "start_date": "2024-01-01",
                                "end_date": "2024-12-31",
                                "initial_capital": 10000
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Backtest results",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/BacktestResult"}
                            }
                        }
                    },
                    "404": {
                        "description": "Strategy not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "422": {"$ref": "#/components/responses/422ValidationError"}
                }
            }
        },
        "/api/v1/backtests/pairs/available": {
            "get": {
                "tags": ["Backtests"],
                "summary": "List available trading pairs",
                "description": "Returns list of available trading pairs for backtesting",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/backtests/history": {
            "get": {
                "tags": ["Backtests"],
                "summary": "Backtest history",
                "description": "Returns history of previous backtests",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        }
    }


def _get_middleware_paths() -> dict:
    """Define middleware configuration endpoint paths"""
    return {
        "/api/v1/rate-limit/status": {
            "get": {
                "tags": ["Middleware"],
                "summary": "Rate limit status",
                "description": "Returns current rate limiting status for the client",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/cors/config": {
            "get": {
                "tags": ["Middleware"],
                "summary": "CORS configuration",
                "description": "Returns current CORS configuration",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/cors/test": {
            "get": {
                "tags": ["Middleware"],
                "summary": "CORS functionality test",
                "description": "Test endpoint for CORS functionality validation",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        },
        "/api/v1/logs/config": {
            "get": {
                "tags": ["Middleware"], 
                "summary": "Logging configuration",
                "description": "Returns current logging middleware configuration",
                "responses": {
                    "200": {"$ref": "#/components/responses/200Success"}
                }
            }
        }
    }


def get_api_spec(app: Flask = None) -> dict:
    """Get the OpenAPI specification"""
    if app is None:
        app = current_app
    return generate_openapi_spec(app)


def save_openapi_spec(app: Flask, output_path: str):
    """Save OpenAPI specification to file"""
    spec = generate_openapi_spec(app)
    
    # Save as JSON
    json_path = output_path.replace('.yaml', '.json') if output_path.endswith('.yaml') else f"{output_path}.json"
    with open(json_path, 'w') as f:
        json.dump(spec, f, indent=2)
    
    # Save as YAML
    yaml_path = output_path.replace('.json', '.yaml') if output_path.endswith('.json') else f"{output_path}.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
    
    return json_path, yaml_path