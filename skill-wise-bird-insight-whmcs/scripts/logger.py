"""
Centralized Logging for WHMCS Insight Queries
- Query log: logs/whmcs_queries.log
- Error log: logs/errors.log
"""

import logging
import os
import sys
from datetime import datetime

# สร้าง logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

QUERY_LOG_FILE = os.path.join(LOG_DIR, "whmcs_queries.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "errors.log")


def _setup_logger(name, log_file, level=logging.INFO):
    """Create a logger with file + console handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler (stderr so stdout stays clean for JSON output)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.WARNING)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


query_logger = _setup_logger("whmcs.query", QUERY_LOG_FILE)
error_logger = _setup_logger("whmcs.error", ERROR_LOG_FILE, logging.ERROR)


def log_query(sql, execution_time=None, row_count=None, params=None):
    """Log a successful query execution."""
    parts = [f"SQL: {sql.strip()[:500]}"]
    if params:
        parts.append(f"Params: {params}")
    if execution_time is not None:
        parts.append(f"Time: {execution_time:.3f}s")
    if row_count is not None:
        parts.append(f"Rows: {row_count}")
    query_logger.info(" | ".join(parts))


def log_error(message, sql=None, exception=None):
    """Log an error."""
    parts = [f"Error: {message}"]
    if sql:
        parts.append(f"SQL: {sql.strip()[:500]}")
    if exception:
        parts.append(f"Exception: {type(exception).__name__}: {exception}")
    error_logger.error(" | ".join(parts))
