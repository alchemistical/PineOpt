"""
Initialize Epic 5 Strategy Database
Extends the existing database with strategy management tables
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.strategy_models import StrategyDatabase

def init_strategy_database():
    """Initialize strategy management database tables"""
    try:
        print("🔧 Initializing Epic 5 Strategy Database...")
        
        # Database path
        db_path = project_root / 'database' / 'pineopt.db'
        
        # Initialize strategy database
        strategy_db = StrategyDatabase(str(db_path))
        
        print("✅ Strategy database initialized successfully!")
        print(f"📁 Database location: {db_path}")
        
        # Test the database
        stats = strategy_db.get_strategy_stats()
        print(f"📊 Database stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize strategy database: {e}")
        return False

if __name__ == "__main__":
    success = init_strategy_database()
    sys.exit(0 if success else 1)