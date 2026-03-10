# WHMCS Database Schema Reference

Complete schema for the WHMCS tables available for querying.

---

## tblclients — Customers

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Client ID |
| firstname | varchar | First name |
| lastname | varchar | Last name |
| companyname | varchar | Company name |
| email | varchar | Email address |
| phonenumber | varchar | Phone number |
| address1 | varchar | Address line 1 |
| address2 | varchar | Address line 2 |
| city | varchar | City |
| state | varchar | State/Province |
| postcode | varchar | Postal code |
| country | varchar(2) | Country code (TH, US, etc.) |
| status | enum | `Active`, `Inactive`, `Closed` |
| datecreated | date | Account creation date |
| notes | text | Admin notes |
| currency | int | Currency ID (FK → tblcurrencies.id) |
| language | varchar | Preferred language |

---

## tblhosting — Hosting Services (Subscriptions)

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Service ID |
| userid | int (FK) | → tblclients.id |
| packageid | int (FK) | → tblproducts.id |
| domain | varchar | Domain on this hosting |
| domainstatus | enum | `Active`, `Suspended`, `Terminated`, `Pending`, `Cancelled` |
| regdate | date | Registration/order date |
| nextduedate | date | Next billing due date |
| amount | decimal | Recurring amount |
| billingcycle | varchar | `Monthly`, `Quarterly`, `Semi-Annually`, `Annually`, `Biennially`, `Free Account` |
| dedicatedip | varchar | Dedicated IP |
| server | int | Server ID |
| username | varchar | Hosting username |
| password | varchar | Hosting password (encrypted) |

---

## tbldomains — Domains

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Domain ID |
| userid | int (FK) | → tblclients.id |
| domain | varchar | Full domain name |
| status | enum | `Active`, `Pending`, `Expired`, `Cancelled`, `Transferred Away` |
| registrationdate | date | Registration date |
| expirydate | date | Expiry date |
| nextduedate | date | Next due date |
| registrar | varchar | Registrar module name |
| registrationperiod | int | Registration period (years) |
| recurringamount | decimal | Renewal amount |

---

## tblinvoices — Invoices

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Invoice ID |
| userid | int (FK) | → tblclients.id |
| invoicenum | varchar | Invoice number |
| date | date | Invoice date |
| duedate | date | Due date |
| datepaid | datetime | Date paid (NULL if unpaid) |
| status | enum | `Paid`, `Unpaid`, `Cancelled`, `Refunded`, `Collections` |
| subtotal | decimal | Subtotal |
| credit | decimal | Credit applied |
| tax | decimal | Tax amount |
| tax2 | decimal | Tax 2 amount |
| total | decimal | Grand total |
| paymentmethod | varchar | Payment method |
| notes | text | Invoice notes |

---

## tblinvoiceitems — Invoice Line Items

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Item ID |
| invoiceid | int (FK) | → tblinvoices.id |
| userid | int (FK) | → tblclients.id |
| type | varchar | `Hosting`, `Domain`, `DomainRegister`, `DomainTransfer`, `Addon`, etc. |
| relid | int | Related service/domain ID |
| description | text | Item description |
| amount | decimal | Item amount |
| taxed | tinyint | Whether taxed (1/0) |
| duedate | date | Item due date |
| paymentmethod | varchar | Payment method |

---

## tblproducts — Products

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Product ID |
| gid | int (FK) | → tblproductgroups.id |
| type | enum | `hostingaccount`, `reselleraccount`, `server`, `other` |
| name | varchar | Product name |
| description | text | Product description |
| hidden | tinyint | Hidden from order (1/0) |
| paytype | enum | `free`, `onetime`, `recurring` |
| pricing | text | Pricing config (serialized) |

---

## tblproductgroups — Product Groups

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Group ID |
| name | varchar | Group name |
| headline | text | Headline text |
| tagline | text | Tagline text |
| orderfrmtpl | varchar | Order form template |
| hidden | tinyint | Hidden (1/0) |

---

## tblorders — Orders

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Order ID |
| userid | int (FK) | → tblclients.id |
| ordernum | varchar | Order number |
| date | datetime | Order date |
| amount | decimal | Order total |
| status | enum | `Active`, `Pending`, `Fraud`, `Cancelled` |
| paymentmethod | varchar | Payment method |
| invoiceid | int (FK) | → tblinvoices.id |

---

## tbltickets — Support Tickets

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Ticket ID |
| userid | int (FK) | → tblclients.id |
| tid | varchar | Ticket number |
| date | datetime | Created date |
| title | varchar | Ticket subject |
| message | text | Ticket message |
| status | enum | `Open`, `Answered`, `Customer-Reply`, `Closed`, `On Hold` |
| urgency | enum | `Low`, `Medium`, `High` |
| lastreply | datetime | Last reply timestamp |

---

## tblcurrencies — Currencies

| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Currency ID |
| code | varchar(3) | Currency code (THB, USD, etc.) |
| prefix | varchar | Display prefix (฿, $) |
| suffix | varchar | Display suffix |
| rate | decimal | Exchange rate |
| default | tinyint | Default currency (1/0) |

---

## Relationships Diagram

```
tblclients
    │
    ├── tblhosting (userid = tblclients.id)
    │       └── tblproducts (packageid = tblproducts.id)
    │               └── tblproductgroups (gid = tblproductgroups.id)
    │
    ├── tbldomains (userid = tblclients.id)
    │
    ├── tblinvoices (userid = tblclients.id)
    │       └── tblinvoiceitems (invoiceid = tblinvoices.id)
    │
    ├── tblorders (userid = tblclients.id)
    │       └── tblinvoices (tblorders.invoiceid = tblinvoices.id)
    │
    ├── tbltickets (userid = tblclients.id)
    │
    └── tblcurrencies (tblclients.currency = tblcurrencies.id)
```

---

## Common Query Patterns

### Revenue by Month
```sql
SELECT DATE_FORMAT(datepaid, '%Y-%m') AS month, 
       SUM(total) AS revenue
FROM tblinvoices 
WHERE status = 'Paid' 
GROUP BY month 
ORDER BY month DESC
```

### Customer Lifetime Value
```sql
SELECT c.id, CONCAT(c.firstname, ' ', c.lastname) AS customer,
       SUM(i.total) AS lifetime_value, COUNT(i.id) AS invoice_count
FROM tblclients c
JOIN tblinvoices i ON c.id = i.userid
WHERE i.status = 'Paid'
GROUP BY c.id
ORDER BY lifetime_value DESC
LIMIT 20
```

### Product Popularity
```sql
SELECT p.name, pg.name AS group_name, COUNT(h.id) AS subscriptions
FROM tblproducts p
JOIN tblproductgroups pg ON p.gid = pg.id
LEFT JOIN tblhosting h ON h.packageid = p.id
GROUP BY p.id
ORDER BY subscriptions DESC
```

### Churn Analysis (Terminated in Last 90 Days)
```sql
SELECT p.name AS product, COUNT(h.id) AS churned
FROM tblhosting h
JOIN tblproducts p ON h.packageid = p.id
WHERE h.domainstatus = 'Terminated'
GROUP BY p.id
ORDER BY churned DESC
```