import logging
import os

def setup_logging():
    """Setup logging configuration"""
    env = os.getenv('ENV', 'production')
    log_level = logging.INFO if env == 'production' else logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Exam Hub API - Environment: {env.upper()}")
    logger.info(f"Logging level: {logging.getLevelName(log_level)}")
    
    return logger 