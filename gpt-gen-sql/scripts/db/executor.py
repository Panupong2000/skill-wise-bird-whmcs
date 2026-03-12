import sys
import time

try:
    import pymysql
    import pymysql.err
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "pymysql"])
    sys.path.insert(0, "/tmp/pylib")
    import pymysql
    import pymysql.err

from .connection import get_connection

# Max rows to return; warn if result set exceeds this
ROW_LIMIT = 500

# Queries slower than this (seconds) get auto-EXPLAIN logged
SLOW_QUERY_THRESHOLD = 2.0

# Connection / query retry settings
MAX_RETRIES = 2


def execute_query(sql):
    """Execute a SELECT query with timeout, retry, row limit, and EXPLAIN logging.

    - Up to MAX_RETRIES retries on OperationalError
    - Fetches at most ROW_LIMIT rows (warns on truncation)
    - Auto-runs EXPLAIN for queries that take > SLOW_QUERY_THRESHOLD seconds
    """
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        conn = None
        try:
            conn = get_connection()

            with conn.cursor() as cursor:
                start = time.time()
                cursor.execute(sql)
                elapsed = time.time() - start

                # Fetch with limit
                rows = cursor.fetchmany(ROW_LIMIT + 1)

                if len(rows) > ROW_LIMIT:
                    rows = rows[:ROW_LIMIT]
                    print(
                        f"[executor] ⚠️ Result set exceeded {ROW_LIMIT} rows — "
                        f"output truncated to {ROW_LIMIT} rows.",
                        file=sys.stderr,
                    )

                # Auto-EXPLAIN for slow queries
                if elapsed > SLOW_QUERY_THRESHOLD:
                    try:
                        cursor.execute(f"EXPLAIN {sql}")
                        explain_rows = cursor.fetchall()
                        print(
                            f"[executor] ⚠️ Slow query ({elapsed:.2f}s). EXPLAIN output:",
                            file=sys.stderr,
                        )
                        for row in explain_rows:
                            print(f"  {row}", file=sys.stderr)
                    except Exception as ex:
                        print(
                            f"[executor] Could not run EXPLAIN: {ex}",
                            file=sys.stderr,
                        )

                return rows

        except pymysql.err.OperationalError as e:
            last_error = e
            print(
                f"[executor] OperationalError on attempt {attempt + 1}/{MAX_RETRIES + 1}: {e}",
                file=sys.stderr,
            )
            if attempt < MAX_RETRIES:
                time.sleep(1)  # brief pause before retry
                continue
            raise

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    # Should not reach here, but just in case
    raise last_error  # type: ignore[misc]