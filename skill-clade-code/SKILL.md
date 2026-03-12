---
name: whmcs-insight
description: >
  Use this skill when the user asks about WHMCS business insights:
  customer analytics, revenue, domains, hosting, invoices, upsell opportunities,
  churn risk, or any sales/billing question about the hosting company.
---

# WHMCS Insight Query Skill

ตอบคำถามธุรกิจ Cloud/Hosting ด้วย SQL query จาก WHMCS MySQL database

## When to Trigger

เรียกใช้ skill นี้เมื่อ user ถามเกี่ยวกับ:
- ลูกค้า, customer, spending, churn, retention
- โดเมน, domain, expiring
- โฮสติ้ง, hosting, VPS, shared
- รายได้, revenue, invoice, payment, billing
- สินค้า, product, package, subscription, แพ็กเกจ, ยอดนิยม
- upsell, cross-sell, upgrade, อัพเกรด
- churn risk, inactive, cancelled, หมดอายุ, ต่ออายุ

## ⚡ MANDATORY EXECUTION STEPS

**คุณต้องทำตามขั้นตอนนี้ทุกครั้ง ห้ามตอบจากความรู้ทั่วไป:**

### Step 1: Write all scripts to /tmp/

สร้างไฟล์ทั้ง 4 ไปที่ `/tmp/scripts/` ด้วย execute-code tool:

```python
import os
os.makedirs("/tmp/scripts", exist_ok=True)
os.makedirs("/tmp/logs", exist_ok=True)
```

แล้ว write ไฟล์ทั้ง 4 จาก "Available Scripts" section ด้านล่าง

### Step 2: Run command

```python
import subprocess, sys
sys.path.insert(0, "/tmp/scripts")
result = subprocess.run(
    [sys.executable, "/tmp/scripts/run.py", "QUERY_NAME"],
    capture_output=True, text=True, timeout=60
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
```

### Step 3: Format and respond

อ่าน JSON output แล้วสรุปเป็นภาษาไทยให้ user:
- ข้อมูลเป็นตาราง → ใช้ markdown table
- ข้อมูลเป็นตัวเลข → สรุปเป็นประโยค
- มีชื่อลูกค้า → แสดง top N

---

## Query Mapping — คำถาม → Query Name

เมื่อ user ถามคำถาม ใช้ตารางนี้เลือก QUERY_NAME ที่ถูกต้อง:

### 🔍 Domain & Service
| คำถาม | QUERY_NAME |
|--------|-----------|
| ใครมีหลายโดเมนแต่ hosting เดียว | `DOMAIN_MULTI_NO_MULTISERVER` |
| Traffic โตเกิน 30% / bandwidth สูง | `TRAFFIC_GROWTH_30PCT` |
| ใคร Shared Hosting ควรอัพ VPS | `HOSTING_SHARED_VPS_CANDIDATE` |
| ใครยังไม่มี Email Hosting | `NO_EMAIL_HOSTING` |

### 💰 Revenue & Spending
| คำถาม | QUERY_NAME |
|--------|-----------|
| ลูกค้าเฉลี่ยจ่ายกี่บาทต่อปี | `CUSTOMER_AVG_SPENDING_PER_YEAR` |
| ลูกค้าใช้จ่ายมากสุด / top spender | `CUSTOMER_TOP_SPENDERS` |
| ลูกค้าใช้จ่ายน้อยสุด | `CUSTOMER_LOWEST_SPENDERS` |
| แพ็กเกจสั่งซื้อน้อย→มาก | `PACKAGE_ORDER_RANKING` |
| รายได้แยกตามแพ็กเกจ | `REVENUE_BY_PACKAGE` |
| ยอดขายปีที่แล้ว vs ปีนี้ / YoY | `REVENUE_YOY_COMPARISON` |
| ลูกค้าจ่ายล่วงหน้า 2-5 ปี | `PREPAID_MULTI_YEAR` |

### 📈 Upsell / Cross-sell
| คำถาม | QUERY_NAME |
|--------|-----------|
| ลูกค้าควรอัพเกรด / upsell | `UPGRADE_CANDIDATES` |
| Monthly ควรเปลี่ยนเป็น Annual | `MONTHLY_TO_ANNUAL_CANDIDATES` |
| ลูกค้าควรซื้อ Reseller/VPS | `RESELLER_CANDIDATES` |
| ลูกค้าควรเสนอ Managed Service | `MANAGED_SERVICE_CANDIDATES` |
| อัปเกรดภายใน 1-3 เดือนแรก | `EARLY_UPGRADERS` |
| เคยอัปเกรดมาแล้ว 1 ครั้ง | `REPEAT_UPGRADERS` |

