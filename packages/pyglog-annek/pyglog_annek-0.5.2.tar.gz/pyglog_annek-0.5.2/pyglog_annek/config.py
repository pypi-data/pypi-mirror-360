import logging
import os
import sys
from dotenv import load_dotenv


def setup_environment():
    """Load environment variables and validate required configuration."""
    load_dotenv()
    
    graylog_address = os.getenv("GRAYLOG_ADDR")
    graylog_token = os.getenv("GRAYLOG_TOKEN")
    
    if graylog_address is None or graylog_token is None:
        print("You must set GRAYLOG_ADDR and GRAYLOG_TOKEN or define them in a .env file.")
        sys.exit(1)
    
    return graylog_address, graylog_token


def setup_logging():
    """Configure logging for the application."""
    logname = "pyglog.log"
    
    logging.basicConfig(
        filename=logname,
        filemode="a",
        format="%(asctime)s.%(msecs)d %(name)s %(levelname)s -- %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )
    
    logger = logging.getLogger("pyglog")
    logger.info("Starting Pyglog the Graylog CLI in Python")
    return logger