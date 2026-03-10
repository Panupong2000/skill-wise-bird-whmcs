"""
WHMCS Database Connection Module
- Parameterized queries with read-only safety guard
- Connection timeout and error handling
- Result row limiting to prevent memory overflow
"""

import sys
import subprocess
import re
import time

try:
    import pymysql
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "pymysql"]
    )
    sys.path.insert(0, "/tmp/pylib")
    import pymysql


DB_CONFIG = {
    "host": "103.2.113.229",
    "port": 3306,
    "user": "lotus_whmcs",
    "password": "w,jmik[8iy[",
    "database": "temp-whmcs",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 10,
    "read_timeout": 30,
    "charset": "utf8mb4",
}

# SQL statements that modify data — blocked for safety
DANGEROUS_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|RENAME|REPLACE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

MAX_ROWS = 200


def get_connection():
    """Create and return a new MySQL connection."""
    return pymysql.connect(**DB_CONFIG)


def validate_read_only(sql):
    """Check that the SQL is a read-only SELECT statement."""
    stripped = sql.strip().rstrip(";").strip()
    if DANGEROUS_PATTERNS.search(stripped):
        raise ValueError(
            f"Blocked: Only SELECT queries are allowed. "
            f"Detected write/DDL statement."
        )
    return True


def query(sql, params=None, limit=None):
    """
    Execute a read-only SQL query and return results as list of dicts.

    Args:
        sql: SQL query string (SELECT only)
        params: Optional tuple/list of parameters for parameterized queries
        limit: Max rows to return (default MAX_ROWS)
    """
    validate_read_only(sql)

    row_limit = limit or MAX_ROWS
    conn = get_connection()
    start = time.time()

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchmany(row_limit)
            elapsed = round(time.time() - start, 3)

            return {
                "data": rows,
                "row_count": len(rows),
                "execution_time_sec": elapsed,
            }

    except pymysql.MySQLError as e:
        return {"error": f"MySQL Error: {e}", "sql": sql}
    except Exception as e:
        return {"error": f"Error: {e}", "sql": sql}
    finally:
        conn.close()


def query_raw(sql, params=None, limit=None):
    """
    Execute a read-only SQL query and return just the data rows.
    Convenience wrapper for tools that don't need metadata.
    """
    result = query(sql, params, limit)
    if "error" in result:
        return result
    return result["data"]