# Available Tools

List all tools: `python scripts/run.py --list`

## Predefined Analytics Tools

### Analytics
| Tool | Args | Description |
|------|------|-------------|
| `top_customers` | `[limit=10]` | Top N customers by hosting orders |
| `unpaid_orders` | — | Customers with unpaid invoices + total unpaid amount |
| `inactive_customers` | `[year=2025]` | Customers whose last order was before the given year |
| `revenue_summary` | — | Revenue totals grouped by invoice status |
| `product_sales` | — | Product sales breakdown with active counts |

### Customers
| Tool | Args | Description |
|------|------|-------------|
| `top_hosting_buyers` | `[limit=10]` | Top N hosting buyers |
| `customer_detail` | `client_id` (**required**) | Full profile: info + hosting + domains + invoices |
| `customer_search` | `keyword` (**required**) | Search by name, email, or company |

### Domains
| Tool | Args | Description |
|------|------|-------------|
| `domain_stats` | — | Total and active domain counts |
| `expiring_domains` | `[days=30]` | Domains expiring within N days |

### Hosting
| Tool | Args | Description |
|------|------|-------------|
| `hosting_stats` | — | Total and active hosting counts |
| `hosting_by_product` | — | Hosting grouped by product with status breakdown |

### Invoices
| Tool | Args | Description |
|------|------|-------------|
| `invoice_summary` | — | Invoice counts and totals by status |
| `overdue_invoices` | — | Unpaid invoices past due date with days overdue |

## Dynamic Query Tool

| Tool | Args | Description |
|------|------|-------------|
| `execute_query` | `sql` (**required**), `[limit]` | Execute any SELECT query against WHMCS DB |

### Safety
- **Read-only**: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE are blocked
- **Row limit**: Default max 200 rows per query
- **Timeout**: Connection 10s, read 30s