### ⚠️ Churn & Retention
| คำถาม | QUERY_NAME |
|--------|-----------|
| ลูกค้าไม่ต่ออายุปี 2025 | `CUSTOMER_NO_RENEWAL_2025` |
| รายได้สูงแต่เสี่ยงยกเลิก | `CHURN_RISK_HIGH_VALUE` |
| ลูกค้าเคยยกเลิกแล้วกลับมา | `CUSTOMERS_CAME_BACK` |
| ควรโทรหาลูกค้าคนไหนสัปดาห์นี้ | `CALL_THIS_WEEK` |
| หมดสัญญาใน 30-60 วัน | `EXPIRING_SOON_30_60_DAYS` |

### 📊 Business Growth
| คำถาม | QUERY_NAME |
|--------|-----------|
| ลูกค้าธุรกิจเติบโตเร็ว | `FAST_GROWING_CUSTOMERS` |
| ลูกค้าพฤติกรรมคล้าย Enterprise | `ENTERPRISE_BEHAVIOR` |
| Top 5 แพ็กเกจยอดนิยม | `TOP_PACKAGES` |
| โดเมนทั้งหมด vs Active | `ACTIVE_DOMAINS_COUNT` |
| Hosting Active มีเท่าไหร่ | `ACTIVE_HOSTING_COUNT` |

### 🛒 Order & Payment
| คำถาม | QUERY_NAME |
|--------|-----------|
| ใครสั่งซื้อแล้วไม่จ่าย / ค้างจ่าย | `ORDER_UNPAID` |
| ลูกค้าสั่งซื้อถึงปีไหน | `PAID_UNTIL_YEAR` |
| ใครซื้อปริมาณเยอะ | `BULK_BUYERS` |
| กำลังจะต่ออายุ 30 วัน | `EXPIRING_SOON_30_DAYS` |
| ลูกค้าครบ 1 เดือนแรก | `FIRST_MONTH_CUSTOMERS` |

### Custom SQL (คำถามที่ไม่ตรงกับข้างบน)

ใช้ `--sql` flag สร้าง SQL เองจาก schema ใน reference.md:
```
python /tmp/scripts/run.py --sql "SELECT COUNT(*) AS total FROM tblclients WHERE status='Active'"
```

**กฎ**: SELECT only, ใช้ JOINs ตาม reference.md, ใส่ LIMIT เสมอ

---

## Available Scripts

**คำเตือน**: ต้อง copy ไฟล์ทั้ง 4 ไฟล์ด้านล่างไปที่ `/tmp/scripts/` ก่อนรัน

### File 1: /tmp/scripts/logger.py

```python
import logging, os, sys
LOG_DIR = "/tmp/logs"
os.makedirs(LOG_DIR, exist_ok=True)
def _setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(level)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger
query_logger = _setup_logger("whmcs.query", os.path.join(LOG_DIR, "whmcs_queries.log"))
error_logger = _setup_logger("whmcs.error", os.path.join(LOG_DIR, "errors.log"), logging.ERROR)
def log_query(sql, execution_time=None, row_count=None, params=None):
    parts = [f"SQL: {sql.strip()[:500]}"]
    if execution_time is not None: parts.append(f"Time: {execution_time:.3f}s")
    if row_count is not None: parts.append(f"Rows: {row_count}")
    query_logger.info(" | ".join(parts))
def log_error(message, sql=None, exception=None):
    parts = [f"Error: {message}"]
    if sql: parts.append(f"SQL: {sql.strip()[:500]}")
    if exception: parts.append(f"Exception: {type(exception).__name__}: {exception}")
    error_logger.error(" | ".join(parts))
```

### File 2: /tmp/scripts/db.py

```python
import os, re, sys, time, subprocess
try:
    import pymysql
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "pymysql"])
    sys.path.insert(0, "/tmp/pylib")
    import pymysql
sys.path.insert(0, "/tmp/scripts")
from logger import log_query, log_error

DB_CONFIG = {
    "host": "103.2.113.229",
    "port": 3306,
    "user": "lotus_whmcs",
    "password": "w,jmik[8iy[",
    "database": "temp-whmcs",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 30,
    "read_timeout": 30,
    "charset": "utf8mb4",
}

DANGEROUS_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|RENAME|REPLACE|GRANT|REVOKE|LOAD)\b",
    re.IGNORECASE,
)
DEFAULT_LIMIT = 100
MAX_RETRIES = 2

def get_connection():
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.MySQLError as e:
            last_error = e
            if attempt < MAX_RETRIES: time.sleep(1)
    log_error("Connection failed after retries", exception=last_error)
    raise last_error

def validate_read_only(sql):
    stripped = sql.strip().rstrip(";").strip()
    match = DANGEROUS_PATTERNS.search(stripped)
    if match:
        raise ValueError(f"Blocked: Only SELECT queries allowed. Detected '{match.group()}' statement.")

def query(sql, params=None, limit=None):
    validate_read_only(sql)
    row_limit = limit if limit else DEFAULT_LIMIT
    conn = get_connection()
    start = time.time()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchmany(row_limit)
            elapsed = round(time.time() - start, 3)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            log_query(sql, execution_time=elapsed, row_count=len(rows), params=params)
            return {"data": rows, "row_count": len(rows), "columns": columns, "execution_time_sec": elapsed}
    except pymysql.MySQLError as e:
        log_error("Query execution failed", sql=sql, exception=e)
        return {"error": f"MySQL Error: {e}", "sql": sql}
    except ValueError:
        raise
    except Exception as e:
        log_error("Unexpected error", sql=sql, exception=e)
        return {"error": f"Error: {e}", "sql": sql}
    finally:
        conn.close()

def query_raw(sql, params=None, limit=None):
    result = query(sql, params, limit)
    if "error" in result: return result
    return result["data"]

def get_table_schema(table_name):
    allowed = {"tblclients","tbldomains","tblhosting","tblinvoices","tblinvoiceitems","tblproducts","tblproductgroups","tblorders","tbltickets","tblcurrencies"}
    if table_name not in allowed:
        return {"error": f"Table '{table_name}' not in allowed list: {sorted(allowed)}"}
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`")
            rows = cursor.fetchall()
            return {"table": table_name, "columns": rows, "column_count": len(rows)}
    except pymysql.MySQLError as e:
        return {"error": f"MySQL Error: {e}"}
    finally:
        conn.close()
