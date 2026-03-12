# Available Tools

เครื่องมือที่ agent สามารถเรียกใช้ผ่าน `scripts/run.py`

---

## query_whmcs — Execute SQL Query

ฟังก์ชันหลักสำหรับ query ข้อมูลจาก WHMCS MySQL

### Predefined Query
```bash
python scripts/run.py <QUERY_NAME> [--format json|table|csv]
```

**Input**: ชื่อ query จาก `queries.py` (e.g. `CUSTOMER_TOP_SPENDERS`)
**Output**: JSON object

```json
{
  "data": [{"client_id": 1, "customer": "John Doe", "total_spent": 50000}],
  "row_count": 10,
  "columns": ["client_id", "customer", "total_spent"],
  "execution_time_sec": 0.123
}
```

### Natural Language Routing
```bash
python scripts/run.py --ask "ลูกค้าที่ใช้จ่ายมากสุด"
```

**Input**: คำถามภาษาไทย/อังกฤษ
**Output**: Routes to matching predefined query, returns same JSON format

### Custom SQL
```bash
python scripts/run.py --sql "SELECT COUNT(*) AS total FROM tblclients"
```

**Input**: SQL string (SELECT only)
**Output**: Same JSON format

### Error Response
```json
{
  "error": "MySQL Error: (1146) Table 'whmcs.unknown' doesn't exist",
  "sql": "SELECT * FROM unknown"
}
```

---

## get_schema — Get Table Structure

ดู column ของตาราง WHMCS

```bash
python scripts/run.py --schema <table_name>
```

**Input**: ชื่อตาราง (ต้องอยู่ใน whitelist)
**Allowed tables**: `tblclients`, `tbldomains`, `tblhosting`, `tblinvoices`, `tblinvoiceitems`, `tblproducts`, `tblproductgroups`, `tblorders`, `tbltickets`, `tblcurrencies`

**Output**:
```json
{
  "table": "tblclients",
  "columns": [
    {"Field": "id", "Type": "int(10)", "Null": "NO", "Key": "PRI", "Default": null, "Extra": "auto_increment"},
    ...
  ],
  "column_count": 15
}
```

---

## list_queries — List Available Queries

```bash
python scripts/run.py --list [--category <category>]
```

**Categories**: `domain_service`, `revenue`, `upsell`, `churn`, `growth`, `order`

**Output** (JSON):
```json
{
  "CUSTOMER_TOP_SPENDERS": {
    "description": "ลูกค้าที่ใช้จ่ายมากสุดต่อปี",
    "category": "revenue"
  },
  ...
}
```

---

## format_table — Output Formatting

ใช้ `--format` flag:

| Format | Description | Use Case |
|--------|-------------|----------|
| `json` | JSON object (default) | Agent processing, API |
| `table` | ASCII table (requires tabulate) | Human-readable display |
| `csv` | CSV format | Export to spreadsheet |

```bash
python scripts/run.py TOP_PACKAGES --format table
python scripts/run.py CUSTOMER_TOP_SPENDERS --format csv
```

---

## Security Constraints

| Rule | Detail |
|------|--------|
| **Read-only** | INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE blocked |
| **Table whitelist** | `--schema` only works with allowed tables |
| **Row limit** | Default 100 rows max |
| **Timeout** | 30s connection + 30s read |
| **Parameterized** | ใช้ `%s` placeholders, ไม่ string-interpolate |
| **Logging** | ทุก query ถูก log ที่ `logs/whmcs_queries.log` |
| **Error isolation** | MySQL errors return JSON, ไม่ crash |