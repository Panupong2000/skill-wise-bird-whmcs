"""
WHMCS Insight Queries
All SQL queries organized by category, matching the 31 insight questions.

Each query is a dict with:
  - sql: the SQL string (may contain %s placeholders)
  - params: default param values (or None)
  - description: Thai + English description
  - category: question category tag

Usage:
  from queries import QUERIES
  q = QUERIES["CUSTOMER_TOP_SPENDERS"]
  result = db.query(q["sql"], q.get("params"))
"""

# =============================================================================
# 🔍 DOMAIN & SERVICE ANALYSIS (Questions 1–4)
# =============================================================================

DOMAIN_MULTI_NO_MULTISERVER = {
    "description": "ลูกค้าที่มีหลายโดเมนแต่ใช้ hosting/VPS เดียว (Multi-domain, single server)",
    "category": "domain_service",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        COUNT(DISTINCT d.id) AS domain_count,
        COUNT(DISTINCT h.id) AS hosting_count
    FROM tblclients c
    JOIN tbldomains d ON d.userid = c.id AND d.status = 'Active'
    LEFT JOIN tblhosting h ON h.userid = c.id AND h.domainstatus = 'Active'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING domain_count > 1 AND hosting_count <= 1
    ORDER BY domain_count DESC
    LIMIT 100
    """,
    "params": None,
}

TRAFFIC_GROWTH_30PCT = {
    "description": "ลูกค้าที่ Traffic โตเกิน 30% — ดูจาก bwusage ใน tblhosting",
    "category": "domain_service",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        h.id AS hosting_id,
        h.domain,
        h.bwusage,
        h.bwlimit,
        ROUND(h.bwusage / NULLIF(h.bwlimit, 0) * 100, 1) AS bw_usage_pct
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    WHERE h.domainstatus = 'Active'
      AND h.bwlimit > 0
      AND h.bwusage > 0
    ORDER BY bw_usage_pct DESC
    LIMIT 100
    """,
    "params": None,
}

HOSTING_SHARED_VPS_CANDIDATE = {
    "description": "ลูกค้าใช้ Shared Hosting แต่ควรอัพเป็น VPS (disk/bw สูง หรือ หลาย domain)",
    "category": "domain_service",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        h.domain,
        p.name AS product_name,
        pg.name AS product_group,
        h.diskusage,
        h.disklimit,
        ROUND(h.diskusage / NULLIF(h.disklimit, 0) * 100, 1) AS disk_pct,
        h.bwusage,
        h.bwlimit,
        ROUND(h.bwusage / NULLIF(h.bwlimit, 0) * 100, 1) AS bw_pct,
        COUNT(DISTINCT d.id) AS domain_count
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    LEFT JOIN tblproductgroups pg ON p.gid = pg.id
    LEFT JOIN tbldomains d ON d.userid = c.id AND d.status = 'Active'
    WHERE h.domainstatus = 'Active'
      AND p.type = 'hostingaccount'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email,
             h.domain, p.name, pg.name, h.diskusage, h.disklimit, h.bwusage, h.bwlimit
    HAVING disk_pct > 70 OR bw_pct > 70 OR domain_count > 3
    ORDER BY disk_pct DESC, bw_pct DESC
    LIMIT 100
    """,
    "params": None,
}

NO_EMAIL_HOSTING = {
    "description": "ลูกค้าที่มี hosting/domain แต่ยังไม่มี Email Hosting",
    "category": "domain_service",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        COUNT(DISTINCT h.id) AS hosting_count,
        COUNT(DISTINCT d.id) AS domain_count
    FROM tblclients c
    LEFT JOIN tblhosting h ON h.userid = c.id AND h.domainstatus = 'Active'
    LEFT JOIN tbldomains d ON d.userid = c.id AND d.status = 'Active'
    WHERE c.status = 'Active'
      AND (h.id IS NOT NULL OR d.id IS NOT NULL)
      AND c.id NOT IN (
          SELECT DISTINCT ii.userid
          FROM tblinvoiceitems ii
          WHERE ii.type = 'Hosting'
            AND ii.description LIKE '%email%'
      )
      AND c.id NOT IN (
          SELECT DISTINCT h2.userid
          FROM tblhosting h2
          JOIN tblproducts p2 ON h2.packageid = p2.id
          JOIN tblproductgroups pg2 ON p2.gid = pg2.id
          WHERE (LOWER(pg2.name) LIKE '%email%' OR LOWER(p2.name) LIKE '%email%')
            AND h2.domainstatus = 'Active'
      )
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    ORDER BY hosting_count DESC
    LIMIT 100
    """,
    "params": None,
}