```

### File 3: /tmp/scripts/queries.py

```python
QUERIES = {
    "DOMAIN_MULTI_NO_MULTISERVER": {
        "description": "ลูกค้าที่มีหลายโดเมนแต่ใช้ hosting เดียว",
        "category": "domain_service",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, COUNT(DISTINCT d.id) AS domain_count, COUNT(DISTINCT h.id) AS hosting_count FROM tblclients c JOIN tbldomains d ON d.userid=c.id AND d.status='Active' LEFT JOIN tblhosting h ON h.userid=c.id AND h.domainstatus='Active' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING domain_count>1 AND hosting_count<=1 ORDER BY domain_count DESC LIMIT 100",
        "params": None
    },
    "TRAFFIC_GROWTH_30PCT": {
        "description": "ลูกค้า Traffic/Bandwidth สูง",
        "category": "domain_service",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, h.domain, h.bwusage, h.bwlimit, ROUND(h.bwusage/NULLIF(h.bwlimit,0)*100,1) AS bw_usage_pct FROM tblhosting h JOIN tblclients c ON h.userid=c.id WHERE h.domainstatus='Active' AND h.bwlimit>0 AND h.bwusage>0 ORDER BY bw_usage_pct DESC LIMIT 100",
        "params": None
    },
    "HOSTING_SHARED_VPS_CANDIDATE": {
        "description": "ลูกค้า Shared Hosting ควรอัพ VPS",
        "category": "domain_service",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, h.domain, p.name AS product_name, h.diskusage, h.disklimit, ROUND(h.diskusage/NULLIF(h.disklimit,0)*100,1) AS disk_pct, h.bwusage, h.bwlimit, ROUND(h.bwusage/NULLIF(h.bwlimit,0)*100,1) AS bw_pct FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND p.type='hostingaccount' AND ((h.disklimit>0 AND h.diskusage/h.disklimit>0.7) OR (h.bwlimit>0 AND h.bwusage/h.bwlimit>0.7)) ORDER BY disk_pct DESC LIMIT 100",
        "params": None
    },
    "NO_EMAIL_HOSTING": {
        "description": "ลูกค้าที่ยังไม่มี Email Hosting",
        "category": "domain_service",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, COUNT(DISTINCT h.id) AS hosting_count, COUNT(DISTINCT d.id) AS domain_count FROM tblclients c LEFT JOIN tblhosting h ON h.userid=c.id AND h.domainstatus='Active' LEFT JOIN tbldomains d ON d.userid=c.id AND d.status='Active' WHERE c.status='Active' AND (h.id IS NOT NULL OR d.id IS NOT NULL) AND c.id NOT IN (SELECT DISTINCT h2.userid FROM tblhosting h2 JOIN tblproducts p2 ON h2.packageid=p2.id WHERE LOWER(p2.name) LIKE '%email%' AND h2.domainstatus='Active') GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email ORDER BY hosting_count DESC LIMIT 100",
        "params": None
    },
    "CUSTOMER_AVG_SPENDING_PER_YEAR": {
        "description": "ลูกค้าเฉลี่ยจ่ายกี่บาทต่อปี (5 ปีย้อนหลัง)",
        "category": "revenue",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, YEAR(i.datepaid) AS pay_year, SUM(i.total) AS yearly_total FROM tblclients c JOIN tblinvoices i ON i.userid=c.id WHERE i.status='Paid' AND i.datepaid>=DATE_SUB(CURDATE(),INTERVAL 5 YEAR) GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email,pay_year ORDER BY yearly_total DESC LIMIT 200",
        "params": None
    },
    "CUSTOMER_TOP_SPENDERS": {
        "description": "ลูกค้าที่ใช้จ่ายมากสุด (Top spenders)",
        "category": "revenue",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, SUM(i.total) AS total_spent, COUNT(i.id) AS invoice_count, MIN(i.datepaid) AS first_payment, MAX(i.datepaid) AS last_payment FROM tblclients c JOIN tblinvoices i ON i.userid=c.id WHERE i.status='Paid' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email ORDER BY total_spent DESC LIMIT 50",
        "params": None
    },
    "CUSTOMER_LOWEST_SPENDERS": {
        "description": "ลูกค้าที่ใช้จ่ายน้อยสุด",
        "category": "revenue",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, SUM(i.total) AS total_spent, COUNT(i.id) AS invoice_count FROM tblclients c JOIN tblinvoices i ON i.userid=c.id WHERE i.status='Paid' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING total_spent>0 ORDER BY total_spent ASC LIMIT 50",
        "params": None
    },
    "PACKAGE_ORDER_RANKING": {
        "description": "แพ็กเกจสั่งซื้อน้อยสุด→มากสุด (new vs renewal)",
        "category": "revenue",
        "sql": "SELECT p.id AS product_id, p.name AS product_name, pg.name AS product_group, COUNT(DISTINCT h.id) AS total_subscriptions FROM tblproducts p LEFT JOIN tblproductgroups pg ON p.gid=pg.id LEFT JOIN tblhosting h ON h.packageid=p.id GROUP BY p.id,p.name,pg.name ORDER BY total_subscriptions ASC",
        "params": None
    },
    "REVENUE_BY_PACKAGE": {
        "description": "รายได้แยกตามแพ็กเกจ",
        "category": "revenue",
        "sql": "SELECT pg.name AS product_group, p.name AS product_name, COUNT(DISTINCT ii.userid) AS customer_count, SUM(ii.amount) AS total_revenue FROM tblinvoiceitems ii JOIN tblinvoices i ON ii.invoiceid=i.id JOIN tblhosting h ON ii.relid=h.id AND ii.type='Hosting' JOIN tblproducts p ON h.packageid=p.id LEFT JOIN tblproductgroups pg ON p.gid=pg.id WHERE i.status='Paid' GROUP BY pg.name,p.name ORDER BY total_revenue DESC",
        "params": None
    },
    "REVENUE_YOY_COMPARISON": {
        "description": "ยอดขายปีที่แล้ว vs ปีนี้ (% เปลี่ยนแปลง)",
        "category": "revenue",
        "sql": "SELECT ty.month, ty.revenue AS revenue_this_year, ly.revenue AS revenue_last_year, ROUND((ty.revenue-COALESCE(ly.revenue,0))/NULLIF(COALESCE(ly.revenue,0),0)*100,1) AS pct_change FROM (SELECT DATE_FORMAT(datepaid,'%m') AS month, SUM(total) AS revenue FROM tblinvoices WHERE status='Paid' AND YEAR(datepaid)=YEAR(CURDATE()) GROUP BY month) ty LEFT JOIN (SELECT DATE_FORMAT(datepaid,'%m') AS month, SUM(total) AS revenue FROM tblinvoices WHERE status='Paid' AND YEAR(datepaid)=YEAR(CURDATE())-1 GROUP BY month) ly ON ty.month=ly.month ORDER BY ty.month",
        "params": None
    },
    "PREPAID_MULTI_YEAR": {
        "description": "ลูกค้าจ่ายล่วงหน้า 2-5 ปี (Biennially/Triennially)",
        "category": "revenue",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, h.domain, p.name AS product_name, h.billingcycle, h.amount, h.regdate, h.nextduedate FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND h.billingcycle IN ('Biennially','Triennially') ORDER BY h.nextduedate ASC",
        "params": None
    },
    "UPGRADE_CANDIDATES": {
        "description": "ลูกค้าที่มีแนวโน้มอัพเกรด",
        "category": "upsell",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, COUNT(DISTINCT h.id) AS product_count, COUNT(DISTINCT d.id) AS domain_count FROM tblclients c JOIN tblhosting h ON h.userid=c.id AND h.domainstatus='Active' LEFT JOIN tbldomains d ON d.userid=c.id AND d.status='Active' WHERE c.status='Active' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING product_count>=2 ORDER BY product_count DESC LIMIT 100",
        "params": None
    },
    "MONTHLY_TO_ANNUAL_CANDIDATES": {
        "description": "ลูกค้า Monthly >= 3 เดือน แนะนำเปลี่ยนรายปี",
        "category": "upsell",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, h.domain, p.name AS product_name, h.billingcycle, h.amount AS monthly_amount, h.regdate, DATEDIFF(CURDATE(),h.regdate) AS days_active, ROUND(h.amount*12,2) AS projected_annual FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND h.billingcycle='Monthly' AND DATEDIFF(CURDATE(),h.regdate)>=90 ORDER BY h.amount DESC LIMIT 100",
        "params": None
    },
    "RESELLER_CANDIDATES": {
        "description": "ลูกค้าบริการ > 5 รายการ — เสนอ Reseller/VPS",
        "category": "upsell",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, COUNT(DISTINCT h.id) AS hosting_count, COUNT(DISTINCT d.id) AS domain_count, (COUNT(DISTINCT h.id)+COUNT(DISTINCT d.id)) AS total_services FROM tblclients c LEFT JOIN tblhosting h ON h.userid=c.id AND h.domainstatus='Active' LEFT JOIN tbldomains d ON d.userid=c.id AND d.status='Active' WHERE c.status='Active' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING total_services>5 ORDER BY total_services DESC LIMIT 100",
        "params": None
    },
    "MANAGED_SERVICE_CANDIDATES": {
        "description": "ลูกค้าใช้ทรัพยากรสูงแต่ไม่เคย upgrade",
        "category": "upsell",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, h.domain, p.name AS product_name, h.diskusage, h.disklimit, ROUND(h.diskusage/NULLIF(h.disklimit,0)*100,1) AS disk_pct, h.bwusage, h.bwlimit, ROUND(h.bwusage/NULLIF(h.bwlimit,0)*100,1) AS bw_pct FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND ((h.disklimit>0 AND h.diskusage/h.disklimit>0.8) OR (h.bwlimit>0 AND h.bwusage/h.bwlimit>0.8)) AND c.id NOT IN (SELECT DISTINCT ii.userid FROM tblinvoiceitems ii WHERE ii.type='Upgrade') ORDER BY disk_pct DESC LIMIT 100",
        "params": None
    },
    "EARLY_UPGRADERS": {
        "description": "ลูกค้าอัปเกรดภายใน 1-3 เดือนแรก",
        "category": "upsell",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, ii.description AS upgrade_desc, ii.amount AS upgrade_amount, i.datepaid AS upgrade_date, h.regdate AS original_signup, DATEDIFF(i.datepaid,h.regdate) AS days_to_upgrade FROM tblinvoiceitems ii JOIN tblinvoices i ON ii.invoiceid=i.id JOIN tblhosting h ON ii.relid=h.id JOIN tblclients c ON ii.userid=c.id WHERE ii.type='Upgrade' AND i.status='Paid' AND DATEDIFF(i.datepaid,h.regdate)<=90 ORDER BY days_to_upgrade ASC LIMIT 100",
        "params": None
    },
    "REPEAT_UPGRADERS": {
        "description": "ลูกค้าเคยอัปเกรดแล้ว >= 1 ครั้ง",
        "category": "upsell",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, COUNT(ii.id) AS upgrade_count, SUM(ii.amount) AS total_upgrade_value, MAX(i.datepaid) AS last_upgrade_date FROM tblinvoiceitems ii JOIN tblinvoices i ON ii.invoiceid=i.id JOIN tblclients c ON ii.userid=c.id WHERE ii.type='Upgrade' AND i.status='Paid' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING upgrade_count>=1 ORDER BY upgrade_count DESC LIMIT 100",
        "params": None
    },
    "CUSTOMER_NO_RENEWAL_2025": {
        "description": "ลูกค้าที่ไม่ได้ต่ออายุในปี 2025",
        "category": "churn",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, MAX(i.datepaid) AS last_payment, COUNT(h.id) AS services FROM tblclients c LEFT JOIN tblinvoices i ON i.userid=c.id AND i.status='Paid' LEFT JOIN tblhosting h ON h.userid=c.id WHERE c.status='Active' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING last_payment<'2025-01-01' OR last_payment IS NULL ORDER BY last_payment DESC LIMIT 100",
        "params": None
    },
    "CHURN_RISK_HIGH_VALUE": {
        "description": "ลูกค้ารายได้สูงแต่เสี่ยงยกเลิก",
        "category": "churn",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, SUM(i.total) AS total_revenue, COUNT(i.id) AS invoice_count, MAX(i.datepaid) AS last_paid_date FROM tblclients c JOIN tblinvoices i ON i.userid=c.id AND i.status='Paid' WHERE c.id NOT IN (SELECT DISTINCT ii.userid FROM tblinvoiceitems ii WHERE ii.description LIKE '%renewal%' OR ii.description LIKE '%ต่ออายุ%') GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING total_revenue>1000 ORDER BY total_revenue DESC LIMIT 100",
        "params": None
    },
    "CUSTOMERS_CAME_BACK": {
        "description": "ลูกค้าเคยยกเลิกแล้วกลับมา",
        "category": "churn",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, COUNT(CASE WHEN h.domainstatus='Active' THEN 1 END) AS active_services, COUNT(CASE WHEN h.domainstatus IN ('Cancelled','Terminated') THEN 1 END) AS cancelled_services FROM tblclients c JOIN tblhosting h ON h.userid=c.id WHERE c.status='Active' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING active_services>0 AND cancelled_services>0 ORDER BY cancelled_services DESC LIMIT 100",
        "params": None
    },
    "CALL_THIS_WEEK": {
        "description": "ลูกค้าควรโทรหาสัปดาห์นี้ (กำลังหมดอายุ ยอดสูง)",
        "category": "churn",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, c.phonenumber, h.domain, p.name AS product_name, h.nextduedate, DATEDIFF(h.nextduedate,CURDATE()) AS days_until_due, h.amount, (SELECT SUM(inv.total) FROM tblinvoices inv WHERE inv.userid=c.id AND inv.status='Paid') AS lifetime_value FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND h.nextduedate BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 14 DAY) ORDER BY lifetime_value DESC LIMIT 1000",
        "params": None
    },
    "EXPIRING_SOON_30_60_DAYS": {
        "description": "ลูกค้าหมดสัญญาใน 30-60 วัน",
        "category": "churn",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, c.phonenumber, h.domain, p.name AS product_name, h.nextduedate, DATEDIFF(h.nextduedate,CURDATE()) AS days_remaining, h.amount, h.billingcycle FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND h.nextduedate BETWEEN DATE_ADD(CURDATE(),INTERVAL 30 DAY) AND DATE_ADD(CURDATE(),INTERVAL 60 DAY) ORDER BY h.nextduedate ASC LIMIT 200",
        "params": None
    },
    "FAST_GROWING_CUSTOMERS": {
        "description": "ลูกค้าธุรกิจเติบโตเร็ว (สั่งซื้อ>1 โดเมน/เดือน)",
        "category": "growth",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, DATE_FORMAT(d.registrationdate,'%Y-%m') AS month, COUNT(d.id) AS domains_registered FROM tbldomains d JOIN tblclients c ON d.userid=c.id WHERE d.registrationdate>=DATE_SUB(CURDATE(),INTERVAL 6 MONTH) GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email,month HAVING domains_registered>1 ORDER BY domains_registered DESC LIMIT 100",
        "params": None
    },
    "ENTERPRISE_BEHAVIOR": {
        "description": "ลูกค้าพฤติกรรมคล้าย Enterprise",
        "category": "growth",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.companyname, c.email, COUNT(DISTINCT h.id) AS hosting_count, COUNT(DISTINCT d.id) AS domain_count, (SELECT SUM(inv.total) FROM tblinvoices inv WHERE inv.userid=c.id AND inv.status='Paid') AS lifetime_value, COUNT(DISTINCT h.packageid) AS unique_products FROM tblclients c LEFT JOIN tblhosting h ON h.userid=c.id AND h.domainstatus='Active' LEFT JOIN tbldomains d ON d.userid=c.id AND d.status='Active' WHERE c.status='Active' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email HAVING hosting_count>=3 OR domain_count>=5 OR unique_products>=2 ORDER BY lifetime_value DESC LIMIT 100",
        "params": None
    },
    "TOP_PACKAGES": {
        "description": "Top 5 แพ็กเกจยอดนิยม",
        "category": "growth",
        "sql": "SELECT p.id AS product_id, p.name AS product_name, pg.name AS product_group, COUNT(h.id) AS total_subscriptions, SUM(CASE WHEN h.domainstatus='Active' THEN 1 ELSE 0 END) AS active, SUM(h.amount) AS total_recurring_revenue FROM tblproducts p LEFT JOIN tblproductgroups pg ON p.gid=pg.id LEFT JOIN tblhosting h ON h.packageid=p.id GROUP BY p.id,p.name,pg.name ORDER BY total_subscriptions DESC LIMIT 5",
        "params": None
    },
    "ACTIVE_DOMAINS_COUNT": {
        "description": "โดเมนทั้งหมด vs Active",
        "category": "growth",
        "sql": "SELECT COUNT(*) AS total_domains, SUM(CASE WHEN status='Active' THEN 1 ELSE 0 END) AS active_domains, SUM(CASE WHEN status='Expired' THEN 1 ELSE 0 END) AS expired_domains, SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END) AS pending_domains, SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) AS cancelled_domains FROM tbldomains",
        "params": None
    },
    "ACTIVE_HOSTING_COUNT": {
        "description": "Hosting Active มีเท่าไหร่",
        "category": "growth",
        "sql": "SELECT COUNT(*) AS total_hosting, SUM(CASE WHEN domainstatus='Active' THEN 1 ELSE 0 END) AS active, SUM(CASE WHEN domainstatus='Suspended' THEN 1 ELSE 0 END) AS suspended, SUM(CASE WHEN domainstatus='Terminated' THEN 1 ELSE 0 END) AS terminated, SUM(CASE WHEN domainstatus='Cancelled' THEN 1 ELSE 0 END) AS cancelled, SUM(CASE WHEN domainstatus='Pending' THEN 1 ELSE 0 END) AS pending FROM tblhosting",
        "params": None
    },
    "ORDER_UNPAID": {
        "description": "ลูกค้าสั่งซื้อแล้วไม่จ่ายเงิน",
        "category": "order",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, i.id AS invoice_id, i.invoicenum, i.date AS invoice_date, i.duedate, i.total, i.status AS invoice_status, DATEDIFF(CURDATE(),i.duedate) AS days_overdue FROM tblinvoices i JOIN tblclients c ON i.userid=c.id WHERE i.status='Unpaid' ORDER BY i.total DESC LIMIT 100",
        "params": None
    },
    "PAID_UNTIL_YEAR": {
        "description": "ลูกค้าสั่งซื้อถึงปีไหน",
        "category": "order",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, h.domain, p.name AS product_name, h.nextduedate AS paid_until, YEAR(h.nextduedate) AS paid_until_year, h.billingcycle, h.amount FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' ORDER BY h.nextduedate ASC LIMIT 200",
        "params": None
    },
    "BULK_BUYERS": {
        "description": "ลูกค้าซื้อปริมาณเยอะ/สินค้าเดียวกันหลายตัว",
        "category": "order",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, p.name AS product_name, COUNT(h.id) AS qty_same_product, SUM(h.amount) AS total_recurring FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' GROUP BY c.id,c.firstname,c.lastname,c.companyname,c.email,p.name HAVING qty_same_product>1 ORDER BY qty_same_product DESC LIMIT 100",
        "params": None
    },
    "EXPIRING_SOON_30_DAYS": {
        "description": "ลูกค้ากำลังจะต่ออายุใน 30 วัน",
        "category": "order",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, c.phonenumber, h.domain, p.name AS product_name, h.nextduedate, DATEDIFF(h.nextduedate,CURDATE()) AS days_until_due, h.amount, h.billingcycle FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND h.nextduedate BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 30 DAY) ORDER BY h.nextduedate ASC LIMIT 200",
        "params": None
    },
    "FIRST_MONTH_CUSTOMERS": {
        "description": "ลูกค้ากำลังจะครบ 1 เดือนแรก",
        "category": "order",
        "sql": "SELECT c.id AS client_id, COALESCE(CONCAT(c.firstname,' ',c.lastname),c.companyname) AS customer, c.email, h.domain, p.name AS product_name, h.regdate, DATEDIFF(CURDATE(),h.regdate) AS days_since_signup, h.amount, h.billingcycle FROM tblhosting h JOIN tblclients c ON h.userid=c.id JOIN tblproducts p ON h.packageid=p.id WHERE h.domainstatus='Active' AND h.regdate BETWEEN DATE_SUB(CURDATE(),INTERVAL 35 DAY) AND DATE_SUB(CURDATE(),INTERVAL 25 DAY) ORDER BY h.regdate ASC LIMIT 100",
        "params": None
    },
}

