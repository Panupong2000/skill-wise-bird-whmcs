"""
WHMCS Domains — Domain-specific queries
"""

from db import query_raw


def domain_stats():
    """Total domains and active domains count."""
    total = query_raw("SELECT COUNT(*) AS total FROM tbldomains")
    active = query_raw(
        "SELECT COUNT(*) AS active FROM tbldomains WHERE status = 'Active'"
    )
    return {
        "total_domains": total[0]["total"] if total else 0,
        "active_domains": active[0]["active"] if active else 0,
    }


def expiring_domains(days=30):
    """Domains expiring within the next N days."""
    sql = """
    SELECT
        d.id,
        d.domain,
        d.expirydate,
        d.status,
        d.registrar,
        CONCAT(c.firstname, ' ', c.lastname) AS customer,
        c.email
    FROM tbldomains d
    JOIN tblclients c ON d.userid = c.id
    WHERE d.expirydate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
      AND d.status = 'Active'
    ORDER BY d.expirydate ASC
    """
    return query_raw(sql, params=(int(days),))