# =============================================================================
# 💰 REVENUE & SPENDING (Questions 5–10)
# =============================================================================

CUSTOMER_AVG_SPENDING_PER_YEAR = {
    "description": "ลูกค้าเฉลี่ยจ่ายกี่บาทต่อปี (5 ปีย้อนหลัง)",
    "category": "revenue",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        YEAR(i.datepaid) AS pay_year,
        SUM(i.total) AS yearly_total
    FROM tblclients c
    JOIN tblinvoices i ON i.userid = c.id
    WHERE i.status = 'Paid'
      AND i.datepaid >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email, pay_year
    ORDER BY yearly_total DESC
    LIMIT 200
    """,
    "params": None,
}

CUSTOMER_TOP_SPENDERS = {
    "description": "ลูกค้าที่ใช้จ่ายมากสุดต่อปี (Top spenders)",
    "category": "revenue",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        SUM(i.total) AS total_spent,
        COUNT(i.id) AS invoice_count,
        MIN(i.datepaid) AS first_payment,
        MAX(i.datepaid) AS last_payment
    FROM tblclients c
    JOIN tblinvoices i ON i.userid = c.id
    WHERE i.status = 'Paid'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    ORDER BY total_spent DESC
    LIMIT 50
    """,
    "params": None,
}

CUSTOMER_LOWEST_SPENDERS = {
    "description": "ลูกค้าที่ใช้จ่ายน้อยสุดต่อปี (Lowest spenders)",
    "category": "revenue",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        SUM(i.total) AS total_spent,
        COUNT(i.id) AS invoice_count
    FROM tblclients c
    JOIN tblinvoices i ON i.userid = c.id
    WHERE i.status = 'Paid'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING total_spent > 0
    ORDER BY total_spent ASC
    LIMIT 50
    """,
    "params": None,
}

PACKAGE_ORDER_RANKING = {
    "description": "แพ็กเกจที่คนสั่งซื้อน้อยสุด → มากสุด (แยก new vs renewal)",
    "category": "revenue",
    "sql": """
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        pg.name AS product_group,
        COUNT(DISTINCT h.id) AS total_subscriptions,
        SUM(CASE WHEN h.billingcycle != 'Free Account' AND h.firstpaymentamount > 0 THEN 1 ELSE 0 END) AS new_orders,
        SUM(CASE WHEN h.billingcycle != 'Free Account' AND h.firstpaymentamount = 0 THEN 1 ELSE 0 END) AS renewals
    FROM tblproducts p
    LEFT JOIN tblproductgroups pg ON p.gid = pg.id
    LEFT JOIN tblhosting h ON h.packageid = p.id
    GROUP BY p.id, p.name, pg.name
    ORDER BY total_subscriptions ASC
    """,
    "params": None,
}

REVENUE_BY_PACKAGE = {
    "description": "รายได้แยกตามแพ็กเกจ — ลูกค้าใหม่ vs ต่ออายุ",
    "category": "revenue",
    "sql": """
    SELECT
        pg.name AS product_group,
        p.name AS product_name,
        COUNT(DISTINCT ii.userid) AS customer_count,
        SUM(ii.amount) AS total_revenue,
        SUM(CASE
            WHEN ii.description LIKE '%renewal%' OR ii.description LIKE '%ต่ออายุ%'
            THEN ii.amount ELSE 0
        END) AS renewal_revenue,
        SUM(CASE
            WHEN ii.description NOT LIKE '%renewal%' AND ii.description NOT LIKE '%ต่ออายุ%'
            THEN ii.amount ELSE 0
        END) AS new_revenue
    FROM tblinvoiceitems ii
    JOIN tblinvoices i ON ii.invoiceid = i.id
    JOIN tblhosting h ON ii.relid = h.id AND ii.type = 'Hosting'
    JOIN tblproducts p ON h.packageid = p.id
    LEFT JOIN tblproductgroups pg ON p.gid = pg.id
    WHERE i.status = 'Paid'
    GROUP BY pg.name, p.name
    ORDER BY total_revenue DESC
    """,
    "params": None,
}

REVENUE_YOY_COMPARISON = {
    "description": "ยอดขายปีที่แล้ว vs ปีนี้ (% เปลี่ยนแปลง)",
    "category": "revenue",
    "sql": """
    SELECT
        this_year.month,
        this_year.revenue AS revenue_this_year,
        last_year.revenue AS revenue_last_year,
        ROUND(
            (this_year.revenue - COALESCE(last_year.revenue, 0))
            / NULLIF(COALESCE(last_year.revenue, 0), 0) * 100, 1
        ) AS pct_change
    FROM (
        SELECT DATE_FORMAT(datepaid, '%m') AS month, SUM(total) AS revenue
        FROM tblinvoices
        WHERE status = 'Paid' AND YEAR(datepaid) = YEAR(CURDATE())
        GROUP BY month
    ) this_year
    LEFT JOIN (
        SELECT DATE_FORMAT(datepaid, '%m') AS month, SUM(total) AS revenue
        FROM tblinvoices
        WHERE status = 'Paid' AND YEAR(datepaid) = YEAR(CURDATE()) - 1
        GROUP BY month
    ) last_year ON this_year.month = last_year.month
    ORDER BY this_year.month
    """,
    "params": None,
}

PREPAID_MULTI_YEAR = {
    "description": "ลูกค้าที่จ่ายล่วงหน้า 2–5 ปี (Biennially / Triennially)",
    "category": "revenue",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        h.domain,
        p.name AS product_name,
        h.billingcycle,
        h.amount,
        h.regdate,
        h.nextduedate
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
      AND h.billingcycle IN ('Biennially', 'Triennially')
    ORDER BY h.nextduedate ASC
    """,
    "params": None,
}