def route_question(question):
    KEYWORD_ROUTES = {
        "หลายโดเมน":"DOMAIN_MULTI_NO_MULTISERVER","multi domain":"DOMAIN_MULTI_NO_MULTISERVER",
        "traffic":"TRAFFIC_GROWTH_30PCT","bandwidth":"TRAFFIC_GROWTH_30PCT",
        "shared hosting":"HOSTING_SHARED_VPS_CANDIDATE","vps candidate":"HOSTING_SHARED_VPS_CANDIDATE","อัพ vps":"HOSTING_SHARED_VPS_CANDIDATE",
        "email hosting":"NO_EMAIL_HOSTING","ไม่มี email":"NO_EMAIL_HOSTING",
        "เฉลี่ยจ่าย":"CUSTOMER_AVG_SPENDING_PER_YEAR","average spending":"CUSTOMER_AVG_SPENDING_PER_YEAR",
        "ใช้จ่ายมากสุด":"CUSTOMER_TOP_SPENDERS","top spender":"CUSTOMER_TOP_SPENDERS",
        "ใช้จ่ายน้อยสุด":"CUSTOMER_LOWEST_SPENDERS","lowest spender":"CUSTOMER_LOWEST_SPENDERS",
        "แพ็กเกจ":"PACKAGE_ORDER_RANKING","package ranking":"PACKAGE_ORDER_RANKING",
        "รายได้แยกตาม":"REVENUE_BY_PACKAGE","revenue by package":"REVENUE_BY_PACKAGE",
        "ปีที่แล้ว vs ปีนี้":"REVENUE_YOY_COMPARISON","yoy":"REVENUE_YOY_COMPARISON",
        "จ่ายล่วงหน้า":"PREPAID_MULTI_YEAR","prepaid":"PREPAID_MULTI_YEAR",
        "อัพเกรด":"UPGRADE_CANDIDATES","upgrade":"UPGRADE_CANDIDATES","upsell":"UPGRADE_CANDIDATES",
        "monthly to annual":"MONTHLY_TO_ANNUAL_CANDIDATES","รายเดือน":"MONTHLY_TO_ANNUAL_CANDIDATES",
        "reseller":"RESELLER_CANDIDATES",
        "managed service":"MANAGED_SERVICE_CANDIDATES","ทรัพยากรสูง":"MANAGED_SERVICE_CANDIDATES",
        "อัปเกรดเร็ว":"EARLY_UPGRADERS","early upgrade":"EARLY_UPGRADERS",
        "อัปเกรดซ้ำ":"REPEAT_UPGRADERS","repeat upgrade":"REPEAT_UPGRADERS",
        "ไม่ต่ออายุ":"CUSTOMER_NO_RENEWAL_2025","no renewal":"CUSTOMER_NO_RENEWAL_2025",
        "เสี่ยงยกเลิก":"CHURN_RISK_HIGH_VALUE","churn risk":"CHURN_RISK_HIGH_VALUE",
        "กลับมา":"CUSTOMERS_CAME_BACK","came back":"CUSTOMERS_CAME_BACK",
        "โทรหา":"CALL_THIS_WEEK","call this week":"CALL_THIS_WEEK",
        "หมดสัญญา":"EXPIRING_SOON_30_60_DAYS","30-60":"EXPIRING_SOON_30_60_DAYS",
        "เติบโตเร็ว":"FAST_GROWING_CUSTOMERS","fast growing":"FAST_GROWING_CUSTOMERS",
        "enterprise":"ENTERPRISE_BEHAVIOR",
        "ยอดนิยม":"TOP_PACKAGES","top package":"TOP_PACKAGES","popular":"TOP_PACKAGES",
        "โดเมนทั้งหมด":"ACTIVE_DOMAINS_COUNT","domain count":"ACTIVE_DOMAINS_COUNT",
        "hosting count":"ACTIVE_HOSTING_COUNT","hosting active":"ACTIVE_HOSTING_COUNT",
        "ไม่จ่ายเงิน":"ORDER_UNPAID","unpaid":"ORDER_UNPAID","ค้างจ่าย":"ORDER_UNPAID",
        "ถึงปีไหน":"PAID_UNTIL_YEAR","paid until":"PAID_UNTIL_YEAR",
        "ปริมาณเยอะ":"BULK_BUYERS","bulk":"BULK_BUYERS",
        "ต่ออายุ 30":"EXPIRING_SOON_30_DAYS","due 30":"EXPIRING_SOON_30_DAYS",
        "ครบ 1 เดือน":"FIRST_MONTH_CUSTOMERS","first month":"FIRST_MONTH_CUSTOMERS",
    }
    q_lower = question.lower()
    for keyword, query_name in KEYWORD_ROUTES.items():
        if keyword.lower() in q_lower:
            return query_name
    return None

