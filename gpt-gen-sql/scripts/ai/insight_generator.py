import openai
import re

# ---------------------------------------------------------------------------
# Query type detection
# ---------------------------------------------------------------------------

_QUERY_TYPE_RULES = [
    ("revenue",   [r"\btblinvoices\b.*\b(datepaid|total|subtotal)\b",
                   r"\btbltransactions\b.*\bamountin\b"]),
    ("churn",     [r"\bdomainstatus\b.*\b(Suspended|Terminated)\b",
                   r"\bdomainstatus\b"]),
    ("support",   [r"\btbltickets\b"]),
    ("domains",   [r"\btbldomains\b"]),
    ("customers", [r"\btblclients\b"]),
]


def detect_query_type(sql):
    """Detect the business query type from the SQL statement.

    Returns one of: revenue, churn, support, domains, customers, general.
    """
    sql_lower = sql.lower()
    for qtype, patterns in _QUERY_TYPE_RULES:
        for pattern in patterns:
            if re.search(pattern, sql_lower, re.IGNORECASE | re.DOTALL):
                return qtype
    return "general"


# ---------------------------------------------------------------------------
# Language detection (Thai / English)
# ---------------------------------------------------------------------------

def _detect_language(text):
    """Simple detection: if text contains Thai characters → 'th', else 'en'."""
    for ch in text:
        if "\u0e01" <= ch <= "\u0e5b":  # Thai Unicode block
            return "th"
    return "en"


# ---------------------------------------------------------------------------
# Type-specific insight context builders
# ---------------------------------------------------------------------------

def _revenue_context(sql, results):
    has_datepaid = any("datepaid" in str(r) for r in results) or "datepaid" in sql.lower()
    hint = ""
    if has_datepaid:
        hint = (
            "If datepaid values span multiple months, compare month-over-month (MoM) revenue "
            "and highlight the trend (growing / declining / stable)."
        )
    return (
        "This is a REVENUE query. Focus on: total revenue figures, payment trends, "
        "and outstanding amounts. " + hint
    )


def _churn_context(sql, results):
    # Try to detect suspended vs active counts for the flag
    active_count = 0
    suspended_count = 0
    for row in results:
        for key, val in row.items():
            key_lower = key.lower()
            if "active" in key_lower and isinstance(val, (int, float)):
                active_count = int(val)
            if ("suspend" in key_lower or "churned" in key_lower or "terminated" in key_lower) and isinstance(val, (int, float)):
                suspended_count += int(val)

    flag = ""
    if active_count > 0 and suspended_count > active_count * 0.1:
        flag = (
            f"⚠️ ALERT: Suspended/terminated count ({suspended_count}) exceeds 10% of "
            f"active count ({active_count}). This is a significant churn signal."
        )

    return (
        "This is a CHURN analysis query. Focus on: churn rate, at-risk services, "
        "suspension reasons if available. " + flag
    )


def _support_context(sql, results):
    return (
        "This is a SUPPORT/TICKETS query. Focus on: ticket volume trends, "
        "response times, open vs resolved ratios, and any priority escalation patterns."
    )


def _domains_context(sql, results):
    # Flag donotrenew domains separately
    donotrenew_count = sum(
        1 for r in results
        if r.get("donotrenew") == 1 or r.get("donotrenew") == "1"
    )
    flag = ""
    if donotrenew_count > 0:
        flag = (
            f"⚠️ NOTE: {donotrenew_count} domain(s) are marked as 'Do Not Renew' — "
            f"these represent confirmed churn intent and should be highlighted separately."
        )

    return (
        "This is a DOMAINS query. Focus on: expiring domains, renewal status, "
        "registration trends, and TLD distribution. " + flag
    )


def _customers_context(sql, results):
    return (
        "This is a CUSTOMERS query. Focus on: customer growth, acquisition trends, "
        "geographic distribution, and account status breakdown."
    )


_CONTEXT_BUILDERS = {
    "revenue":   _revenue_context,
    "churn":     _churn_context,
    "support":   _support_context,
    "domains":   _domains_context,
    "customers": _customers_context,
}


# ---------------------------------------------------------------------------
# Main insight generator
# ---------------------------------------------------------------------------

def generate_insight(sql, results, question):
    """Generate a concise, business-specific WHMCS insight from query results.

    Args:
        sql: The SQL that was executed.
        results: List of row dicts from the query.
        question: The original natural-language question.

    Returns:
        A business insight string (max ~150 words).
    """
    query_type = detect_query_type(sql)
    lang = _detect_language(question)

    # Build type-specific context
    context_builder = _CONTEXT_BUILDERS.get(query_type)
    type_context = context_builder(sql, results) if context_builder else ""

    # Language instruction
    lang_instruction = (
        "ตอบเป็นภาษาไทย (Answer in Thai)." if lang == "th"
        else "Answer in English."
    )

    # Truncate results for the prompt to avoid token overflow
    result_preview = results[:20]  # max 20 rows for context

    prompt = f"""{lang_instruction}

You are a WHMCS business analyst. Given the SQL query, its results, and the original question, provide a concise business insight.

{type_context}

Rules:
- Keep your response under 150 words
- Be specific with numbers from the results
- Highlight any anomalies or actionable recommendations
- Do NOT repeat the SQL or raw data — interpret the results
- When presenting data as a table, use proper markdown table format:
  - Use `:---:` for center-aligned columns (e.g. rank/order)
  - Use `---:` for right-aligned columns (e.g. numbers/amounts)
  - Use `:---` for left-aligned columns (e.g. names/text)
  - Format numbers with commas (e.g. 2,616)
  - Example:
    | อันดับ | ชื่อ | จำนวน |
    | :---: | :--- | ---: |
    | 1 | Product A | 2,616 ราย |

Original question: {question}

SQL executed:
{sql}

Query results (up to 20 rows):
{result_preview}

Provide your business insight:"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()
