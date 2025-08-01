#!/usr/bin/env python3
"""
FIA v3.0 - Main entry point for Railway deployment
This file ensures Nixpacks detects the project as Python and provides
a simple entry point that delegates to the backend application.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point that starts the FastAPI backend"""
    try:
        # Get the root directory
        root_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.join(root_dir, 'backend')
        
        logger.info(f"Root directory: {root_dir}")
        logger.info(f"Backend directory: {backend_dir}")
        
        # Verify backend directory exists
        if not os.path.exists(backend_dir):
            logger.error(f"Backend directory not found: {backend_dir}")
            sys.exit(1)
            
        # Add both root and backend directories to Python path
        sys.path.insert(0, root_dir)
        sys.path.insert(0, backend_dir)
        
        # Change to backend directory for proper file paths
        os.chdir(backend_dir)
        logger.info(f"Changed working directory to: {os.getcwd()}")
        
        # Import and run uvicorn
        import uvicorn
        
        port = int(os.environ.get('PORT', '8000'))
        logger.info(f"Starting FastAPI application on port {port}")
        
        # Run with proper configuration for production
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()