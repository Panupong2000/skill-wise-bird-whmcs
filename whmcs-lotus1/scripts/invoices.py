"""
WHMCS Invoices — Invoice and billing queries
"""

from db import query_raw


def invoice_summary():
    """Invoice counts and totals grouped by status."""
    sql = """
    SELECT
        status,
        COUNT(id) AS invoice_count,
        COALESCE(SUM(total), 0) AS total_amount,
        COALESCE(SUM(subtotal), 0) AS subtotal,
        COALESCE(SUM(credit), 0) AS total_credit
    FROM tblinvoices
    GROUP BY status
    ORDER BY total_amount DESC
    """
    return query_raw(sql)


def overdue_invoices():
    """Unpaid invoices that are past due date."""
    sql = """
    SELECT
        i.id AS invoice_id,
        i.invoicenum,
        CONCAT(c.firstname, ' ', c.lastname) AS customer,
        c.email,
        i.date AS invoice_date,
        i.duedate,
        i.total,
        DATEDIFF(CURDATE(), i.duedate) AS days_overdue
    FROM tblinvoices i
    JOIN tblclients c ON i.userid = c.id
    WHERE i.status = 'Unpaid' AND i.duedate < CURDATE()
    ORDER BY days_overdue DESC
    """
    return query_raw(sql)
