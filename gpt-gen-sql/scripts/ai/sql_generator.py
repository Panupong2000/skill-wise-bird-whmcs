import openai
import json
import re
import sys

# ---------------------------------------------------------------------------
# Load schema (structured format with nested "columns" dicts)
# ---------------------------------------------------------------------------
with open("schema/schema.json", "r", encoding="utf-8") as _f:
    SCHEMA: dict = json.load(_f)

# Pre-compute lookup sets for fast validation
VALID_TABLES = set(SCHEMA.keys())
VALID_COLUMNS = {
    table: set(info["columns"].keys()) for table, info in SCHEMA.items()
}
ALL_COLUMNS = set()
for cols in VALID_COLUMNS.values():
    ALL_COLUMNS |= cols

# ---------------------------------------------------------------------------
# Load prompts
# ---------------------------------------------------------------------------
with open("prompts/system_prompt.md", "r", encoding="utf-8") as _f:
    SYSTEM_PROMPT = _f.read()

with open("prompts/sql_rules.md", "r", encoding="utf-8") as _f:
    SQL_RULES = _f.read()

MAX_RETRIES = 2  # max retry attempts (so up to 3 total calls)


# ---------------------------------------------------------------------------
# Schema validation helpers
# ---------------------------------------------------------------------------

# Regex patterns to extract table references (after FROM / JOIN)
_TABLE_RE = re.compile(
    r'\b(?:FROM|JOIN)\s+`?(\w+)`?', re.IGNORECASE
)

# Regex to extract column references — simplified but effective for WHMCS queries
# Matches: table.column, or standalone column in SELECT/WHERE/ON/ORDER BY/GROUP BY
_QUALIFIED_COL_RE = re.compile(
    r'\b`?(\w+)`?\s*\.\s*`?(\w+)`?', re.IGNORECASE
)


def _extract_table_names(sql: str) -> set[str]:
    """Extract table names referenced in SQL (after FROM/JOIN)."""
    # Also strip aliases — take only the first word after FROM/JOIN
    return {m.group(1).lower() for m in _TABLE_RE.finditer(sql)}


def _extract_qualified_columns(sql: str) -> list[tuple[str, str]]:
    """Extract (table, column) pairs from table.column references."""
    return [(m.group(1).lower(), m.group(2).lower()) for m in _QUALIFIED_COL_RE.finditer(sql)]


def validate_schema_references(sql):
    """
    Check every table and qualified column in the SQL against the schema.
    Returns a list of error descriptions (empty = valid).
    """
    errors = []

    # Check tables
    for table in _extract_table_names(sql):
        if table.lower() not in {t.lower() for t in VALID_TABLES}:
            errors.append(f"Unknown table: {table}")

    # Check qualified columns (table.column)
    valid_tables_lower = {t.lower(): t for t in VALID_TABLES}
    for table, column in _extract_qualified_columns(sql):
        if table in valid_tables_lower:
            real_table = valid_tables_lower[table]
            if column.lower() not in {c.lower() for c in VALID_COLUMNS[real_table]}:
                errors.append(f"Unknown column: {table}.{column}")
        # If table itself is unknown, it was already caught above

    return errors


# ---------------------------------------------------------------------------
# SQL generation with anti-hallucination retry
# ---------------------------------------------------------------------------

class SchemaValidationError(Exception):
    """Raised when generated SQL references unknown tables/columns after retries."""
    pass


def generate_sql(question):
    """
    Generate SQL from a natural-language question.
    Validates schema references and retries up to MAX_RETRIES times with
    correction hints if unknown tables/columns are found.
    """
    schema_context = json.dumps(SCHEMA, indent=2)
    correction_hint = ""

    for attempt in range(MAX_RETRIES + 1):
        user_content = f"""Database schema:

{schema_context}

{SQL_RULES}

{correction_hint}

Convert this question into SQL:

{question}

Return only SQL."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
        )

        sql = response.choices[0].message.content.strip()

        # Strip markdown code fences if the model wraps the SQL
        if sql.startswith("```"):
            sql = re.sub(r"^```(?:sql)?\s*", "", sql)
            sql = re.sub(r"\s*```$", "", sql)

        # Validate against schema
        errors = validate_schema_references(sql)

        if not errors:
            return sql

        # Build correction hint for next attempt
        error_list = "; ".join(errors)
        correction_hint = (
            f"⚠️ CORRECTION: Your previous SQL had errors: {error_list}. "
            f"Use ONLY tables and columns from the provided schema. "
            f"Valid tables are: {', '.join(sorted(VALID_TABLES))}."
        )

        print(
            f"[sql_generator] Attempt {attempt + 1}/{MAX_RETRIES + 1} — "
            f"schema errors: {error_list}",
            file=sys.stderr,
        )

    # All retries exhausted
    raise SchemaValidationError(
        f"Failed to generate valid SQL after {MAX_RETRIES + 1} attempts. "
        f"Last errors: {error_list}"
    )