# =============================================================================
# 📈 UPSELL / CROSS-SELL OPPORTUNITIES (Questions 11–16)
# =============================================================================

UPGRADE_CANDIDATES = {
    "description": "ลูกค้าที่มีแนวโน้มอัพเกรด (ซื้อหลายสินค้า, ใช้จ่ายมาก)",
    "category": "upsell",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        COUNT(DISTINCT h.id) AS product_count,
        COUNT(DISTINCT d.id) AS domain_count,
        SUM(DISTINCT i.total) AS total_spent
    FROM tblclients c
    JOIN tblhosting h ON h.userid = c.id AND h.domainstatus = 'Active'
    LEFT JOIN tbldomains d ON d.userid = c.id AND d.status = 'Active'
    LEFT JOIN tblinvoices i ON i.userid = c.id AND i.status = 'Paid'
    WHERE c.status = 'Active'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING product_count >= 2
    ORDER BY total_spent DESC
    LIMIT 100
    """,
    "params": None,
}

MONTHLY_TO_ANNUAL_CANDIDATES = {
    "description": "ลูกค้าที่จ่าย Monthly มา >= 3 เดือน — แนะนำเปลี่ยนเป็นรายปี",
    "category": "upsell",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        h.domain,
        p.name AS product_name,
        h.billingcycle,
        h.amount AS monthly_amount,
        h.regdate,
        DATEDIFF(CURDATE(), h.regdate) AS days_active,
        ROUND(h.amount * 12, 2) AS projected_annual
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
      AND h.billingcycle = 'Monthly'
      AND DATEDIFF(CURDATE(), h.regdate) >= 90
    ORDER BY h.amount DESC
    LIMIT 100
    """,
    "params": None,
}

RESELLER_CANDIDATES = {
    "description": "ลูกค้าที่สั่งซื้อโดเมน/โฮสต์ > 5 รายการ — ขาย Reseller/VPS",
    "category": "upsell",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        COUNT(DISTINCT h.id) AS hosting_count,
        COUNT(DISTINCT d.id) AS domain_count,
        (COUNT(DISTINCT h.id) + COUNT(DISTINCT d.id)) AS total_services
    FROM tblclients c
    LEFT JOIN tblhosting h ON h.userid = c.id AND h.domainstatus = 'Active'
    LEFT JOIN tbldomains d ON d.userid = c.id AND d.status = 'Active'
    WHERE c.status = 'Active'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING total_services > 5
    ORDER BY total_services DESC
    LIMIT 100
    """,
    "params": None,
}

MANAGED_SERVICE_CANDIDATES = {
    "description": "ลูกค้าที่ใช้ทรัพยากรสูงแต่ไม่เคย upgrade — เสนอ Managed Service",
    "category": "upsell",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        h.domain,
        p.name AS product_name,
        h.diskusage,
        h.disklimit,
        ROUND(h.diskusage / NULLIF(h.disklimit, 0) * 100, 1) AS disk_pct,
        h.bwusage,
        h.bwlimit,
        ROUND(h.bwusage / NULLIF(h.bwlimit, 0) * 100, 1) AS bw_pct
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
      AND (
          (h.disklimit > 0 AND h.diskusage / h.disklimit > 0.8)
          OR (h.bwlimit > 0 AND h.bwusage / h.bwlimit > 0.8)
      )
      AND c.id NOT IN (
          SELECT DISTINCT ii.userid
          FROM tblinvoiceitems ii
          WHERE ii.type = 'Upgrade'
      )
    ORDER BY disk_pct DESC
    LIMIT 100
    """,
    "params": None,
}

