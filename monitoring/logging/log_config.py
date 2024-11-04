import logging
import logging.config
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SysLogHandler
from pathlib import Path

LOG_DIR = Path("/var/log/website") 
LOG_FILE = LOG_DIR / "app.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB per log file
LOG_BACKUP_COUNT = 5  # Keep 5 backup log files
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define a formatter for all logs
formatter = logging.Formatter(LOG_FORMAT)

# Create a file handler that rotates logs when they reach a certain size
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter)

# Create a console handler that outputs to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# Create a syslog handler for cloud-based logging
syslog_handler = SysLogHandler(address='/dev/log')
syslog_handler.setFormatter(formatter)

# Custom logger with multiple handlers
logger = logging.getLogger("website_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.addHandler(syslog_handler)

# Usage
logger.info("Logging initialized and configuration is set.")

def set_log_level(level):
    """
    Set the logging level for all handlers.
    Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    logger.setLevel(level)
    file_handler.setLevel(level)
    console_handler.setLevel(level)
    syslog_handler.setLevel(level)

# Function to demonstrate logging
def log_performance_metrics(query_time, results_count):
    if query_time > 5.0:
        logger.warning(f"Query took too long: {query_time} seconds")
    else:
        logger.info(f"Query executed in {query_time} seconds, {results_count} results returned")

# Advanced log rotation based on time (rotate every midnight)
time_rotating_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", backupCount=LOG_BACKUP_COUNT
)
time_rotating_handler.setFormatter(formatter)
logger.addHandler(time_rotating_handler)

# Adding a custom filter for log messages
class CustomLogFilter(logging.Filter):
    def filter(self, record):
        return 'ERROR' in record.getMessage()

# Apply filter to syslog handler
syslog_handler.addFilter(CustomLogFilter())

# Adding structured logging (JSON format)
try:
    import json_log_formatter
    json_formatter = json_log_formatter.JSONFormatter()
    json_file_handler = logging.FileHandler(LOG_DIR / "json_logs.log")
    json_file_handler.setFormatter(json_formatter)
    logger.addHandler(json_file_handler)
except ImportError:
    logger.error("json_log_formatter module not installed, skipping JSON logging")

# Log to external services (cloud, Elastic, Splunk)
def log_to_external_service(service_name, message, level="INFO"):
    if service_name == "Elastic":
        elastic_handler = logging.StreamHandler(sys.stdout) 
        elastic_handler.setFormatter(formatter)
        logger.addHandler(elastic_handler)
        logger.info(message)
    elif service_name == "Splunk":
        splunk_handler = logging.StreamHandler(sys.stdout)  
        splunk_handler.setFormatter(formatter)
        logger.addHandler(splunk_handler)
        logger.info(message)

# Health check log for monitoring
def log_health_check(status):
    if status == "OK":
        logger.info("System health check passed")
    else:
        logger.error(f"System health check failed: {status}")

# Configuration for specific modules
def configure_module_logging(module_name, log_file):
    module_logger = logging.getLogger(module_name)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    module_logger.addHandler(handler)
    return module_logger

# Module-specific logging
db_logger = configure_module_logging("database", LOG_DIR / "db.log")
crawler_logger = configure_module_logging("crawler", LOG_DIR / "crawler.log")

# Logging in database operations
def log_db_query(query, time_taken):
    if time_taken > 2.0:
        db_logger.warning(f"Slow query detected: {query} took {time_taken} seconds")
    else:
        db_logger.info(f"Executed query: {query} in {time_taken} seconds")

# Logging in crawler operations
def log_crawl_event(url, status_code):
    if status_code != 200:
        crawler_logger.error(f"Failed to crawl {url}, status code: {status_code}")
    else:
        crawler_logger.info(f"Successfully crawled {url}, status code: {status_code}")

# Logging critical errors
def log_critical_error(error_message, traceback_info):
    logger.critical(f"Critical error occurred: {error_message}\nTraceback: {traceback_info}")

# Logging for metrics
def log_metrics(cpu_usage, memory_usage):
    logger.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
    if cpu_usage > 90:
        logger.warning("High CPU usage detected")
    if memory_usage > 90:
        logger.warning("High memory usage detected")

# Custom logging format for API responses
class APILogFormatter(logging.Formatter):
    def format(self, record):
        record.msg = f"API response: {record.msg}"
        return super().format(record)

# API logging
def log_api_response(endpoint, response_code, response_time):
    api_logger = logging.getLogger("api")
    api_handler = logging.StreamHandler(sys.stdout)
    api_handler.setFormatter(APILogFormatter(LOG_FORMAT))
    api_logger.addHandler(api_handler)
    
    if response_time > 1.0:
        api_logger.warning(f"Slow response from {endpoint}, time: {response_time}s")
    api_logger.info(f"API response from {endpoint}, code: {response_code}")

# Configuring logging level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
set_log_level(log_level)

logger.info("Logger configuration complete.")