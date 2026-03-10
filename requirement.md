# Claude Code Prompt: สร้าง WHMCS Insight Query Skill

---

## 📋 Prompt สำหรับสั่ง Claude Code

```
Create a complete Agent Skill for querying a WHMCS on-premise MySQL database 
to generate sales and customer insights. Follow the standard skill structure:
SKILL.md, tools.md, reference.md, scripts/, requirements.txt

---

## CONTEXT

This skill is for a hosting/domain company using WHMCS (on-premise).
The team wants to ask business questions in natural language and get 
SQL-powered answers from the WHMCS database.

---

## DATABASE SCHEMA

The WHMCS MySQL database has these key tables:

### tblclients
- id, firstname, lastname, companyname, email, phonenumber
- country, datecreated, status (Active/Inactive/Closed)
- credit, currency, groupid

### tbldomains
- id, userid (FK→tblclients), orderid
- domain, type, status (Active/Expired/Cancelled/Pending/Redemption/Transferred Away)
- registrationdate, expirydate, nextduedate, nextinvoicedate
- registrar, registrationperiod, recurringamount, firstpaymentamount
- paymentmethod, dnsmanagement, emailforwarding, idprotection, donotrenew

### tblhosting
- id, userid (FK→tblclients), packageid (FK→tblproducts), orderid
- domain, domainstatus (Active/Suspended/Terminated/Cancelled/Pending/Fraud)
- regdate, nextduedate, nextinvoicedate
- amount, firstpaymentamount, billingcycle (Monthly/Quarterly/Semi-Annually/Annually/Biennially/Triennially)
- diskusage, disklimit, bwusage, bwlimit
- server, qty, promoid

### tblinvoices
- id, userid (FK→tblclients)
- date, duedate, datepaid
- subtotal, total, credit, tax
- status (Paid/Unpaid/Cancelled/Refunded/Collections/Draft)
- paymentmethod

### tblinvoiceitems
- id, invoiceid (FK→tblinvoices), userid (FK→tblclients)
- type (Hosting/Domain/AddOn/Item/Upgrade/Prorated)
- relid, description, amount, taxed

### tblproducts
- id, name, type, gid (FK→tblproductgroups)
- hidden, paytype (free/onetime/recurring)
- billingcycleupgrade, retired, is_featured

### tblproductgroups
- id, name, slug, hidden, order

---

## INSIGHT QUESTIONS TO SUPPORT

Build SQL queries and natural language routing for ALL of these questions:

### 🔍 Domain & Service Analysis
1. ใครมีหลายโดเมนแต่ยังไม่ใช้ Multi-Server (ใครมีโดเมน>1, โฮสต์เดียว, VPS เดียว)
2. ใครมี Traffic โตขึ้นเกิน 30% ใน 3 เดือนล่าสุด (bwusage growth in tblhosting)
3. ใครกำลังใช้ Shared Hosting แต่มีพฤติกรรมเหมาะกับ VPS
   (disk/bandwidth usage สูง หรือ มีหลายโดเมนบน shared)
4. ใครยังไม่มี Email Hosting
   (มี hosting/domain แต่ไม่มี product จากกลุ่ม email ใน tblinvoiceitems)

### 💰 Revenue & Spending
5. ลูกค้าเฉลี่ยจ่ายกี่บาทต่อปี (ชื่อลูกค้า, รายจ่าย 5 ปีย้อนหลัง เรียงมากไปน้อย)
6. ลูกค้าที่ใช้จ่ายมากสุด / น้อยสุด ต่อปี
7. แพ็กเกจที่คนสั่งซื้อน้อยสุด → มากสุด (แยก: สั่งซื้อใหม่ vs ต่ออายุ)
8. รายได้แยกตามแพ็กเกจ (Hosting, Domain, Email, Website) แยกลูกค้าใหม่ vs ต่ออายุ
9. ยอดขายปีที่แล้ว vs ปีนี้ คิดเป็น % เปลี่ยนแปลง
10. ลูกค้าที่จ่ายล่วงหน้า 2-5 ปี (billingcycle = Biennially หรือ Triennially)

### 📈 Upsell / Cross-sell Opportunities
11. ลูกค้ารายใด สามารถอัพเกรดขายได้ (ซื้อสินค้าหลายอย่าง, มีแนวโน้ม)
12. ลูกค้ารายใดมีแนวโน้มซื้อแพ็กเกจรายปีแทนรายเดือน
    (จ่าย Monthly มาแล้ว >= 3 เดือน)
13. ลูกค้ากลุ่มใดมีโอกาสขาย Reseller Hosting หรือ VPS
    (สั่งซื้อโดเมนหรือโฮสต์มากกว่า 5 รายการใน 1 เดือน)
14. ลูกค้ากลุ่มใดควรเสนอ Managed Service
    (ใช้ทรัพยากรสูง แต่ไม่เคย upgrade)
15. ลูกค้ากลุ่มใดมักอัปเกรดภายใน 1 หรือ 3 เดือนแรก
16. ลูกค้ารายใดเคยอัปเกรดมาแล้ว 1 ครั้ง (มีโอกาสอัปเกรดซ้ำ)

### ⚠️ Churn & Retention Risk
17. รายชื่อลูกค้าที่ไม่ได้ต่ออายุในปี 2025
18. ลูกค้ารายใดสร้างรายได้มากแต่มีความเสี่ยงยกเลิก
    (ซื้อใหม่อย่างเดียว ไม่เคยต่ออายุ)
19. ลูกค้ากลุ่มใดเคยยกเลิกแล้วกลับมา (Cancelled → Active again)
20. สัปดาห์นี้ควรโทรหาลูกค้าคนไหน
    (กำลังจะหมดอายุ ยอดขายสูงสุด 1,000 คน)
21. ลูกค้ารายใดกำลังจะหมดสัญญาใน 30–60 วัน

### 📊 Business Growth Signals
22. ลูกค้ารายใดมีธุรกิจเติบโตเร็ว (สั่งซื้อ > 1 โดเมนใน 1 เดือน)
23. ลูกค้ากลุ่มใดมีพฤติกรรมคล้าย Enterprise
24. Top 5 แพ็กเกจยอดนิยม
25. โดเมนจดภายใต้เรากี่โดเมน ทั้งหมด vs Active
26. Hosting Active มีเท่าไหร่

### 🛒 Order & Payment Behavior
27. ใครซื้ออะไร สั่งซื้ออย่างเดียวไม่จ่ายเงิน
    (tblorders status=Pending, tblinvoices status=Unpaid)
28. ใครสั่งซื้อถึงปีไหน (เช่น paid until 2024 → ติดตามกลับมาปี 2025)
29. ใครซื้อปริมาณเยอะ หรือสินค้าเดียวกันหลายๆ ตัว
30. ลูกค้ารายใดกำลังจะต่ออายุ (nextduedate ใน 30 วัน)
31. ลูกค้ารายใดกำลังจะครบ 1 เดือนแรก (regdate + 30 days)

---

## REQUIRED FILES TO CREATE

### 1. SKILL.md
Standard skill frontmatter + instructions for the AI agent:
- When to trigger (any business question about WHMCS customers, revenue, domains, hosting)
- Step-by-step: understand intent → map to query category → run SQL → format response
- Reference to tools.md and reference.md
- Output format guidelines (table for lists, summary for aggregates)

### 2. reference.md  
Full domain knowledge:
- Table schema summary (key columns only)
- Business logic: status codes meaning (Active/Cancelled/etc)
- WHMCS billing cycles mapping
- Product type categories (Hosting vs Domain vs Email vs VPS etc)
- Common JOIN patterns between tables
- Table of Contents at top (file will be long)

### 3. tools.md
Document these tools the agent can call:
- `query_whmcs(sql: str) → list[dict]` — execute read-only SQL
- `get_schema(table_name: str) → dict` — get table structure
- `format_table(data: list[dict]) → str` — format as markdown table
- Input/output specs, error handling notes, security constraints

### 4. scripts/db.py
Production-ready database connection layer:
- Load config from .env (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
- Connection pooling with pymysql
- `query(sql, params=None) → list[dict]` — safe parameterized queries
- `get_table_schema(table_name) → dict`
- Error handling, connection retry, query timeout (30s)
- Read-only enforcement (raise error on INSERT/UPDATE/DELETE/DROP)
- Query logging with execution time

### 5. scripts/queries.py
All SQL queries as named constants, organized by category:
- CUSTOMER_TOP_SPENDERS
- CUSTOMER_NO_RENEWAL_2025
- DOMAIN_MULTI_NO_MULTISERVER
- HOSTING_SHARED_VPS_CANDIDATE  
- REVENUE_BY_PACKAGE
- REVENUE_YOY_COMPARISON
- EXPIRING_SOON_30_DAYS
- EXPIRING_SOON_60_DAYS
- NO_EMAIL_HOSTING
- MONTHLY_TO_ANNUAL_CANDIDATES
- RESELLER_CANDIDATES
- CHURN_RISK_HIGH_VALUE
- TRAFFIC_GROWTH_30PCT
- ORDER_UNPAID
- TOP_PACKAGES
- ACTIVE_DOMAINS_COUNT
- ACTIVE_HOSTING_COUNT
- CUSTOMERS_CAME_BACK
- UPGRADE_CANDIDATES
- PREPAID_MULTI_YEAR
(and all others from the insight questions list above)

### 6. scripts/run.py
Entry point / orchestrator:
- Accept natural language question as input (CLI arg or stdin)
- Route to appropriate query from queries.py
- Call db.py to execute
- Format and print results
- Support --format flag: table / json / csv

### 7. scripts/logger.py
Centralized logging:
- Log query text, execution time, row count, timestamp
- Write to logs/whmcs_queries.log
- Separate error log to logs/errors.log

### 8. requirements.txt
```
pymysql>=1.1.0
python-dotenv>=1.0.0
tabulate>=0.9.0
pandas>=2.0.0
```

### 9. .env.example
```
DB_HOST=192.168.x.x
DB_PORT=3306
DB_NAME=whmcs
DB_USER=whmcs_readonly
DB_PASS=your_password_here
DB_TIMEOUT=30
```

### 10. .gitignore
```
.env
logs/
__pycache__/
*.pyc
.DS_Store
```

### 11. README.md
- Overview
- Prerequisites
- Setup instructions (create read-only MySQL user, install deps, configure .env)
- How to run (CLI examples for each insight category)
- Security notes (read-only user required)
- Query examples

---

## IMPORTANT CONSTRAINTS

1. **Read-only ONLY** — never generate INSERT/UPDATE/DELETE/DROP queries
2. **Parameterized queries** — never string-interpolate user input into SQL
3. **Thai language support** — comments and output labels can be Thai
4. **Performance** — add LIMIT clauses by default (LIMIT 100 unless user specifies)
5. **NULL handling** — use COALESCE for firstname/lastname/companyname
6. **Billing cycle mapping**:
   - Monthly = 1 month
   - Quarterly = 3 months  
   - Semi-Annually = 6 months
   - Annually = 12 months
   - Biennially = 24 months
   - Triennially = 36 months

---

## EXPECTED OUTPUT STRUCTURE

```
whmcs-insight-skill/
├── SKILL.md
├── tools.md
├── reference.md
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── scripts/
    ├── db.py
    ├── queries.py
    ├── run.py
    └── logger.py
```

Please create all files completely. Make SQL queries production-quality 
with proper JOINs, WHERE clauses, GROUP BY, and ORDER BY.
Thai business context: this is a Thai hosting company, 
currency is THB, customers may have Thai names.