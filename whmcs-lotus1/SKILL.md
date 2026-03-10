---
name: whmcs-analytics
description: Use this skill whenever the user asks about customers, hosting services, domains, invoices, product sales, revenue, or any WHMCS analytics. This skill can run predefined analytics tools AND generate custom SQL queries against the WHMCS database.
---

# WHMCS Analytics Skill

This skill connects to a WHMCS MySQL database and provides two modes of operation:

## Mode 1: Predefined Tools (ใช้สำหรับคำถามทั่วไป)

Run predefined tools for common analytics questions:

```bash
python scripts/run.py <tool_name> [args...]
```

### Available Tools

| Tool | Args | Description |
|------|------|-------------|
| `top_customers` | `[limit]` | Top N customers by hosting orders |
| `unpaid_orders` | — | Customers with unpaid invoices + amounts |
| `inactive_customers` | `[year]` | Customers inactive since specified year |
| `revenue_summary` | — | Revenue totals by invoice status |
| `product_sales` | — | Product sales breakdown |
| `top_hosting_buyers` | `[limit]` | Top N hosting buyers |
| `customer_detail` | `client_id` | Full customer profile + hosting/domains/invoices |
| `customer_search` | `keyword` | Search customers by name/email/company |
| `domain_stats` | — | Domain counts (total/active) |
| `expiring_domains` | `[days]` | Domains expiring within N days |
| `hosting_stats` | — | Hosting counts (total/active) |
| `hosting_by_product` | — | Hosting grouped by product |
| `invoice_summary` | — | Invoice totals by status |
| `overdue_invoices` | — | Overdue unpaid invoices |

### Examples

```bash
python scripts/run.py top_customers 20
python scripts/run.py inactive_customers 2024
python scripts/run.py customer_detail 42
python scripts/run.py customer_search "john"
python scripts/run.py expiring_domains 60
```

---

## Mode 2: Dynamic SQL Query (ใช้สำหรับคำถามซับซ้อน)

When predefined tools don't cover the question, generate and execute custom SQL:

```bash
python scripts/run.py execute_query "SELECT ..."
```

### Rules for Generating SQL

1. **SELECT only** — INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE are blocked
2. **Use table/column names from the schema** — see reference.md for full details
3. **Always use JOINs** — follow the relationships defined in reference.md
4. **Limit results** — add LIMIT clause for large tables, default cap is 200 rows
5. **Use aliases** — make column names readable (AS customer_name, AS total_orders)

### WHMCS Schema Quick Reference

**Core Tables & Relationships:**

```
tblclients (id, firstname, lastname, email, companyname, status, datecreated)
    ├── tblhosting (userid → tblclients.id)
    │     └── tblproducts (packageid → tblproducts.id)
    │           └── tblproductgroups (gid → tblproductgroups.id)
    ├── tbldomains (userid → tblclients.id)
    └── tblinvoices (userid → tblclients.id)
          └── tblinvoiceitems (invoiceid → tblinvoices.id)
```

**Key Status Values:**
- `tblhosting.domainstatus`: Active, Suspended, Terminated, Pending, Cancelled
- `tbldomains.status`: Active, Pending, Expired, Cancelled
- `tblinvoices.status`: Paid, Unpaid, Cancelled, Refunded, Collections
- `tblclients.status`: Active, Inactive, Closed

### Example Dynamic Queries

```bash
# Monthly revenue for 2025
python scripts/run.py execute_query "SELECT DATE_FORMAT(datepaid, '%Y-%m') AS month, SUM(total) AS revenue FROM tblinvoices WHERE status='Paid' AND YEAR(datepaid)=2025 GROUP BY month ORDER BY month"

# Customers with both hosting and domains
python scripts/run.py execute_query "SELECT c.id, CONCAT(c.firstname,' ',c.lastname) AS customer, COUNT(DISTINCT h.id) AS hosting, COUNT(DISTINCT d.id) AS domains FROM tblclients c JOIN tblhosting h ON c.id=h.userid JOIN tbldomains d ON c.id=d.userid GROUP BY c.id ORDER BY hosting DESC LIMIT 20"
```

---

## Sandbox Rules

The execute-code sandbox runs at `/app/` which is a **read-only filesystem**, so:

1. **Always write scripts to `/tmp/` first** — copy content from the scripts directory
2. **Scripts have DB values ready to use** — the system injects values from Configuration automatically
3. **Run scripts from `/tmp/`** — never use path `scripts/` or `/app/`

## Full Schema Reference

For detailed column names, types, and relationships, see `reference.md`.