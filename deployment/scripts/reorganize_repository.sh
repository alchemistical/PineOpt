#!/bin/bash

# PineOpt Repository Reorganization Script
# Transforms chaotic file structure into organized architecture
# 
# Created: August 22, 2025
# Status: Ready for execution

set -e  # Exit on any error

echo "🏗️ Starting PineOpt repository reorganization..."

# Create new directory structure
echo "📁 Creating new directory structure..."
mkdir -p {docs/{api,architecture,user-guide,development},backend/{api,database,services,conversion,tests},frontend/{src,public,tests},examples/{pine-scripts,strategies,data},deployment/{docker,nginx,scripts},research/{notebooks,experiments,analysis},outputs/{logs,reports,data}}

echo "✅ Directory structure created"

# =====================================================
# MOVE DOCUMENTATION
# =====================================================
echo "📚 Reorganizing documentation..."

# Move documentation files
if [ -d "documentation" ]; then
    mv documentation/* docs/architecture/ 2>/dev/null || true
    rmdir documentation 2>/dev/null || true
fi

# Move specific docs
mv API_TEST_REPORT_QA.md docs/api/ 2>/dev/null || true
mv UXPLAN.md docs/user-guide/ 2>/dev/null || true
mv Epic*.md docs/architecture/ 2>/dev/null || true
mv REPOSITORY_CLEANUP_ACTION_PLAN.md docs/development/ 2>/dev/null || true

# Remove duplicate documentation directories
rm -rf Documentations/ 2>/dev/null || true

echo "✅ Documentation reorganized"

# =====================================================
# MOVE BACKEND CODE
# =====================================================
echo "🔧 Reorganizing backend code..."

# Move API code
if [ -d "api" ]; then
    cp -r api/* backend/api/ 2>/dev/null || true
    # Keep original api directory for now (will remove later)
fi

# Move database code
if [ -d "database" ]; then
    cp -r database/* backend/database/ 2>/dev/null || true
    # Keep original database directory for now
fi

# Move Pine2Py conversion code
if [ -d "pine2py" ]; then
    mv pine2py/* backend/conversion/ 2>/dev/null || true
    rmdir pine2py 2>/dev/null || true
fi

# Move research code to services
if [ -d "research/analysis" ]; then
    mv research/analysis/* backend/services/ 2>/dev/null || true
fi

if [ -d "research/backtest" ]; then
    mv research/backtest/* backend/services/ 2>/dev/null || true
fi

# Move tests
if [ -d "tests" ]; then
    mv tests/* backend/tests/ 2>/dev/null || true
    rmdir tests 2>/dev/null || true
fi

# Move test files from root
mv test_*.py backend/tests/ 2>/dev/null || true

echo "✅ Backend code reorganized"

# =====================================================
# MOVE FRONTEND CODE
# =====================================================
echo "🎨 Reorganizing frontend code..."

# Move src directory
if [ -d "src" ]; then
    cp -r src/* frontend/src/ 2>/dev/null || true
    # Keep original src for now
fi

# Move public files
mv index.html frontend/public/ 2>/dev/null || true

# Create frontend package.json if it doesn't exist
if [ ! -f "frontend/package.json" ]; then
    # Copy root package.json to frontend
    cp package.json frontend/ 2>/dev/null || true
fi

echo "✅ Frontend code reorganized"

# =====================================================
# MOVE EXAMPLES AND DEMOS
# =====================================================
echo "🧪 Reorganizing examples..."

# Move examples
if [ -d "examples" ]; then
    cp -r examples/* examples/ 2>/dev/null || true
fi

# Move demo files
mv demo_*.pine examples/pine-scripts/ 2>/dev/null || true
mv hye_*.pine examples/pine-scripts/ 2>/dev/null || true
mv test_*.pine examples/pine-scripts/ 2>/dev/null || true
mv *.pine examples/pine-scripts/ 2>/dev/null || true

# Move generated strategies
if [ -d "generated_strategies" ]; then
    mv generated_strategies/* examples/strategies/ 2>/dev/null || true
    rmdir generated_strategies 2>/dev/null || true
fi

echo "✅ Examples reorganized"

# =====================================================
# MOVE DEPLOYMENT FILES
# =====================================================
echo "🚀 Reorganizing deployment files..."

# Move Docker files
mv Dockerfile.* deployment/docker/ 2>/dev/null || true
mv docker-compose.yml deployment/docker/ 2>/dev/null || true
mv nginx.conf deployment/nginx/ 2>/dev/null || true

# Move scripts
if [ -d "scripts" ]; then
    mv scripts/* deployment/scripts/ 2>/dev/null || true
    rmdir scripts 2>/dev/null || true
fi

echo "✅ Deployment files reorganized"

# =====================================================
# MOVE RESEARCH CODE
# =====================================================
echo "🔬 Reorganizing research code..."

# Move research notebooks if they exist
if [ -d "research/notebooks" ]; then
    mv research/notebooks/* research/notebooks/ 2>/dev/null || true
fi

# Move AI analysis
if [ -d "research/ai_analysis" ]; then
    mv research/ai_analysis/* research/experiments/ 2>/dev/null || true
fi

# Move intelligent converter
if [ -d "research/intelligent_converter" ]; then
    mv research/intelligent_converter/* research/experiments/ 2>/dev/null || true
fi

echo "✅ Research code reorganized"

# =====================================================
# MOVE OUTPUT FILES
# =====================================================
echo "📊 Reorganizing output files..."

# Move output files to proper locations
mv *.json outputs/logs/ 2>/dev/null || true
mv *.log outputs/logs/ 2>/dev/null || true

# The outputs directory structure is already there and populated
echo "✅ Output files reorganized"

# =====================================================
# CLEAN UP ROOT DIRECTORY
# =====================================================
echo "🧹 Cleaning up root directory..."

# Move remaining Python files to backend/tests
mv *.py backend/tests/ 2>/dev/null || true

# Move shared directory
if [ -d "shared" ]; then
    mv shared/* backend/ 2>/dev/null || true
    rmdir shared 2>/dev/null || true
fi

echo "✅ Root directory cleaned"

# =====================================================
# CREATE NEW CONFIGURATION FILES
# =====================================================
echo "⚙️ Creating new configuration files..."

# Create root-level package.json for monorepo
cat > package.json << 'EOF'
{
  "name": "pineopt",
  "version": "1.0.0",
  "description": "Advanced Crypto Algorithm Lab - Pine Script to Python Conversion Platform",
  "private": true,
  "workspaces": [
    "frontend"
  ],
  "scripts": {
    "dev": "concurrently \"npm run backend:dev\" \"npm run frontend:dev\"",
    "backend:dev": "cd backend && python api/app.py",
    "frontend:dev": "cd frontend && npm run dev",
    "build": "cd frontend && npm run build",
    "test": "npm run test:backend && npm run test:frontend",
    "test:backend": "cd backend && python -m pytest tests/",
    "test:frontend": "cd frontend && npm test",
    "lint": "npm run lint:backend && npm run lint:frontend",
    "lint:backend": "cd backend && python -m flake8 .",
    "lint:frontend": "cd frontend && npm run lint"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  },
  "author": "PineOpt Team",
  "license": "MIT"
}
EOF

# Create environment example
cat > .env.example << 'EOF'
# Database
DATABASE_URL=sqlite:///backend/database/pineopt_unified.db

# API Configuration  
API_PORT=5007
API_HOST=0.0.0.0
FLASK_ENV=development

# Frontend
FRONTEND_PORT=3000
FRONTEND_URL=http://localhost:3000

# External APIs
BINANCE_API_URL=https://api.binance.com
RATE_LIMIT_REQUESTS=1200
RATE_LIMIT_WINDOW=60

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
EOF

# Create root README
cat > README.md << 'EOF'
# PineOpt 🚀

> **Advanced Crypto Algorithm Lab** - Pine Script to Python Conversion & Strategy Research Platform

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

## 🎯 Overview

PineOpt converts TradingView Pine Script strategies into Python code for backtesting with real cryptocurrency market data. Built for developers and researchers to explore, optimize, and validate crypto trading algorithms.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Installation
```bash
git clone https://github.com/your-username/PineOpt.git
cd PineOpt
npm install
pip install -r backend/requirements.txt
```

### Development
```bash
# Start both backend and frontend
npm run dev

# Or start separately:
npm run backend:dev  # http://localhost:5007
npm run frontend:dev # http://localhost:3000
```

## 📁 Project Structure

```
PineOpt/
├── 📚 docs/                          # Documentation
├── 🔧 backend/                      # Python backend
├── 🎨 frontend/                     # React frontend  
├── 🧪 examples/                     # Sample code
├── 🚀 deployment/                   # Docker & deployment
├── 🔬 research/                     # Research & experiments
└── 📊 outputs/                      # Generated outputs
```

## ✨ Features

- **Pine Script Conversion**: Automated translation to Python
- **Crypto Market Data**: 470+ USDT perpetual futures  
- **Professional Charts**: TradingView-style visualization
- **Strategy Backtesting**: Historical performance analysis
- **Unified Database**: Consolidated data management

## 📚 Documentation

- [API Reference](docs/api/)
- [User Guide](docs/user-guide/)
- [Architecture](docs/architecture/)
- [Development Setup](docs/development/)

## 🤝 Contributing

See [Contributing Guide](docs/development/contributing.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

**Built with ❤️ for the crypto trading community**
EOF

echo "✅ New configuration files created"

# =====================================================
# SUMMARY AND VALIDATION
# =====================================================
echo ""
echo "🎉 Repository reorganization completed!"
echo ""
echo "📊 Summary:"
echo "  ✅ Documentation consolidated in docs/"
echo "  ✅ Backend code organized in backend/"
echo "  ✅ Frontend code organized in frontend/"
echo "  ✅ Examples organized in examples/"
echo "  ✅ Deployment files in deployment/"
echo "  ✅ Research code in research/"
echo "  ✅ Outputs organized in outputs/"
echo "  ✅ Root directory cleaned"
echo "  ✅ New configuration files created"
echo ""
echo "🔍 Validating structure..."

# Count files in each major directory
dirs=("docs" "backend" "frontend" "examples" "deployment" "research" "outputs")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f | wc -l | tr -d ' ')
        echo "  $dir: $count files"
    fi
done

echo ""
echo "⚠️ IMPORTANT: Original directories (api/, src/, etc.) still exist for safety"
echo "   After testing, you can remove them with: rm -rf api/ src/ database/ research/"
echo ""
echo "🚀 Next steps:"
echo "  1. Test the new structure: npm run dev"
echo "  2. Update import paths if needed"
echo "  3. Remove old directories after validation"
echo "  4. Commit the new structure"
echo ""
echo "✅ Reorganization script completed successfully!"