EARLY_UPGRADERS = {
    "description": "ลูกค้าที่มักอัปเกรดภายใน 1–3 เดือนแรก",
    "category": "upsell",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        ii.description AS upgrade_desc,
        ii.amount AS upgrade_amount,
        i.datepaid AS upgrade_date,
        h.regdate AS original_signup,
        DATEDIFF(i.datepaid, h.regdate) AS days_to_upgrade
    FROM tblinvoiceitems ii
    JOIN tblinvoices i ON ii.invoiceid = i.id
    JOIN tblhosting h ON ii.relid = h.id
    JOIN tblclients c ON ii.userid = c.id
    WHERE ii.type = 'Upgrade'
      AND i.status = 'Paid'
      AND DATEDIFF(i.datepaid, h.regdate) <= 90
    ORDER BY days_to_upgrade ASC
    LIMIT 100
    """,
    "params": None,
}

REPEAT_UPGRADERS = {
    "description": "ลูกค้าที่เคยอัปเกรดมาแล้วอย่างน้อย 1 ครั้ง (โอกาสอัปเกรดซ้ำ)",
    "category": "upsell",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        COUNT(ii.id) AS upgrade_count,
        SUM(ii.amount) AS total_upgrade_value,
        MAX(i.datepaid) AS last_upgrade_date
    FROM tblinvoiceitems ii
    JOIN tblinvoices i ON ii.invoiceid = i.id
    JOIN tblclients c ON ii.userid = c.id
    WHERE ii.type = 'Upgrade'
      AND i.status = 'Paid'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING upgrade_count >= 1
    ORDER BY upgrade_count DESC, total_upgrade_value DESC
    LIMIT 100
    """,
    "params": None,
}


# =============================================================================
# ⚠️ CHURN & RETENTION RISK (Questions 17–21)
# =============================================================================

CUSTOMER_NO_RENEWAL_2025 = {
    "description": "ลูกค้าที่ไม่ได้ต่ออายุในปี 2025",
    "category": "churn",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        MAX(i.datepaid) AS last_payment,
        COUNT(h.id) AS services
    FROM tblclients c
    LEFT JOIN tblinvoices i ON i.userid = c.id AND i.status = 'Paid'
    LEFT JOIN tblhosting h ON h.userid = c.id
    WHERE c.status = 'Active'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING last_payment < '2025-01-01' OR last_payment IS NULL
    ORDER BY last_payment DESC
    LIMIT 100
    """,
    "params": None,
}

CHURN_RISK_HIGH_VALUE = {
    "description": "ลูกค้ารายได้สูงแต่เสี่ยงยกเลิก (ซื้อใหม่อย่างเดียว ไม่เคยต่ออายุ)",
    "category": "churn",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        SUM(i.total) AS total_revenue,
        COUNT(i.id) AS invoice_count,
        MAX(i.datepaid) AS last_paid_date,
        COUNT(DISTINCT h.id) AS active_services
    FROM tblclients c
    JOIN tblinvoices i ON i.userid = c.id AND i.status = 'Paid'
    LEFT JOIN tblhosting h ON h.userid = c.id AND h.domainstatus = 'Active'
    WHERE c.id NOT IN (
        SELECT DISTINCT ii.userid
        FROM tblinvoiceitems ii
        WHERE ii.description LIKE '%renewal%'
           OR ii.description LIKE '%ต่ออายุ%'
    )
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING total_revenue > 1000
    ORDER BY total_revenue DESC
    LIMIT 100
    """,
    "params": None,
}