def list_queries(category=None):
    result = {}
    for name, q in QUERIES.items():
        if category and q["category"] != category: continue
        result[name] = {"description": q["description"], "category": q["category"]}
    return result
```

### File 4: /tmp/scripts/run.py

```python
import json, sys, os, argparse, datetime, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import query, query_raw, get_table_schema
from queries import QUERIES, route_question, list_queries

def json_serial(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)): return obj.isoformat()
    if isinstance(obj, datetime.timedelta): return str(obj)
    if isinstance(obj, bytes): return obj.decode("utf-8", errors="replace")
    if hasattr(obj, '__float__'): return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def format_output(result, fmt="json"):
    if "error" in result:
        return json.dumps(result, indent=2, ensure_ascii=False)
    data = result.get("data", result) if isinstance(result, dict) else result
    if fmt == "json":
        output = result if isinstance(result, dict) else {"data": result}
        return json.dumps(output, indent=2, default=json_serial, ensure_ascii=False)
    elif fmt == "csv":
        if not data: return ""
        import csv, io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return buf.getvalue()
    else:
        return json.dumps(result, indent=2, default=json_serial, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="WHMCS Insight Query Tool")
    parser.add_argument("query_name", nargs="?", help="Predefined query name")
    parser.add_argument("--ask", type=str, help="Natural language question")
    parser.add_argument("--sql", type=str, help="Custom SQL query (SELECT only)")
    parser.add_argument("--list", action="store_true", help="List queries")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--schema", type=str, help="Get table schema")
    parser.add_argument("--format", type=str, default="json", choices=["json","csv"])
    args = parser.parse_args()

    if args.list:
        print(json.dumps(list_queries(args.category), indent=2, ensure_ascii=False))
        return
    if args.schema:
        print(json.dumps(get_table_schema(args.schema), indent=2, default=json_serial, ensure_ascii=False))
        return
    if args.ask:
        matched = route_question(args.ask)
        if matched:
            q = QUERIES[matched]
            result = query(q["sql"], q.get("params"))
            print(format_output(result, args.format))
        else:
            print(json.dumps({"error": "ไม่พบ query ที่ตรงกับคำถาม", "question": args.ask}, indent=2, ensure_ascii=False))
        return
    if args.sql:
        result = query(args.sql)
        print(format_output(result, args.format))
        return
    if args.query_name:
        if args.query_name not in QUERIES:
            print(json.dumps({"error": f"Unknown query: {args.query_name}", "available": sorted(QUERIES.keys())}, indent=2, ensure_ascii=False))
            return
        q = QUERIES[args.query_name]
        result = query(q["sql"], q.get("params"))
        print(format_output(result, args.format))
        return
    parser.print_help()

if __name__ == "__main__":
    main()
```

---

## Safety Rules

1. **Read-only** — INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE ถูก block
2. **Row limit** — default 100 rows
3. **Timeout** — 30s connection + read

## References
- Full schema + JOIN patterns → `reference.md`
- Tool specifications → `tools.md`