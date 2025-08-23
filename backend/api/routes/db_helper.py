"""
Database Helper for Epic 7 Routes
Handles import path resolution for unified database access
"""

import sys
import os

def get_database_access():
    """
    Get UnifiedDataAccess instance with proper import path handling
    
    Returns:
        UnifiedDataAccess instance
    """
    # Add backend directory to path
    backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    from database.unified_data_access import UnifiedDataAccess
    return UnifiedDataAccess()