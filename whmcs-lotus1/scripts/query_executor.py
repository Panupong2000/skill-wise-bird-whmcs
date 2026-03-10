"""
Dynamic Query Executor
Allows the AI agent to execute arbitrary SELECT queries against the WHMCS database.
Includes read-only validation and structured JSON output.
"""

from db import query


def execute_query(sql, limit=None):
    """
    Execute a dynamic SQL query (SELECT only).

    Args:
        sql: The SQL query string to execute
        limit: Optional max rows (default uses db.MAX_ROWS)

    Returns:
        dict with data, row_count, execution_time_sec or error
    """
    if not sql or not sql.strip():
        return {"error": "Empty query provided"}

    return query(sql, limit=int(limit) if limit else None)
