"""
WHMCS Analytics — General analytics and reporting queries
"""

from db import query_raw


def top_customers(limit=10):
    """Top customers by number of hosting services purchased."""
    sql = """
    SELECT
        c.id,
        CONCAT(c.firstname, ' ', c.lastname) AS customer,
        c.email,
        COUNT(h.id) AS total_orders
    FROM tblclients c
    JOIN tblhosting h ON c.id = h.userid
    GROUP BY c.id, c.firstname, c.lastname, c.email
    ORDER BY total_orders DESC
    LIMIT %s
    """
    return query_raw(sql, params=(int(limit),))


def unpaid_orders():
    """Customers with unpaid invoices and total unpaid amount."""
    sql = """
    SELECT
        c.id,
        CONCAT(c.firstname, ' ', c.lastname) AS customer,
        c.email,
        COUNT(i.id) AS unpaid_invoices,
        SUM(i.total) AS total_unpaid
    FROM tblclients c
    JOIN tblinvoices i ON c.id = i.userid
    WHERE i.status = 'Unpaid'
    GROUP BY c.id, c.firstname, c.lastname, c.email
    ORDER BY total_unpaid DESC
    """
    return query_raw(sql)


def inactive_customers(year=2025):
    """Customers whose last hosting order was before the given year."""
    sql = """
    SELECT
        c.id,
        CONCAT(c.firstname, ' ', c.lastname) AS customer,
        c.email,
        MAX(h.regdate) AS last_order
    FROM tblclients c
    JOIN tblhosting h ON c.id = h.userid
    GROUP BY c.id, c.firstname, c.lastname, c.email
    HAVING last_order < %s
    ORDER BY last_order DESC
    """
    cutoff = f"{int(year)}-01-01"
    return query_raw(sql, params=(cutoff,))


def revenue_summary():
    """Revenue summary — total, paid, unpaid, cancelled."""
    sql = """
    SELECT
        i.status,
        COUNT(i.id) AS invoice_count,
        COALESCE(SUM(i.total), 0) AS total_amount
    FROM tblinvoices i
    GROUP BY i.status
    ORDER BY total_amount DESC
    """
    return query_raw(sql)


def product_sales():
    """Top selling products by number of hosting subscriptions."""
    sql = """
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        pg.name AS product_group,
        COUNT(h.id) AS total_sold,
        SUM(CASE WHEN h.domainstatus = 'Active' THEN 1 ELSE 0 END) AS active_count
    FROM tblproducts p
    LEFT JOIN tblproductgroups pg ON p.gid = pg.id
    LEFT JOIN tblhosting h ON h.packageid = p.id
    GROUP BY p.id, p.name, pg.name
    ORDER BY total_sold DESC
    """
    return query_raw(sql)