"""
WHMCS Skill — Tool Dispatcher
Run predefined analytics tools or execute dynamic SQL queries.

Usage:
    python run.py <tool_name> [args...]
    python run.py execute_query "SELECT ..."
    python run.py top_customers 20
"""

import json
import sys
import os
import datetime

# Add script directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics import (
    top_customers,
    unpaid_orders,
    inactive_customers,
    revenue_summary,
    product_sales,
)
from customers import top_hosting_buyers, customer_detail, customer_search
from domains import domain_stats, expiring_domains
from hosting import hosting_stats, hosting_by_product
from invoices import invoice_summary, overdue_invoices
from query_executor import execute_query


# Tool registry: name -> (function, arg_names, description)
TOOLS = {
    # Analytics
    "top_customers": (top_customers, ["limit"], "Top N customers by hosting orders"),
    "unpaid_orders": (unpaid_orders, [], "Customers with unpaid invoices"),
    "inactive_customers": (inactive_customers, ["year"], "Customers inactive since year"),
    "revenue_summary": (revenue_summary, [], "Revenue by invoice status"),
    "product_sales": (product_sales, [], "Product sales breakdown"),
    # Customers
    "top_hosting_buyers": (top_hosting_buyers, ["limit"], "Top N hosting buyers"),
    "customer_detail": (customer_detail, ["client_id"], "Full customer profile"),
    "customer_search": (customer_search, ["keyword"], "Search customers by name/email"),
    # Domains
    "domain_stats": (domain_stats, [], "Domain counts (total/active)"),
    "expiring_domains": (expiring_domains, ["days"], "Domains expiring in N days"),
    # Hosting
    "hosting_stats": (hosting_stats, [], "Hosting counts (total/active)"),
    "hosting_by_product": (hosting_by_product, [], "Hosting grouped by product"),
    # Invoices
    "invoice_summary": (invoice_summary, [], "Invoice totals by status"),
    "overdue_invoices": (overdue_invoices, [], "Overdue unpaid invoices"),
    # Dynamic
    "execute_query": (execute_query, ["sql", "limit"], "Execute a custom SELECT query"),
}


def json_serial(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, datetime.timedelta):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    raise TypeError(f"Type {type(obj)} not serializable")


def main():
    if len(sys.argv) < 2:
        tools_list = {name: desc for name, (_, _, desc) in TOOLS.items()}
        print(json.dumps({"error": "No tool specified", "available_tools": tools_list}, indent=2))
        return

    tool_name = sys.argv[1]

    if tool_name == "--list":
        tools_list = {}
        for name, (_, args, desc) in TOOLS.items():
            tools_list[name] = {"description": desc, "args": args}
        print(json.dumps(tools_list, indent=2))
        return

    if tool_name not in TOOLS:
        print(json.dumps({"error": f"Unknown tool: {tool_name}", "available": list(TOOLS.keys())}))
        return

    func, arg_names, _ = TOOLS[tool_name]
    args = sys.argv[2:]

    try:
        # Build kwargs from positional args
        kwargs = {}
        for i, arg_name in enumerate(arg_names):
            if i < len(args):
                kwargs[arg_name] = args[i]

        result = func(**kwargs)
        print(json.dumps(result, indent=2, default=json_serial, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e), "tool": tool_name}))


if __name__ == "__main__":
    main()