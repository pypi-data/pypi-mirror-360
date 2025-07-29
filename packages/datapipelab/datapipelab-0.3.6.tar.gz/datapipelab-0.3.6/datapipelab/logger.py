import sys
from loguru import logger
from pathlib import Path

# Create logs directory
log_dir = Path(__file__).resolve().parent / "logs"
log_dir.mkdir(exist_ok=True)

# Log file path
log_file = log_dir / "app.log"

# Remove the default loguru handler
logger.remove()

# Add combined rotation: size and time
logger.add(
    str(log_file),
    rotation="10 MB",              # Rotate if file exceeds 10MB
    retention=100,                 # Keep last 100 files
    compression="zip",             # Compress rotated logs as .zip
    enqueue=True,
    backtrace=True,
    diagnose=True,
    level="INFO",
    serialize=True
)

# Add console handler
logger.add(
    sink=sys.stdout,               # Output to console
    level="INFO",                  # Set log level
    backtrace=True,
    diagnose=True,
    colorize=True                  # Enable colored output
)