CUSTOMERS_CAME_BACK = {
    "description": "ลูกค้าที่เคยยกเลิกแล้วกลับมาใช้งานอีก (Cancelled → Active)",
    "category": "churn",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        COUNT(CASE WHEN h.domainstatus = 'Active' THEN 1 END) AS active_services,
        COUNT(CASE WHEN h.domainstatus IN ('Cancelled', 'Terminated') THEN 1 END) AS cancelled_services
    FROM tblclients c
    JOIN tblhosting h ON h.userid = c.id
    WHERE c.status = 'Active'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING active_services > 0 AND cancelled_services > 0
    ORDER BY cancelled_services DESC
    LIMIT 100
    """,
    "params": None,
}

CALL_THIS_WEEK = {
    "description": "ลูกค้าที่ควรโทรหาสัปดาห์นี้ (กำลังจะหมดอายุ, ยอดขายสูง)",
    "category": "churn",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        c.phonenumber,
        h.domain,
        p.name AS product_name,
        h.nextduedate,
        DATEDIFF(h.nextduedate, CURDATE()) AS days_until_due,
        h.amount,
        (
            SELECT SUM(inv.total)
            FROM tblinvoices inv
            WHERE inv.userid = c.id AND inv.status = 'Paid'
        ) AS lifetime_value
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
      AND h.nextduedate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 14 DAY)
    ORDER BY lifetime_value DESC
    LIMIT 1000
    """,
    "params": None,
}

EXPIRING_SOON_30_60_DAYS = {
    "description": "ลูกค้าที่กำลังจะหมดสัญญาใน 30–60 วัน",
    "category": "churn",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        c.phonenumber,
        h.domain,
        p.name AS product_name,
        h.nextduedate,
        DATEDIFF(h.nextduedate, CURDATE()) AS days_remaining,
        h.amount,
        h.billingcycle
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
      AND h.nextduedate BETWEEN DATE_ADD(CURDATE(), INTERVAL 30 DAY)
                            AND DATE_ADD(CURDATE(), INTERVAL 60 DAY)
    ORDER BY h.nextduedate ASC
    LIMIT 200
    """,
    "params": None,
}


# =============================================================================
# 📊 BUSINESS GROWTH SIGNALS (Questions 22–26)
# =============================================================================

FAST_GROWING_CUSTOMERS = {
    "description": "ลูกค้าธุรกิจเติบโตเร็ว (สั่งซื้อ > 1 โดเมนใน 1 เดือน)",
    "category": "growth",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        DATE_FORMAT(d.registrationdate, '%Y-%m') AS month,
        COUNT(d.id) AS domains_registered
    FROM tbldomains d
    JOIN tblclients c ON d.userid = c.id
    WHERE d.registrationdate >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email, month
    HAVING domains_registered > 1
    ORDER BY domains_registered DESC, month DESC
    LIMIT 100
    """,
    "params": None,
}

ENTERPRISE_BEHAVIOR = {
    "description": "ลูกค้าที่มีพฤติกรรมคล้าย Enterprise (หลาย product, ใช้จ่ายสูง, องค์กร)",
    "category": "growth",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.companyname,
        c.email,
        COUNT(DISTINCT h.id) AS hosting_count,
        COUNT(DISTINCT d.id) AS domain_count,
        (
            SELECT SUM(inv.total)
            FROM tblinvoices inv
            WHERE inv.userid = c.id AND inv.status = 'Paid'
        ) AS lifetime_value,
        COUNT(DISTINCT h.packageid) AS unique_products
    FROM tblclients c
    LEFT JOIN tblhosting h ON h.userid = c.id AND h.domainstatus = 'Active'
    LEFT JOIN tbldomains d ON d.userid = c.id AND d.status = 'Active'
    WHERE c.status = 'Active'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email
    HAVING (hosting_count >= 3 OR domain_count >= 5 OR unique_products >= 2)
    ORDER BY lifetime_value DESC
    LIMIT 100
    """,
    "params": None,
}

TOP_PACKAGES = {
    "description": "Top 5 แพ็กเกจยอดนิยม",
    "category": "growth",
    "sql": """
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        pg.name AS product_group,
        COUNT(h.id) AS total_subscriptions,
        SUM(CASE WHEN h.domainstatus = 'Active' THEN 1 ELSE 0 END) AS active,
        SUM(h.amount) AS total_recurring_revenue
    FROM tblproducts p
    LEFT JOIN tblproductgroups pg ON p.gid = pg.id
    LEFT JOIN tblhosting h ON h.packageid = p.id
    GROUP BY p.id, p.name, pg.name
    ORDER BY total_subscriptions DESC
    LIMIT 5
    """,
    "params": None,
}

ACTIVE_DOMAINS_COUNT = {
    "description": "โดเมนทั้งหมด vs Active",
    "category": "growth",
    "sql": """
    SELECT
        COUNT(*) AS total_domains,
        SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS active_domains,
        SUM(CASE WHEN status = 'Expired' THEN 1 ELSE 0 END) AS expired_domains,
        SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_domains,
        SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_domains
    FROM tbldomains
    """,
    "params": None,
}

ACTIVE_HOSTING_COUNT = {
    "description": "Hosting Active มีเท่าไหร่",
    "category": "growth",
    "sql": """
    SELECT
        COUNT(*) AS total_hosting,
        SUM(CASE WHEN domainstatus = 'Active' THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN domainstatus = 'Suspended' THEN 1 ELSE 0 END) AS suspended,
        SUM(CASE WHEN domainstatus = 'Terminated' THEN 1 ELSE 0 END) AS terminated,
        SUM(CASE WHEN domainstatus = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN domainstatus = 'Pending' THEN 1 ELSE 0 END) AS pending
    FROM tblhosting
    """,
    "params": None,
}


# =============================================================================
# 🛒 ORDER & PAYMENT BEHAVIOR (Questions 27–31)
# =============================================================================

ORDER_UNPAID = {
    "description": "ลูกค้าที่สั่งซื้อแล้วไม่จ่ายเงิน (Pending order + Unpaid invoice)",
    "category": "order",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        i.id AS invoice_id,
        i.invoicenum,
        i.date AS invoice_date,
        i.duedate,
        i.total,
        i.status AS invoice_status,
        DATEDIFF(CURDATE(), i.duedate) AS days_overdue
    FROM tblinvoices i
    JOIN tblclients c ON i.userid = c.id
    WHERE i.status = 'Unpaid'
    ORDER BY i.total DESC
    LIMIT 100
    """,
    "params": None,
}

