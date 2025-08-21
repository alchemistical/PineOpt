# Pine Strategy Upload UI

A comprehensive web-based interface for uploading Pine Script strategies, converting them to Python, and saving to database.

## Features

### 🔄 Pine Script Upload & Conversion
- **File Upload**: Support for `.pine` and `.txt` files via drag-and-drop or file picker
- **Strategy Attributes**: Edit strategy name and description before conversion
- **Real-time Conversion**: Convert Pine Script to Python using the Pine2Py pipeline
- **Code Preview**: View the generated Python code before saving

### 💾 Database Integration
- **SQLite Storage**: Automatically saves converted strategies to database
- **Strategy Management**: View all saved strategies with metadata
- **Version Control**: Track conversion timestamps and source code

### 🎯 User Experience
- **Success/Error Messages**: Clear feedback for all user actions
- **Loading States**: Visual indicators during processing
- **Responsive Design**: Works on desktop and mobile devices
- **Tabbed Interface**: Separate sections for OHLC data and Pine scripts

## Architecture

### Frontend (React + TypeScript)
```
src/
├── components/
│   ├── PineStrategyUpload.tsx  # Main Pine upload component
│   ├── FileUpload.tsx          # OHLC data upload (existing)
│   └── SimpleChart.tsx         # Chart visualization (existing)
└── App.tsx                     # Main app with tabbed interface
```

### Backend (Flask + Python)
```
api/
├── server.py                   # Flask API server
└── strategies.db               # SQLite database (auto-created)
```

### API Endpoints
- `POST /api/convert-pine` - Convert Pine Script to Python
- `POST /api/strategies` - Save converted strategy to database
- `GET /api/strategies` - Get all saved strategies
- `GET /api/strategies/<id>` - Get specific strategy
- `GET /api/test-conversion` - Test conversion pipeline

## Quick Start

### 1. Install Dependencies
```bash
# Python dependencies
source .venv/bin/activate
pip install flask flask-cors

# Node dependencies (if not already installed)
npm install
```

### 2. Start Development Environment
```bash
# Option 1: Use the startup script
./start-dev.sh

# Option 2: Start manually
# Terminal 1 - API Server
source .venv/bin/activate && cd api && python server.py

# Terminal 2 - React Frontend
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:5001
- Navigate to the "Pine Scripts" tab to use the converter

## Usage Workflow

### 1. Upload Pine Script
- Click on "Pine Scripts" tab
- Drag and drop a `.pine` file or click "Choose File"
- The file content will be automatically loaded and parsed

### 2. Edit Strategy Attributes
- **Strategy Name**: Modify the auto-detected or default name
- **Description**: Add a description for documentation

### 3. Convert to Python
- Click "Convert to Python" button
- The Pine2Py pipeline will process the script
- Generated Python code will be displayed in the preview section

### 4. Save to Database
- Review the generated Python code
- Click "Save to Database" to persist the strategy
- Success message will show the saved strategy ID

## Supported Pine Script Features

### Currently Supported (MVP)
- Basic RSI strategies
- Input parameters with ranges
- Simple entry/exit conditions
- Strategy metadata extraction

### Planned Features
- Moving averages (SMA, EMA, WMA)
- Bollinger Bands and other indicators
- Complex conditional logic
- Multi-timeframe analysis
- Advanced order types

## Sample Pine Script

Create a test file with this content:

```pinescript
//@version=5
strategy("Sample RSI Strategy", overlay=false)

// Input parameters
rsi_length = input.int(14, title="RSI Length", minval=1, maxval=100)
rsi_overbought = input.float(70.0, title="RSI Overbought", minval=50, maxval=100)
rsi_oversold = input.float(30.0, title="RSI Oversold", minval=0, maxval=50)

// Calculate RSI
rsi_value = ta.rsi(close, rsi_length)

// Entry conditions
long_condition = ta.crossover(rsi_value, rsi_oversold)
short_condition = ta.crossunder(rsi_value, rsi_overbought)

// Execute trades
if long_condition
    strategy.entry("Long", strategy.long)

if short_condition
    strategy.entry("Short", strategy.short)
```

## Database Schema

```sql
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    pine_source TEXT NOT NULL,
    python_code TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

### Common Issues & Solutions

1. **Port 5000 Already in Use**
   - The API server uses port 5001 to avoid conflicts with macOS AirPlay
   - Ensure nothing else is running on port 5001

2. **Conversion Failed**
   - Check Pine Script syntax
   - Ensure the script contains recognizable patterns (currently RSI-focused)
   - Review the error message in the UI

3. **Database Connection Issues**
   - The SQLite database is created automatically
   - Check write permissions in the `api/` directory

## Development Notes

### Adding New Pine Script Patterns
1. Update `pine2py/codegen/emit.py` to recognize new patterns
2. Add corresponding Python implementations in `pine2py/runtime/`
3. Test with sample Pine scripts

### UI Customization
- All styling uses Tailwind CSS classes
- Dark theme is applied consistently
- Responsive breakpoints are defined in `tailwind.config.js`

## Security Considerations

- File uploads are restricted to `.pine` and `.txt` files
- Generated Python code is validated for syntax errors
- No external code execution - conversion is pattern-based
- SQLite database is local (not accessible externally)

## Production Deployment

For production deployment:

1. **Use a Production WSGI Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 api.server:app
   ```

2. **Build React Frontend**:
   ```bash
   npm run build
   # Serve the dist/ directory with nginx or similar
   ```

3. **Environment Variables**:
   ```bash
   export FLASK_ENV=production
   export PORT=5001
   ```

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new Pine Script patterns
3. Update documentation for new features
4. Ensure responsive design for new UI components

## License

Part of the PineOpt Trading Analytics Platform.