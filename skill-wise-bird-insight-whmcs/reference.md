# WHMCS Database Reference

> Full schema, status codes, billing cycles, and JOIN patterns for query generation.

## Table of Contents

- [Table Schema](#table-schema)
  - [tblclients](#tblclients)
  - [tblhosting](#tblhosting)
  - [tbldomains](#tbldomains)
  - [tblinvoices](#tblinvoices)
  - [tblinvoiceitems](#tblinvoiceitems)
  - [tblproducts](#tblproducts)
  - [tblproductgroups](#tblproductgroups)
  - [tblorders](#tblorders)
- [Status Codes](#status-codes)
- [Billing Cycles](#billing-cycles)
- [Product Type Categories](#product-type-categories)
- [JOIN Patterns](#join-patterns)
- [Common Query Patterns](#common-query-patterns)

---

## Table Schema

### tblclients

ลูกค้า — ตาราง master ที่ทุกตารางอ้างอิงถึง

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Client ID |
| firstname | varchar | ชื่อ |
| lastname | varchar | นามสกุล |
| companyname | varchar | ชื่อบริษัท |
| email | varchar | Email |
| phonenumber | varchar | เบอร์โทร |
| address1 | varchar | ที่อยู่ |
| city | varchar | จังหวัด |
| state | varchar | รัฐ/จังหวัด |
| postcode | varchar | รหัสไปรษณีย์ |
| country | varchar(2) | รหัสประเทศ (TH, US) |
| status | enum | `Active`, `Inactive`, `Closed` |
| datecreated | date | วันสร้างบัญชี |
| credit | decimal | เครดิตคงเหลือ |
| currency | int | Currency ID (FK → tblcurrencies) |
| groupid | int | Client group ID |
| notes | text | หมายเหตุ admin |

> **NULL Handling**: ใช้ `COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname)` เสมอ

---

### tblhosting

Hosting / VPS / Service subscriptions — บริการที่ลูกค้าสั่งซื้อ

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Service ID |
| userid | int (FK) | → tblclients.id |
| packageid | int (FK) | → tblproducts.id |
| orderid | int (FK) | → tblorders.id |
| domain | varchar | Domain ที่ใช้กับ hosting |
| domainstatus | enum | `Active`, `Suspended`, `Terminated`, `Cancelled`, `Pending`, `Fraud` |
| regdate | date | วันที่สั่งซื้อ |
| nextduedate | date | วันครบกำหนดต่ออายุ |
| nextinvoicedate | date | วันออก invoice ถัดไป |
| amount | decimal | ยอดเรียกเก็บ recurring |
| firstpaymentamount | decimal | ยอดจ่ายครั้งแรก |
| billingcycle | varchar | รอบบิล (ดู Billing Cycles) |
| diskusage | int | Disk ที่ใช้ (MB) |
| disklimit | int | Disk limit (MB), 0 = unlimited |
| bwusage | int | Bandwidth ที่ใช้ (MB) |
| bwlimit | int | Bandwidth limit (MB), 0 = unlimited |
| server | int | Server ID |
| username | varchar | Hosting username |
| qty | int | Quantity |
| promoid | int | Promotion ID |

---

### tbldomains

โดเมนที่จดทะเบียน

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Domain ID |
| userid | int (FK) | → tblclients.id |
| orderid | int (FK) | → tblorders.id |
| domain | varchar | ชื่อโดเมน (e.g. example.co.th) |
| type | varchar | `Register`, `Transfer` |
| status | enum | `Active`, `Expired`, `Cancelled`, `Pending`, `Redemption`, `Transferred Away` |
| registrationdate | date | วันจดทะเบียน |
| expirydate | date | วันหมดอายุ |
| nextduedate | date | วันครบกำหนด |
| nextinvoicedate | date | วันออก invoice |
| registrar | varchar | Registrar module |
| registrationperiod | int | ระยะเวลาจด (ปี) |
| recurringamount | decimal | ค่าต่ออายุ |
| firstpaymentamount | decimal | ค่าจดครั้งแรก |
| paymentmethod | varchar | วิธีจ่ายเงิน |
| dnsmanagement | tinyint | เปิด DNS Management (1/0) |
| emailforwarding | tinyint | เปิด Email Forwarding (1/0) |
| idprotection | tinyint | เปิด ID Protection (1/0) |
| donotrenew | tinyint | ไม่ต่ออายุ (1/0) |

---

### tblinvoices

ใบแจ้งหนี้

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Invoice ID |
| userid | int (FK) | → tblclients.id |
| invoicenum | varchar | เลขใบแจ้งหนี้ |
| date | date | วันที่ออก |
| duedate | date | วันครบกำหนด |
| datepaid | datetime | วันที่จ่าย (NULL = ยังไม่จ่าย) |
| subtotal | decimal | ยอดก่อน VAT |
| total | decimal | ยอดรวมทั้งหมด |
| credit | decimal | Credit ที่ใช้ |
| tax | decimal | ภาษี |
| tax2 | decimal | ภาษี 2 |
| status | enum | `Paid`, `Unpaid`, `Cancelled`, `Refunded`, `Collections`, `Draft` |
| paymentmethod | varchar | วิธีชำระ |
| notes | text | หมายเหตุ |

---

### tblinvoiceitems

รายการใน invoice — ใช้ระบุประเภทสินค้าและเชื่อมกลับไปหา hosting/domain

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Item ID |
| invoiceid | int (FK) | → tblinvoices.id |
| userid | int (FK) | → tblclients.id |
| type | varchar | `Hosting`, `Domain`, `DomainRegister`, `DomainTransfer`, `Addon`, `Item`, `Upgrade`, `Prorated` |
| relid | int | Related ID (hosting.id or domain.id ตาม type) |
| description | text | รายละเอียด เช่น "Shared Hosting - example.com (01/01/2025 - 01/01/2026)" |
| amount | decimal | จำนวนเงิน |
| taxed | tinyint | เสีย VAT (1/0) |
| duedate | date | วันครบกำหนด |
| paymentmethod | varchar | วิธีชำระ |

> **Important**: `description` มักมีข้อมูล renewal เช่น "renewal", "ต่ออายุ" — ใช้ LIKE เพื่อแยก new vs renewal

---

### tblproducts

สินค้า/แพ็กเกจ

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Product ID |
| name | varchar | ชื่อสินค้า |
| type | enum | `hostingaccount`, `reselleraccount`, `server`, `other` |
| gid | int (FK) | → tblproductgroups.id |
| hidden | tinyint | ซ่อนจากหน้าสั่งซื้อ (1/0) |
| paytype | enum | `free`, `onetime`, `recurring` |
| retired | tinyint | เลิกขาย (1/0) |
| is_featured | tinyint | สินค้าแนะนำ (1/0) |

---

### tblproductgroups

กลุ่มสินค้า (Hosting, Domain, Email, VPS, etc.)

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Group ID |
| name | varchar | ชื่อกลุ่ม |
| slug | varchar | URL slug |
| hidden | tinyint | ซ่อน (1/0) |
| order | int | ลำดับการแสดง |

---

### tblorders

คำสั่งซื้อ

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Order ID |
| userid | int (FK) | → tblclients.id |
| ordernum | varchar | เลขคำสั่งซื้อ |
| date | datetime | วันที่สั่ง |
| amount | decimal | ยอดรวม |
| status | enum | `Active`, `Pending`, `Fraud`, `Cancelled` |
| paymentmethod | varchar | วิธีจ่าย |
| invoiceid | int (FK) | → tblinvoices.id |

---

## Status Codes

### tblclients.status
| Status | ความหมาย |
|--------|----------|
| `Active` | ใช้งานปกติ |
| `Inactive` | ไม่ active แต่ยังไม่ปิด |
| `Closed` | ปิดบัญชีแล้ว |

### tblhosting.domainstatus
| Status | ความหมาย |
|--------|----------|
| `Active` | ใช้งานปกติ |
| `Suspended` | ระงับ (ค้างจ่าย/ละเมิด) |
| `Terminated` | ยกเลิกถาวร |
| `Cancelled` | ลูกค้าขอยกเลิก |
| `Pending` | รอดำเนินการ |
| `Fraud` | ตรวจพบทุจริต |

### tbldomains.status
| Status | ความหมาย |
|--------|----------|
| `Active` | จดอยู่/ใช้งาน |
| `Expired` | หมดอายุ |
| `Cancelled` | ยกเลิก |
| `Pending` | รอจดทะเบียน |
| `Redemption` | ช่วง Redemption (ต้องจ่ายเพิ่มเพื่อกู้) |
| `Transferred Away` | ย้าย registrar |

### tblinvoices.status
| Status | ความหมาย |
|--------|----------|
| `Paid` | จ่ายแล้ว |
| `Unpaid` | ยังไม่จ่าย |
| `Cancelled` | ยกเลิก |
| `Refunded` | คืนเงิน |
| `Collections` | ส่งทวงหนี้ |
| `Draft` | ร่าง |

---

## Billing Cycles

| Cycle | ระยะเวลา | เดือน |
|-------|----------|------|
| `Monthly` | รายเดือน | 1 |
| `Quarterly` | ราย 3 เดือน | 3 |
| `Semi-Annually` | ราย 6 เดือน | 6 |
| `Annually` | รายปี | 12 |
| `Biennially` | ราย 2 ปี | 24 |
| `Triennially` | ราย 3 ปี | 36 |
| `Free Account` | ฟรี | - |

**Conversion**: ต้องการยอดรายปี → `amount * 12 / months`

---

## Product Type Categories

ใช้ `tblproductgroups.name` และ `tblproducts.type` เพื่อแยกประเภท:

| Category | เช็คจาก | ตัวอย่าง |
|----------|---------|---------|
| Hosting (Shared) | `p.type = 'hostingaccount'` | Shared Hosting, Web Hosting |
| VPS | `pg.name LIKE '%VPS%'` | Cloud VPS, VPS Hosting |
| Reseller | `p.type = 'reselleraccount'` | Reseller Hosting |
| Dedicated Server | `p.type = 'server'` | Dedicated Server |
| Email | `pg.name LIKE '%email%' OR p.name LIKE '%email%'` | Email Hosting, Google Workspace |
| Domain | ใช้ `tbldomains` ตรง | .com, .co.th |
| SSL | `pg.name LIKE '%SSL%'` | SSL Certificate |
| Website Builder | `pg.name LIKE '%website%'` | Website Builder |

---

## JOIN Patterns

### ลูกค้า → Hosting → Product
```sql
FROM tblclients c
JOIN tblhosting h ON h.userid = c.id
JOIN tblproducts p ON h.packageid = p.id
LEFT JOIN tblproductgroups pg ON p.gid = pg.id
```

### ลูกค้า → Domains
```sql
FROM tblclients c
JOIN tbldomains d ON d.userid = c.id
```

### ลูกค้า → Invoices → Invoice Items
```sql
FROM tblclients c
JOIN tblinvoices i ON i.userid = c.id
JOIN tblinvoiceitems ii ON ii.invoiceid = i.id
```

### Invoice Items → Hosting → Product (ดูรายได้ตาม product)
```sql
FROM tblinvoiceitems ii
JOIN tblinvoices i ON ii.invoiceid = i.id
JOIN tblhosting h ON ii.relid = h.id AND ii.type = 'Hosting'
JOIN tblproducts p ON h.packageid = p.id
```

### ลูกค้า → Orders → Invoices
```sql
FROM tblclients c
JOIN tblorders o ON o.userid = c.id
JOIN tblinvoices i ON o.invoiceid = i.id
```

---

## Common Query Patterns

### Customer Full Name (NULL-safe)
```sql
COALESCE(CONCAT(c.firstname, ' ', c.lastname), c.companyname) AS customer
```

### Resource Usage % (ป้องกัน division by zero)
```sql
ROUND(h.diskusage / NULLIF(h.disklimit, 0) * 100, 1) AS disk_pct
ROUND(h.bwusage / NULLIF(h.bwlimit, 0) * 100, 1) AS bw_pct
```

### Lifetime Value
```sql
(SELECT SUM(inv.total) FROM tblinvoices inv WHERE inv.userid = c.id AND inv.status = 'Paid') AS lifetime_value
```

### Days Until Due
```sql
DATEDIFF(h.nextduedate, CURDATE()) AS days_until_due
```

### New vs Renewal (from invoice items)
```sql
-- Renewal
ii.description LIKE '%renewal%' OR ii.description LIKE '%ต่ออายุ%'
-- New order (everything else)
ii.description NOT LIKE '%renewal%' AND ii.description NOT LIKE '%ต่ออายุ%'
```

### Year-over-Year
```sql
YEAR(datepaid) = YEAR(CURDATE())       -- ปีนี้
YEAR(datepaid) = YEAR(CURDATE()) - 1   -- ปีที่แล้ว
```