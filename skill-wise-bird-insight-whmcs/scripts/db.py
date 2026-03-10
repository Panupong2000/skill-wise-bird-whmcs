"""
WHMCS Database Connection Layer
- Loads config from .env
- Read-only enforcement (blocks INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE)
- Parameterized queries with error handling
- Query timeout and connection retry
- Query logging with execution time
"""

import os
import re
import sys
import time
import subprocess

# --- Dependency bootstrap (for sandbox environments) ---
try:
    import pymysql
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "pymysql"]
    )
    sys.path.insert(0, "/tmp/pylib")
    import pymysql

try:
    from dotenv import load_dotenv
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "python-dotenv"]
    )
    sys.path.insert(0, "/tmp/pylib")
    from dotenv import load_dotenv

from logger import log_query, log_error

# --- Load environment ---
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(_env_path)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "whmcs_readonly"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "whmcs"),
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": int(os.getenv("DB_TIMEOUT", 30)),
    "read_timeout": int(os.getenv("DB_TIMEOUT", 30)),
    "charset": "utf8mb4",
}

# --- Safety ---
DANGEROUS_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|RENAME|REPLACE|GRANT|REVOKE|LOAD)\b",
    re.IGNORECASE,
)

DEFAULT_LIMIT = 100
MAX_RETRIES = 2


def get_connection():
    """Create a new MySQL connection with retry."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            conn = pymysql.connect(**DB_CONFIG)
            return conn
        except pymysql.MySQLError as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(1)
    log_error("Connection failed after retries", exception=last_error)
    raise last_error


def validate_read_only(sql):
    """Raise ValueError if SQL contains write/DDL statements."""
    stripped = sql.strip().rstrip(";").strip()
    match = DANGEROUS_PATTERNS.search(stripped)
    if match:
        raise ValueError(
            f"❌ Blocked: Only SELECT queries allowed. "
            f"Detected '{match.group()}' statement."
        )


def query(sql, params=None, limit=None):
    """
    Execute a read-only SQL query.

    Args:
        sql: SQL string (SELECT only)
        params: Optional tuple/list for parameterized query
        limit: Max rows to return (default 100)

    Returns:
        dict with keys: data, row_count, execution_time_sec, columns
    """
    validate_read_only(sql)
    row_limit = limit if limit else DEFAULT_LIMIT

    conn = get_connection()
    start = time.time()

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchmany(row_limit)
            elapsed = round(time.time() - start, 3)

            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            log_query(sql, execution_time=elapsed, row_count=len(rows), params=params)

            return {
                "data": rows,
                "row_count": len(rows),
                "columns": columns,
                "execution_time_sec": elapsed,
            }

    except pymysql.MySQLError as e:
        log_error("Query execution failed", sql=sql, exception=e)
        return {"error": f"MySQL Error: {e}", "sql": sql}
    except ValueError:
        raise
    except Exception as e:
        log_error("Unexpected error", sql=sql, exception=e)
        return {"error": f"Error: {e}", "sql": sql}
    finally:
        conn.close()


def query_raw(sql, params=None, limit=None):
    """Execute query and return just the data rows (list of dicts)."""
    result = query(sql, params, limit)
    if "error" in result:
        return result
    return result["data"]


def get_table_schema(table_name):
    """
    Get column definitions for a WHMCS table.
    Uses DESCRIBE which is read-only.
    """
    # Whitelist allowed tables to prevent injection
    allowed = {
        "tblclients", "tbldomains", "tblhosting", "tblinvoices",
        "tblinvoiceitems", "tblproducts", "tblproductgroups",
        "tblorders", "tbltickets", "tblcurrencies",
    }
    if table_name not in allowed:
        return {"error": f"Table '{table_name}' not in allowed list: {sorted(allowed)}"}

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`")
            rows = cursor.fetchall()
            return {
                "table": table_name,
                "columns": rows,
                "column_count": len(rows),
            }
    except pymysql.MySQLError as e:
        return {"error": f"MySQL Error: {e}"}
    finally:
        conn.close()
