"""
WHMCS Insight Query — CLI Entry Point

Usage:
    # Run a predefined query
    python run.py CUSTOMER_TOP_SPENDERS
    python run.py TOP_PACKAGES

    # Route from natural language question
    python run.py --ask "ลูกค้าที่ใช้จ่ายมากสุด"

    # Execute custom SQL (read-only)
    python run.py --sql "SELECT COUNT(*) AS total FROM tblclients"

    # List all available queries
    python run.py --list
    python run.py --list --category revenue

    # Get table schema
    python run.py --schema tblclients

    # Output format
    python run.py TOP_PACKAGES --format table
    python run.py TOP_PACKAGES --format json
    python run.py TOP_PACKAGES --format csv
"""

import json
import sys
import os
import argparse
import datetime
import subprocess

# Add script directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import query, query_raw, get_table_schema
from queries import QUERIES, route_question, list_queries

# --- Tabulate (optional, fallback to JSON) ---
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def json_serial(obj):
    """JSON serializer for non-standard types."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, datetime.timedelta):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if hasattr(obj, '__float__'):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def format_output(result, fmt="json"):
    """Format query result for output."""
    if "error" in result:
        return json.dumps(result, indent=2, ensure_ascii=False)

    data = result.get("data", result) if isinstance(result, dict) else result

    if fmt == "json":
        output = result if isinstance(result, dict) else {"data": result}
        return json.dumps(output, indent=2, default=json_serial, ensure_ascii=False)

    elif fmt == "table" and HAS_TABULATE:
        if not data:
            return "(no results)"
        return tabulate(data, headers="keys", tablefmt="grid")

    elif fmt == "csv":
        if not data:
            return ""
        import csv
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return buf.getvalue()

    else:
        return json.dumps(result, indent=2, default=json_serial, ensure_ascii=False)


def run_named_query(name, fmt="json"):
    """Run a predefined query by name."""
    if name not in QUERIES:
        return json.dumps({
            "error": f"Unknown query: {name}",
            "available": sorted(QUERIES.keys()),
        }, indent=2, ensure_ascii=False)

    q = QUERIES[name]
    result = query(q["sql"], q.get("params"))
    print(f"# {q['description']}", file=sys.stderr)
    return format_output(result, fmt)


def run_custom_sql(sql, fmt="json"):
    """Run a custom SQL query."""
    result = query(sql)
    return format_output(result, fmt)


def main():
    parser = argparse.ArgumentParser(
        description="WHMCS Insight Query Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py CUSTOMER_TOP_SPENDERS
  python run.py --ask "ใครใช้จ่ายมากสุด"
  python run.py --sql "SELECT COUNT(*) FROM tblclients"
  python run.py --list --category revenue
  python run.py --schema tblhosting
  python run.py TOP_PACKAGES --format table
        """,
    )

    parser.add_argument("query_name", nargs="?", help="Predefined query name to run")
    parser.add_argument("--ask", type=str, help="Natural language question (Thai/English)")
    parser.add_argument("--sql", type=str, help="Custom SQL query (SELECT only)")
    parser.add_argument("--list", action="store_true", help="List all available queries")
    parser.add_argument("--category", type=str, help="Filter queries by category")
    parser.add_argument("--schema", type=str, help="Get table schema")
    parser.add_argument("--format", type=str, default="json",
                        choices=["json", "table", "csv"], help="Output format")

    args = parser.parse_args()

    # --- List mode ---
    if args.list:
        queries = list_queries(args.category)
        if args.format == "table" and HAS_TABULATE:
            rows = [{"name": k, **v} for k, v in queries.items()]
            print(tabulate(rows, headers="keys", tablefmt="grid"))
        else:
            print(json.dumps(queries, indent=2, ensure_ascii=False))
        return

    # --- Schema mode ---
    if args.schema:
        result = get_table_schema(args.schema)
        print(json.dumps(result, indent=2, default=json_serial, ensure_ascii=False))
        return

    # --- Natural language question ---
    if args.ask:
        matched = route_question(args.ask)
        if matched:
            print(f"# Matched: {matched}", file=sys.stderr)
            print(run_named_query(matched, args.format))
        else:
            print(json.dumps({
                "error": "ไม่พบ query ที่ตรงกับคำถาม",
                "question": args.ask,
                "hint": "ลองใช้ --list เพื่อดู query ที่มี หรือใช้ --sql สำหรับ custom query",
            }, indent=2, ensure_ascii=False))
        return

    # --- Custom SQL ---
    if args.sql:
        print(run_custom_sql(args.sql, args.format))
        return

    # --- Named query ---
    if args.query_name:
        print(run_named_query(args.query_name, args.format))
        return

    # --- No args ---
    parser.print_help()


if __name__ == "__main__":
    main()