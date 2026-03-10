"""
WHMCS Hosting — Hosting service queries
"""

from db import query_raw


def hosting_stats():
    """Total hosting services and active count."""
    total = query_raw("SELECT COUNT(*) AS total FROM tblhosting")
    active = query_raw(
        "SELECT COUNT(*) AS active FROM tblhosting WHERE domainstatus = 'Active'"
    )
    return {
        "total_hosting": total[0]["total"] if total else 0,
        "active_hosting": active[0]["active"] if active else 0,
    }


def hosting_by_product():
    """Hosting breakdown by product — total, active, suspended."""
    sql = """
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        pg.name AS product_group,
        COUNT(h.id) AS total,
        SUM(CASE WHEN h.domainstatus = 'Active' THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN h.domainstatus = 'Suspended' THEN 1 ELSE 0 END) AS suspended,
        SUM(CASE WHEN h.domainstatus = 'Terminated' THEN 1 ELSE 0 END) AS terminated
    FROM tblhosting h
    JOIN tblproducts p ON h.packageid = p.id
    LEFT JOIN tblproductgroups pg ON p.gid = pg.id
    GROUP BY p.id, p.name, pg.name
    ORDER BY total DESC
    """
    return query_raw(sql)
