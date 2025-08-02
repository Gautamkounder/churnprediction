#!/usr/bin/env python3
"""
WhatsApp Bot Startup Script
"""

import os
import sys
import logging
from config import config

def setup_logging(log_level):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('whatsapp_bot.log')
        ]
    )

def main():
    """Main startup function"""
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Load configuration
    app_config = config.get(env, config['default'])
    
    # Setup logging
    setup_logging(app_config.LOG_LEVEL)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        app_config.validate_config()
        logger.info(f"Starting WhatsApp Bot in {env} mode")
        
        # Import and run the app
        from whatsapp_bot import app
        
        # Configure app
        app.config.from_object(app_config)
        
        # Start the server
        logger.info(f"Server starting on port {app_config.PORT}")
        app.run(
            host='0.0.0.0',
            port=app_config.PORT,
            debug=app_config.DEBUG
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()