def validate_sql(sql):
    """Validate SQL for safety — blocks dangerous operations, enforces best practices."""

    sql_upper = sql.upper().strip()

    # 1. Block dangerous keywords
    forbidden = ["DELETE", "UPDATE", "DROP", "ALTER", "INSERT", "TRUNCATE", "GRANT", "REVOKE"]
    for word in forbidden:
        # Match whole words to avoid false positives (e.g. "updated_at" matching "UPDATE")
        import re
        if re.search(r'\b' + word + r'\b', sql_upper):
            raise Exception(f"Unsafe SQL detected: {word} is not allowed")

    # 2. Must be a SELECT query
    if not sql_upper.startswith("SELECT"):
        raise Exception("Only SELECT queries are allowed")

    # 3. Block password columns
    password_patterns = [
        r'\bpassword\b',
        r'\bauthdata\b',
        r'\bcardnum\b',
        r'\bsecurityqans\b',
    ]
    import re
    for pattern in password_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            raise Exception(f"Selecting sensitive columns is not allowed: {pattern}")

    # 4. Warn if no LIMIT clause (add one automatically)
    if "LIMIT" not in sql_upper:
        return sql.rstrip().rstrip(";") + " LIMIT 500;"

    # 5. Basic SQL injection patterns
    injection_patterns = [
        r";\s*SELECT",       # stacked queries
        r"UNION\s+SELECT",   # union injection
        r"--\s",             # comment injection
        r"/\*",              # block comment injection
        r"SLEEP\s*\(",       # time-based injection
        r"BENCHMARK\s*\(",   # benchmark injection
        r"LOAD_FILE\s*\(",   # file read injection
        r"INTO\s+OUTFILE",   # file write injection
        r"INTO\s+DUMPFILE",  # file dump injection
    ]
    for pattern in injection_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            raise Exception(f"Potential SQL injection detected")

    return sql