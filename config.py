import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for WhatsApp Bot"""
    
    # WhatsApp Business API Configuration
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'default_verify_token_12345')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    PORT = int(os.getenv('PORT', 5000))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # ML Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'xgboost_model.pkl')
    SCALER_PATH = os.getenv('SCALER_PATH', 'scaler.pkl')
    
    # Database Configuration (for future use)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Rate Limiting (messages per minute per user)
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 10))
    
    # Session timeout (in minutes)
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.WHATSAPP_TOKEN:
            errors.append("WHATSAPP_TOKEN is required")
        
        if not cls.PHONE_NUMBER_ID:
            errors.append("PHONE_NUMBER_ID is required")
        
        if errors:
            raise ValueError("Configuration errors: " + ", ".join(errors))
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}