PAID_UNTIL_YEAR = {
    "description": "ลูกค้าสั่งซื้อถึงปีไหน (paid until when) — ติดตามกลับมา",
    "category": "order",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        h.domain,
        p.name AS product_name,
        h.nextduedate AS paid_until,
        YEAR(h.nextduedate) AS paid_until_year,
        h.billingcycle,
        h.amount
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
    ORDER BY h.nextduedate ASC
    LIMIT 200
    """,
    "params": None,
}

BULK_BUYERS = {
    "description": "ลูกค้าที่ซื้อปริมาณเยอะ / สินค้าเดียวกันหลายตัว",
    "category": "order",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        p.name AS product_name,
        COUNT(h.id) AS qty_same_product,
        SUM(h.amount) AS total_recurring
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
    GROUP BY c.id, c.firstname, c.lastname, c.companyname, c.email, p.name
    HAVING qty_same_product > 1
    ORDER BY qty_same_product DESC
    LIMIT 100
    """,
    "params": None,
}

EXPIRING_SOON_30_DAYS = {
    "description": "ลูกค้าที่กำลังจะต่ออายุ (nextduedate ใน 30 วัน)",
    "category": "order",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        c.phonenumber,
        h.domain,
        p.name AS product_name,
        h.nextduedate,
        DATEDIFF(h.nextduedate, CURDATE()) AS days_until_due,
        h.amount,
        h.billingcycle
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
      AND h.nextduedate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    ORDER BY h.nextduedate ASC
    LIMIT 200
    """,
    "params": None,
}

FIRST_MONTH_CUSTOMERS = {
    "description": "ลูกค้าที่กำลังจะครบ 1 เดือนแรก (regdate + 30 days)",
    "category": "order",
    "sql": """
    SELECT
        c.id AS client_id,
        COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer,
        c.email,
        h.domain,
        p.name AS product_name,
        h.regdate,
        DATEDIFF(CURDATE(), h.regdate) AS days_since_signup,
        h.amount,
        h.billingcycle
    FROM tblhosting h
    JOIN tblclients c ON h.userid = c.id
    JOIN tblproducts p ON h.packageid = p.id
    WHERE h.domainstatus = 'Active'
      AND h.regdate BETWEEN DATE_SUB(CURDATE(), INTERVAL 35 DAY)
                        AND DATE_SUB(CURDATE(), INTERVAL 25 DAY)
    ORDER BY h.regdate ASC
    LIMIT 100
    """,
    "params": None,
}


# =============================================================================
# QUERY REGISTRY — maps query name to query dict
# =============================================================================

QUERIES = {
    # Domain & Service Analysis
    "DOMAIN_MULTI_NO_MULTISERVER": DOMAIN_MULTI_NO_MULTISERVER,
    "TRAFFIC_GROWTH_30PCT": TRAFFIC_GROWTH_30PCT,
    "HOSTING_SHARED_VPS_CANDIDATE": HOSTING_SHARED_VPS_CANDIDATE,
    "NO_EMAIL_HOSTING": NO_EMAIL_HOSTING,
    # Revenue & Spending
    "CUSTOMER_AVG_SPENDING_PER_YEAR": CUSTOMER_AVG_SPENDING_PER_YEAR,
    "CUSTOMER_TOP_SPENDERS": CUSTOMER_TOP_SPENDERS,
    "CUSTOMER_LOWEST_SPENDERS": CUSTOMER_LOWEST_SPENDERS,
    "PACKAGE_ORDER_RANKING": PACKAGE_ORDER_RANKING,
    "REVENUE_BY_PACKAGE": REVENUE_BY_PACKAGE,
    "REVENUE_YOY_COMPARISON": REVENUE_YOY_COMPARISON,
    "PREPAID_MULTI_YEAR": PREPAID_MULTI_YEAR,
    # Upsell / Cross-sell
    "UPGRADE_CANDIDATES": UPGRADE_CANDIDATES,
    "MONTHLY_TO_ANNUAL_CANDIDATES": MONTHLY_TO_ANNUAL_CANDIDATES,
    "RESELLER_CANDIDATES": RESELLER_CANDIDATES,
    "MANAGED_SERVICE_CANDIDATES": MANAGED_SERVICE_CANDIDATES,
    "EARLY_UPGRADERS": EARLY_UPGRADERS,
    "REPEAT_UPGRADERS": REPEAT_UPGRADERS,
    # Churn & Retention
    "CUSTOMER_NO_RENEWAL_2025": CUSTOMER_NO_RENEWAL_2025,
    "CHURN_RISK_HIGH_VALUE": CHURN_RISK_HIGH_VALUE,
    "CUSTOMERS_CAME_BACK": CUSTOMERS_CAME_BACK,
    "CALL_THIS_WEEK": CALL_THIS_WEEK,
    "EXPIRING_SOON_30_60_DAYS": EXPIRING_SOON_30_60_DAYS,
    # Business Growth
    "FAST_GROWING_CUSTOMERS": FAST_GROWING_CUSTOMERS,
    "ENTERPRISE_BEHAVIOR": ENTERPRISE_BEHAVIOR,
    "TOP_PACKAGES": TOP_PACKAGES,
    "ACTIVE_DOMAINS_COUNT": ACTIVE_DOMAINS_COUNT,
    "ACTIVE_HOSTING_COUNT": ACTIVE_HOSTING_COUNT,
    # Order & Payment
    "ORDER_UNPAID": ORDER_UNPAID,
    "PAID_UNTIL_YEAR": PAID_UNTIL_YEAR,
    "BULK_BUYERS": BULK_BUYERS,
    "EXPIRING_SOON_30_DAYS": EXPIRING_SOON_30_DAYS,
    "FIRST_MONTH_CUSTOMERS": FIRST_MONTH_CUSTOMERS,
}


# --- Keyword routing: maps Thai/English keywords to query names ---
KEYWORD_ROUTES = {
    # Domain & Service
    "หลายโดเมน": "DOMAIN_MULTI_NO_MULTISERVER",
    "multi domain": "DOMAIN_MULTI_NO_MULTISERVER",
    "multi-server": "DOMAIN_MULTI_NO_MULTISERVER",
    "traffic": "TRAFFIC_GROWTH_30PCT",
    "bandwidth": "TRAFFIC_GROWTH_30PCT",
    "shared hosting": "HOSTING_SHARED_VPS_CANDIDATE",
    "vps candidate": "HOSTING_SHARED_VPS_CANDIDATE",
    "อัพ vps": "HOSTING_SHARED_VPS_CANDIDATE",
    "email hosting": "NO_EMAIL_HOSTING",
    "ไม่มี email": "NO_EMAIL_HOSTING",
    # Revenue
    "เฉลี่ยจ่าย": "CUSTOMER_AVG_SPENDING_PER_YEAR",
    "average spending": "CUSTOMER_AVG_SPENDING_PER_YEAR",
    "ใช้จ่ายมากสุด": "CUSTOMER_TOP_SPENDERS",
    "top spender": "CUSTOMER_TOP_SPENDERS",
    "ใช้จ่ายน้อยสุด": "CUSTOMER_LOWEST_SPENDERS",
    "lowest spender": "CUSTOMER_LOWEST_SPENDERS",
    "แพ็กเกจ": "PACKAGE_ORDER_RANKING",
    "package ranking": "PACKAGE_ORDER_RANKING",
    "รายได้แยกตาม": "REVENUE_BY_PACKAGE",
    "revenue by package": "REVENUE_BY_PACKAGE",
    "ปีที่แล้ว vs ปีนี้": "REVENUE_YOY_COMPARISON",
    "yoy": "REVENUE_YOY_COMPARISON",
    "year over year": "REVENUE_YOY_COMPARISON",
    "จ่ายล่วงหน้า": "PREPAID_MULTI_YEAR",
    "prepaid": "PREPAID_MULTI_YEAR",
    "biennially": "PREPAID_MULTI_YEAR",
    "triennially": "PREPAID_MULTI_YEAR",
    # Upsell
    "อัพเกรด": "UPGRADE_CANDIDATES",
    "upgrade": "UPGRADE_CANDIDATES",
    "upsell": "UPGRADE_CANDIDATES",
    "monthly to annual": "MONTHLY_TO_ANNUAL_CANDIDATES",
    "รายเดือน": "MONTHLY_TO_ANNUAL_CANDIDATES",
    "reseller": "RESELLER_CANDIDATES",
    "managed service": "MANAGED_SERVICE_CANDIDATES",
    "ทรัพยากรสูง": "MANAGED_SERVICE_CANDIDATES",
    "อัปเกรดเร็ว": "EARLY_UPGRADERS",
    "early upgrade": "EARLY_UPGRADERS",
    "อัปเกรดซ้ำ": "REPEAT_UPGRADERS",
    "repeat upgrade": "REPEAT_UPGRADERS",
    # Churn
    "ไม่ต่ออายุ": "CUSTOMER_NO_RENEWAL_2025",
    "no renewal": "CUSTOMER_NO_RENEWAL_2025",
    "เสี่ยงยกเลิก": "CHURN_RISK_HIGH_VALUE",
    "churn risk": "CHURN_RISK_HIGH_VALUE",
    "กลับมา": "CUSTOMERS_CAME_BACK",
    "came back": "CUSTOMERS_CAME_BACK",
    "โทรหา": "CALL_THIS_WEEK",
    "call this week": "CALL_THIS_WEEK",
    "หมดสัญญา": "EXPIRING_SOON_30_60_DAYS",
    "30-60": "EXPIRING_SOON_30_60_DAYS",
    # Growth
    "เติบโตเร็ว": "FAST_GROWING_CUSTOMERS",
    "fast growing": "FAST_GROWING_CUSTOMERS",
    "enterprise": "ENTERPRISE_BEHAVIOR",
    "ยอดนิยม": "TOP_PACKAGES",
    "top package": "TOP_PACKAGES",
    "popular": "TOP_PACKAGES",
    "โดเมนทั้งหมด": "ACTIVE_DOMAINS_COUNT",
    "domain count": "ACTIVE_DOMAINS_COUNT",
    "hosting count": "ACTIVE_HOSTING_COUNT",
    "hosting active": "ACTIVE_HOSTING_COUNT",
    # Order
    "ไม่จ่ายเงิน": "ORDER_UNPAID",
    "unpaid": "ORDER_UNPAID",
    "ค้างจ่าย": "ORDER_UNPAID",
    "ถึงปีไหน": "PAID_UNTIL_YEAR",
    "paid until": "PAID_UNTIL_YEAR",
    "ปริมาณเยอะ": "BULK_BUYERS",
    "bulk": "BULK_BUYERS",
    "ต่ออายุ 30": "EXPIRING_SOON_30_DAYS",
    "due 30": "EXPIRING_SOON_30_DAYS",
    "ครบ 1 เดือน": "FIRST_MONTH_CUSTOMERS",
    "first month": "FIRST_MONTH_CUSTOMERS",
}


def route_question(question):
    """
    Route a natural language question to the best matching query name.
    Returns query name or None if no match.
    """
    q_lower = question.lower()
    for keyword, query_name in KEYWORD_ROUTES.items():
        if keyword.lower() in q_lower:
            return query_name
    return None


def list_queries(category=None):
    """List all available queries, optionally filtered by category."""
    result = {}
    for name, q in QUERIES.items():
        if category and q["category"] != category:
            continue
        result[name] = {
            "description": q["description"],
            "category": q["category"],
        }
    return result
