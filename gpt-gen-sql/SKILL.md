---
name: whmcs-database-agent
description: Use this skill whenever the user asks questions about WHMCS customers, domains, hosting services, invoices, tickets, transactions, or product statistics.
---

# WHMCS Database Agent

This skill allows the AI to query a WHMCS database using natural language.

The AI should:

1. Read the database schema
2. Generate SQL (with anti-hallucination validation against schema)
3. Validate SQL for safety (no DELETE, UPDATE, DROP, etc.)
4. Execute query (with 10s timeout, 500-row limit, auto-retry)
5. Return result with SQL and data

Execution entry point:

scripts/run.py

## Scope Rules

This skill is ONLY for querying WHMCS database data (customers, hosting, domains, invoices, tickets, transactions, products).

- If the user asks about anything NOT related to WHMCS data (e.g. business strategy, marketing advice, general knowledge), respond: **"ขออภัยครับ ไม่สามารถช่วยได้เนื่องจากไม่อยู่ใน scope ของระบบ ระบบนี้ใช้สำหรับดึงข้อมูลจากฐานข้อมูล WHMCS เท่านั้นครับ"**
- Do NOT generate business insights, analysis, or recommendations
- Only present the data from the query results

## Excel & CSV Export

When query results exceed **100 rows**, the script automatically exports to files:
- Excel: `/tmp/query_result.xlsx`
- CSV: `/tmp/query_result.csv`
- The JSON output will contain `"export": "file"`, `"excel_path"`, and `"csv_path"` instead of `"result"`
- When this happens, provide the Excel file to the user and show the SQL that was used
- Tell the user: "ผลลัพธ์มีจำนวนมาก จึงส่งออกเป็นไฟล์ Excel และ CSV แล้วครับ"

## Query Caching

- Identical queries are cached for 5 minutes in `/tmp/sql_cache/`
- Output includes `"cached": true/false` to indicate if result came from cache

## Output Formatting Rules

When presenting results to the user:

1. **Always show the SQL query** that was executed in a code block:
   ```sql
   SELECT ...
   ```

2. **Do NOT use markdown tables** — use a numbered list format instead:

   **Example output format:**

   SQL ที่ใช้:
   ```sql
   SELECT c.firstname, c.lastname, h.domain, h.billingcycle, p.name
   FROM tblhosting h
   JOIN tblclients c ON c.id = h.userid
   JOIN tblproducts p ON p.id = h.packageid
   WHERE h.billingcycle = 'Triennially' AND h.domainstatus = 'Active'
   LIMIT 20;
   ```

   ผลลัพธ์ (พบ 20 รายการ):

   1. **Janenarong Chimmajcha** — LG Household & Health Care — `lghnh.co.th` — Triennially — HOSTING UNLIMITED DOMAIN GREEN 1
   2. **Chakkapan Mongkonrat** — `kwanjairesort.com` — Triennially — HOSTING UNLIMITED EMAIL & DB RED 1
   3. **ศูนย์คอมพิวเตอร์** — มหาวิทยาลัยฟาดอนี — `host.ftu.ac.th` — Triennially — CLOUD VPS LINUX 1

3. **Format rules for the list:**
   - Bold the customer name
   - Use backticks for domain names
   - Separate fields with " — " (em dash)
   - Show the total count at the top (e.g. "พบ 20 รายการ")
   - Format numbers with commas (e.g. 2,616)

4. **Do NOT add business insights, analysis, or recommendations after the data**

5. **Keep the response concise** — show the data only

## Sandbox Rules

The execute-code sandbox runs at `/app/` which is a **read-only filesystem**, so:

1. **Always write scripts to `/tmp/` first** — copy all content from the "Available Scripts" section
2. **Scripts have DB values ready to use** — the system injects values from Configuration automatically, no replacement needed
3. **Run scripts from `/tmp/`** — never use path `scripts/` or `/app/`
