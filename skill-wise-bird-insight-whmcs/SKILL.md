---
name: whmcs-insight
description: >
  Use this skill when the user asks about WHMCS business insights:
  customer analytics, revenue, domains, hosting, invoices, upsell opportunities,
  churn risk, or any sales/billing question about the hosting company.
---

# WHMCS Insight Query Skill

สำหรับ Cloud/Hosting Company ที่ใช้ WHMCS — ตอบคำถามธุรกิจด้วย SQL query จาก MySQL database

## When to Trigger

เรียกใช้ skill นี้เมื่อ user ถามเกี่ยวกับ:
- ลูกค้า (customers, spending, churn, retention)
- โดเมน (domains, expiring, registration)
- โฮสติ้ง (hosting, VPS, shared, resource usage)
- รายได้ (revenue, invoices, payments, billing)
- สินค้า (products, packages, subscriptions)
- โอกาสขาย (upsell, cross-sell, upgrade candidates)
- ความเสี่ยง (churn risk, inactive, cancelled)

---

## How It Works — 2 Modes

### Mode 1: Predefined Queries (แนะนำ)

มี 31 queries สำเร็จรูปครอบคลุม 6 หมวด — ใช้ชื่อ query โดยตรง:

```bash
python scripts/run.py CUSTOMER_TOP_SPENDERS
python scripts/run.py TOP_PACKAGES --format table
python scripts/run.py EXPIRING_SOON_30_DAYS --format csv
```

หรือใช้คำถามภาษาธรรมชาติ:

```bash
python scripts/run.py --ask "ลูกค้าที่ใช้จ่ายมากสุด"
python scripts/run.py --ask "ใครยังไม่จ่ายเงิน"
```

### Mode 2: Custom SQL (สำหรับคำถามซับซ้อน)

สร้าง SQL เองจาก schema knowledge (SELECT only):

```bash
python scripts/run.py --sql "SELECT COUNT(*) AS total FROM tblclients WHERE status='Active'"
```

---

## Step-by-Step Instructions for Agent

1. **เข้าใจคำถาม** — user ถามอะไร? อยู่ในหมวดไหน?
2. **ตรวจดู predefined queries** — ใช้ `python scripts/run.py --list` ดูว่ามี query ไหนตรง
3. **เลือก mode**:
   - ถ้ามี predefined → ใช้ชื่อ query `python scripts/run.py <QUERY_NAME>`
   - ถ้าไม่มี → สร้าง SQL เอง `python scripts/run.py --sql "SELECT ..."`
4. **Execute** — รัน script แล้วอ่าน JSON result
5. **ตอบ user** — สรุปผลเป็นภาษาที่อ่านง่าย:
   - ข้อมูลเป็นตาราง → ใช้ markdown table
   - ข้อมูลเป็นตัวเลข → สรุปเป็นประโยค
   - มีชื่อลูกค้า → แสดง top N

---

## Query Categories

| Category | หมวด | Queries |
|----------|-------|---------|
| `domain_service` | 🔍 Domain & Service | 4 queries |
| `revenue` | 💰 Revenue & Spending | 7 queries |
| `upsell` | 📈 Upsell / Cross-sell | 6 queries |
| `churn` | ⚠️ Churn & Retention | 5 queries |
| `growth` | 📊 Business Growth | 5 queries |
| `order` | 🛒 Order & Payment | 5 queries |

List by category: `python scripts/run.py --list --category revenue`

---

## Utility Commands

```bash
# List all 31 queries
python scripts/run.py --list

# Get table schema (column names, types)
python scripts/run.py --schema tblclients
python scripts/run.py --schema tblhosting

# Output formats: json (default), table, csv
python scripts/run.py TOP_PACKAGES --format table
```

---

## Safety Rules

1. **Read-only** — INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE ถูก block
2. **Parameterized queries** — ไม่ string-interpolate ค่าจาก user
3. **Row limit** — default 100 rows, ป้องกัน memory overflow
4. **Timeout** — connection 30s, read 30s

## Sandbox Rules

The execute-code sandbox runs at `/app/` which is a **read-only filesystem**, so:

1. **Always write scripts to `/tmp/` first** — copy the scripts directory content
2. **Scripts load DB config from .env** — ต้องมี .env ที่ /tmp/ หรือ parent directory
3. **Run scripts from `/tmp/`** — never use path `/app/`

## References

- Full schema + JOIN patterns → `reference.md`
- Tool specifications → `tools.md`
- All SQL queries → `scripts/queries.py`