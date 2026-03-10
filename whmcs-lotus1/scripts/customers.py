"""
WHMCS Customers — Customer-specific queries
"""

from db import query_raw


def top_hosting_buyers(limit=10):
    """Customers who bought the most hosting services."""
    sql = """
    SELECT
        c.id,
        CONCAT(c.firstname, ' ', c.lastname) AS customer,
        c.email,
        c.companyname,
        COUNT(h.id) AS hosting_count
    FROM tblclients c
    JOIN tblhosting h ON c.id = h.userid
    GROUP BY c.id, c.firstname, c.lastname, c.email, c.companyname
    ORDER BY hosting_count DESC
    LIMIT %s
    """
    return query_raw(sql, params=(int(limit),))


def customer_detail(client_id):
    """Full detail of a customer: profile + hosting + domains + invoices."""
    profile = query_raw(
        """
        SELECT id, firstname, lastname, companyname, email, phonenumber,
               address1, city, state, postcode, country, status, datecreated
        FROM tblclients WHERE id = %s
        """,
        params=(int(client_id),),
    )

    hosting = query_raw(
        """
        SELECT h.id, h.domain, p.name AS product, h.domainstatus AS status,
               h.regdate, h.nextduedate, h.amount
        FROM tblhosting h
        LEFT JOIN tblproducts p ON h.packageid = p.id
        WHERE h.userid = %s
        ORDER BY h.regdate DESC
        """,
        params=(int(client_id),),
    )

    domains = query_raw(
        """
        SELECT id, domain, status, registrationdate, expirydate, registrar
        FROM tbldomains WHERE userid = %s
        ORDER BY expirydate DESC
        """,
        params=(int(client_id),),
    )

    invoices = query_raw(
        """
        SELECT id, invoicenum, date, duedate, total, status
        FROM tblinvoices WHERE userid = %s
        ORDER BY date DESC LIMIT 20
        """,
        params=(int(client_id),),
    )

    return {
        "profile": profile[0] if profile else None,
        "hosting": hosting,
        "domains": domains,
        "recent_invoices": invoices,
    }


def customer_search(keyword):
    """Search customers by name, email, or company name."""
    like = f"%{keyword}%"
    sql = """
    SELECT id, firstname, lastname, companyname, email, status, datecreated
    FROM tblclients
    WHERE firstname LIKE %s OR lastname LIKE %s 
          OR email LIKE %s OR companyname LIKE %s
    ORDER BY id DESC
    LIMIT 50
    """
    return query_raw(sql, params=(like, like, like, like))