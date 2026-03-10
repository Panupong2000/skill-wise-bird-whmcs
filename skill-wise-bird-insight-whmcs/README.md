# WHMCS Insight Query Skill

AI agent skill สำหรับ query ข้อมูล WHMCS เพื่อวิเคราะห์ลูกค้า รายได้ และโอกาสขาย

## Overview

ให้ทีมขาย/บริหาร ถามคำถามธุรกิจเป็นภาษาไทย/อังกฤษ แล้วได้คำตอบจาก WHMCS database:

- 🔍 **Domain & Service Analysis** — ใครมีหลายโดเมน, traffic สูง, ควรอัพ VPS
- 💰 **Revenue & Spending** — รายได้ตามแพ็กเกจ, top spenders, YoY comparison
- 📈 **Upsell / Cross-sell** — ลูกค้าที่ควรอัพเกรด, เปลี่ยนรายปี, ขาย Reseller
- ⚠️ **Churn & Retention** — เสี่ยงยกเลิก, ไม่ต่ออายุ, ลูกค้ากลับมา
- 📊 **Business Growth** — ธุรกิจเติบโตเร็ว, Enterprise behavior, Top packages
- 🛒 **Order & Payment** — ค้างจ่าย, bulk buyers, กำลังจะหมดอายุ

## Prerequisites

1. **MySQL Read-only User** — สร้าง user แยกที่มีสิทธิ์ SELECT เท่านั้น:
   ```sql
   CREATE USER 'whmcs_readonly'@'%' IDENTIFIED BY 'your_password';
   GRANT SELECT ON whmcs.* TO 'whmcs_readonly'@'%';
   FLUSH PRIVILEGES;
   ```

2. **Python 3.8+**

3. **Network** — เครื่องที่รันต้องเข้าถึง MySQL ของ WHMCS ได้

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure database connection
cp .env.example .env
# Edit .env with your MySQL credentials

# 3. Test connection
python scripts/run.py --schema tblclients
```

## Usage

```bash
# List all 31 available insight queries
python scripts/run.py --list

# Run specific query
python scripts/run.py CUSTOMER_TOP_SPENDERS
python scripts/run.py TOP_PACKAGES --format table
python scripts/run.py ORDER_UNPAID --format csv

# Natural language question
python scripts/run.py --ask "ใครใช้จ่ายมากสุด"
python scripts/run.py --ask "ลูกค้าที่ค้างจ่าย"

# Custom SQL (SELECT only)
python scripts/run.py --sql "SELECT COUNT(*) AS total FROM tblclients WHERE status='Active'"

# Get table schema
python scripts/run.py --schema tblhosting

# Filter by category
python scripts/run.py --list --category revenue
python scripts/run.py --list --category churn
```

## Query Categories

| Flag | Queries | ตัวอย่าง |
|------|---------|---------|
| `domain_service` | 4 | Multi-domain, VPS candidates, Email hosting |
| `revenue` | 7 | Top spenders, YoY, Revenue by package |
| `upsell` | 6 | Monthly→Annual, Reseller candidates |
| `churn` | 5 | No renewal, Churn risk, Came back |
| `growth` | 5 | Fast growing, Enterprise, Top packages |
| `order` | 5 | Unpaid, Bulk buyers, Expiring soon |

## File Structure

```
skill-wise-bird-insight-whmcs/
├── SKILL.md              # Agent instructions & routing logic
├── tools.md              # Tool specifications
├── reference.md          # Full WHMCS schema & business rules
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── .env.example          # Database config template
├── .gitignore
├── logs/                 # Query & error logs (auto-created)
│   ├── whmcs_queries.log
│   └── errors.log
└── scripts/
    ├── db.py             # Database connection layer
    ├── queries.py        # 31 SQL queries + keyword routing
    ├── run.py            # CLI entry point
    └── logger.py         # Centralized logging
```

## Security

- ✅ **Read-only** — All write SQL (INSERT/UPDATE/DELETE/DROP) is blocked at code level
- ✅ **Parameterized** — No string interpolation in SQL
- ✅ **Table whitelist** — Schema inspection limited to WHMCS tables
- ✅ **Row limit** — Default max 100 rows per query
- ✅ **Timeout** — 30s connection + read timeout
- ✅ **Logging** — All queries logged with timestamp and execution time

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` | ตรวจ DB_HOST/PORT ใน .env, เปิด MySQL remote access |
| `Access denied` | ตรวจ DB_USER/DB_PASS, GRANT SELECT |
| `Table doesn't exist` | ตรวจ DB_NAME ใน .env ให้ตรงกับ WHMCS database |
| `No module pymysql` | รัน `pip install -r requirements.txt` |
| `Blocked: Only SELECT` | ลองใช้ query ที่มี SELECT เท่านั้น |
