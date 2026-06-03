# Data Dictionary - Bluestock Mutual Fund Analytics Database

**Database:** `bluestock_mf.db` (SQLite)  
**Created:** Day 2 - Data Cleaning & Database Design  
**Version:** 1.0  
**Last Updated:** 2026-06-03  

---

## Table of Contents

1. [Overview](#overview)
2. [Dimension Tables](#dimension-tables)
3. [Fact Tables](#fact-tables)
4. [Relationships & Keys](#relationships--keys)
5. [Data Quality Rules](#data-quality-rules)
6. [Business Definitions](#business-definitions)

---

## Overview

This is a **Star Schema** database designed for analyzing Mutual Fund performance, transactions, and investor behavior. It consists of:

- **4 Dimension Tables:** dim_fund, dim_date, dim_investor
- **4 Fact Tables:** fact_nav, fact_transactions, fact_performance, fact_aum

The schema enables efficient analytical queries while maintaining data integrity through foreign keys.

---

## Dimension Tables

### 1. **dim_fund** - Fund Master Data

**Purpose:** Central repository for fund attributes and characteristics  
**Primary Key:** `fund_id` (Integer, auto-increment)  
**Source:** fund_master.csv (from Bluestock)

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| fund_id | INTEGER | NO | Unique identifier for each fund (auto-increment) |
| amfi_code | VARCHAR(10) | NO | AMFI scheme code - Unique identifier assigned by Association of Mutual Funds in India |
| fund_name | VARCHAR(255) | NO | Full name of the mutual fund scheme |
| fund_house | VARCHAR(100) | NO | Name of the asset management company (AMC) managing the fund |
| category | VARCHAR(50) | YES | Fund category (Equity, Debt, Hybrid, etc.) |
| sub_category | VARCHAR(50) | YES | Sub-category of the fund (Large Cap, Small Cap, Government Securities, etc.) |
| risk_grade | VARCHAR(10) | YES | Risk classification (Low, Moderate, High, Very High) |
| launch_date | DATE | YES | Date when the fund was first launched |
| created_at | TIMESTAMP | NO | System timestamp when record was created |

**Sample Data:**
```
fund_id | amfi_code | fund_name | fund_house | category | sub_category | risk_grade | launch_date
1 | 125497 | HDFC Top 100 Direct | HDFC Asset Management | Equity | Large Cap | Moderate | 2005-01-15
2 | 119551 | SBI Bluechip Fund | SBI Funds Management | Equity | Large Cap | Moderate | 2004-08-20
```

**Key Properties:**
- UNIQUE constraint on amfi_code (no duplicates)
- One fund can have multiple NAV records, transactions, and performance records

---

### 2. **dim_date** - Calendar Dimension

**Purpose:** Enables time-based analysis and reporting  
**Primary Key:** `date_id` (Integer, auto-increment)

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| date_id | INTEGER | NO | Unique date identifier |
| date | DATE | NO | Actual calendar date (YYYY-MM-DD) |
| year | INTEGER | YES | Calendar year (e.g., 2026) |
| month | INTEGER | YES | Month of year (1-12) |
| day | INTEGER | YES | Day of month (1-31) |
| quarter | INTEGER | YES | Quarter of year (1-4) |
| day_of_week | VARCHAR(10) | YES | Day name (Monday, Tuesday, etc.) |
| is_weekend | INTEGER | YES | Binary flag (1=weekend, 0=weekday) |
| created_at | TIMESTAMP | NO | System timestamp |

**Sample Data:**
```
date_id | date | year | month | day | quarter | day_of_week | is_weekend
1 | 2026-01-01 | 2026 | 1 | 1 | 1 | Thursday | 0
2 | 2026-01-02 | 2026 | 1 | 2 | 1 | Friday | 0
```

**Key Properties:**
- UNIQUE constraint on date
- Used for all time-based joins (no transaction dates in fact tables directly)
- Enables YoY and seasonal analysis

---

### 3. **dim_investor** - Investor Master Data

**Purpose:** Store investor profile and verification status  
**Primary Key:** `investor_id` (Integer, auto-increment)  
**Source:** investor_transactions.csv

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| investor_id | INTEGER | NO | Unique identifier for investor |
| investor_key | VARCHAR(50) | YES | External investor identifier (PAN/AADHAR masked) |
| kyc_status | VARCHAR(20) | YES | Know Your Customer status (APPROVED, PENDING, REJECTED, VERIFIED) |
| investor_state | VARCHAR(50) | YES | State of residence (Geographic location) |
| investor_type | VARCHAR(50) | YES | Type of investor (Individual, HUF, Partnership, Company) |
| created_at | TIMESTAMP | NO | System timestamp |

**Sample Data:**
```
investor_id | investor_key | kyc_status | investor_state | investor_type
1 | PAN_XXXX1234 | APPROVED | Maharashtra | Individual
2 | PAN_XXXX5678 | VERIFIED | Karnataka | Individual
```

**Key Properties:**
- UNIQUE constraint on investor_key (external identifier)
- KYC status must be one of: APPROVED, PENDING, REJECTED, VERIFIED
- Used for regulatory compliance tracking

---

## Fact Tables

### 4. **fact_nav** - Net Asset Value History

**Purpose:** Daily NAV values for all funds  
**Primary Key:** `nav_id` (Integer, auto-increment)  
**Foreign Keys:** fund_id (→ dim_fund), date_id (→ dim_date)  
**Source:** nav_history.csv

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| nav_id | INTEGER | NO | Unique identifier for NAV record |
| fund_id | INTEGER | NO | Reference to dim_fund |
| date_id | INTEGER | NO | Reference to dim_date |
| nav_value | FLOAT | NO | Net Asset Value (price per unit) in INR |
| updated_at | TIMESTAMP | NO | System timestamp |

**Data Quality Rules:**
- nav_value MUST be > 0
- (fund_id, date_id) must be unique - no duplicate NAV for same fund on same date
- Forward-filled for holidays/weekends

**Sample Data:**
```
nav_id | fund_id | date_id | nav_value | updated_at
1 | 1 | 100 | 1250.50 | 2026-06-01 14:30:00
2 | 1 | 101 | 1251.25 | 2026-06-02 14:30:00
```

**Typical Queries:**
- Track fund prices over time
- Calculate returns
- Identify price trends

---

### 5. **fact_transactions** - Investor Transactions

**Purpose:** Record of all investor purchase/redemption transactions  
**Primary Key:** `transaction_id` (Integer, auto-increment)  
**Foreign Keys:** investor_id, fund_id, date_id  
**Source:** investor_transactions.csv

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| transaction_id | INTEGER | NO | Unique transaction identifier |
| investor_id | INTEGER | NO | Reference to dim_investor |
| fund_id | INTEGER | NO | Reference to dim_fund |
| date_id | INTEGER | NO | Reference to dim_date (transaction date) |
| transaction_type | VARCHAR(20) | NO | Type of transaction: SIP, LUMPSUM, REDEMPTION, SWITCH |
| amount | FLOAT | NO | Transaction amount in INR |
| units | FLOAT | YES | Number of units purchased/redeemed |
| created_at | TIMESTAMP | NO | System timestamp |

**Data Quality Rules:**
- amount MUST be > 0
- transaction_type must be one of: SIP, LUMPSUM, REDEMPTION, SWITCH
- units typically = amount / NAV (calculated field optional)

**Sample Data:**
```
transaction_id | investor_id | fund_id | date_id | transaction_type | amount | units
1001 | 1 | 1 | 150 | LUMPSUM | 50000.00 | 39.96
1002 | 2 | 2 | 151 | SIP | 5000.00 | 4.12
```

**Transaction Types:**
- **SIP:** Systematic Investment Plan (recurring monthly/quarterly)
- **LUMPSUM:** One-time investment
- **REDEMPTION:** Withdrawal from fund
- **SWITCH:** Transfer between funds

---

### 6. **fact_performance** - Fund Performance Metrics

**Purpose:** Performance returns and expense ratios  
**Primary Key:** `performance_id` (Integer, auto-increment)  
**Foreign Keys:** fund_id, date_id  
**Source:** scheme_performance.csv

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| performance_id | INTEGER | NO | Unique identifier |
| fund_id | INTEGER | NO | Reference to dim_fund |
| date_id | INTEGER | NO | Reference to dim_date (as of date) |
| return_1m | FLOAT | YES | Returns for last 1 month (%) |
| return_3m | FLOAT | YES | Returns for last 3 months (%) |
| return_6m | FLOAT | YES | Returns for last 6 months (%) |
| return_1y | FLOAT | YES | Returns for last 1 year (%) |
| return_3y | FLOAT | YES | Returns for last 3 years annualized (%) |
| return_5y | FLOAT | YES | Returns for last 5 years annualized (%) |
| expense_ratio | FLOAT | YES | Annual expense ratio (%) - Range: 0.1% to 2.5% |
| created_at | TIMESTAMP | NO | System timestamp |

**Data Quality Rules:**
- All return values must be numeric
- expense_ratio must be between 0.1% and 2.5%
- (fund_id, date_id) must be unique

**Sample Data:**
```
performance_id | fund_id | date_id | return_1y | return_3y | expense_ratio
1 | 1 | 200 | 15.5 | 12.3 | 0.45
2 | 2 | 200 | 14.2 | 11.8 | 0.50
```

**Return Calculations:**
- Simple Returns: (Current Value - Initial Value) / Initial Value × 100
- Annualized Returns: ((Ending Value / Beginning Value) ^ (1/years) - 1) × 100
- CAGR: Compound Annual Growth Rate

---

### 7. **fact_aum** - Assets Under Management

**Purpose:** Track fund size and growth over time  
**Primary Key:** `aum_id` (Integer, auto-increment)  
**Foreign Keys:** fund_id, date_id  
**Source:** aum_history.csv

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| aum_id | INTEGER | NO | Unique identifier |
| fund_id | INTEGER | NO | Reference to dim_fund |
| date_id | INTEGER | NO | Reference to dim_date (as of date) |
| aum_value | FLOAT | NO | Assets Under Management in INR (Crores) |
| aum_units | FLOAT | YES | Total units outstanding |
| created_at | TIMESTAMP | NO | System timestamp |

**Data Quality Rules:**
- aum_value MUST be > 0
- (fund_id, date_id) must be unique

**Sample Data:**
```
aum_id | fund_id | date_id | aum_value | aum_units
1 | 1 | 200 | 50000.00 | 40000000
2 | 2 | 200 | 35000.00 | 30000000
```

**Business Meaning:**
- Larger AUM typically indicates fund popularity and stability
- Rapid AUM growth can indicate strong investor interest
- Declining AUM may indicate redemptions or performance issues

---

## Relationships & Keys

### Foreign Key Relationships

```
fact_nav
  ├── fund_id → dim_fund.fund_id
  └── date_id → dim_date.date_id

fact_transactions
  ├── investor_id → dim_investor.investor_id
  ├── fund_id → dim_fund.fund_id
  └── date_id → dim_date.date_id

fact_performance
  ├── fund_id → dim_fund.fund_id
  └── date_id → dim_date.date_id

fact_aum
  ├── fund_id → dim_fund.fund_id
  └── date_id → dim_date.date_id
```

### Indexes for Performance

```sql
CREATE INDEX idx_nav_fund_date ON fact_nav(fund_id, date_id);
CREATE INDEX idx_txn_investor ON fact_transactions(investor_id);
CREATE INDEX idx_txn_fund ON fact_transactions(fund_id);
CREATE INDEX idx_perf_fund ON fact_performance(fund_id);
CREATE INDEX idx_aum_fund ON fact_aum(fund_id);
```

---

## Data Quality Rules

### Validation Rules by Table

| Table | Column | Rule | Error Handling |
|-------|--------|------|----------------|
| fact_nav | nav_value | > 0 | Remove invalid records |
| fact_transactions | amount | > 0 | Remove invalid records |
| fact_transactions | transaction_type | IN (SIP, LUMPSUM, REDEMPTION, SWITCH) | Standardize or flag |
| fact_performance | expense_ratio | 0.1 to 2.5 | Remove out-of-range |
| dim_investor | kyc_status | IN (APPROVED, PENDING, REJECTED, VERIFIED) | Log anomalies |
| dim_date | is_weekend | IN (0, 1) | Binary validation |

### Missing Data Handling

- **NAV:** Forward-filled for holidays/weekends
- **Returns:** NULL if calculation not possible
- **Investor State:** NULL allowed (location may be unknown)
- **Risk Grade:** NULL allowed if not classified

---

## Business Definitions

### Key Metrics

**1. Net Asset Value (NAV)**
- Definition: Price of one unit of a mutual fund
- Calculation: (Total Assets - Total Liabilities) / Total Units Outstanding
- Unit: Indian Rupees (₹)
- Frequency: Updated daily after market close

**2. Assets Under Management (AUM)**
- Definition: Total value of assets managed by a fund
- Calculation: NAV × Total Units Outstanding
- Unit: Indian Rupees in Crores (₹Cr)
- Business Use: Measure fund size and popularity

**3. Return Metrics**
- **1M Return:** Return over last 1 month
- **3M Return:** Return over last 3 months
- **1Y Return:** Return over last 1 year
- **3Y Return:** Annualized return over 3 years
- **5Y Return:** Annualized return over 5 years

**4. Expense Ratio**
- Definition: Annual percentage charged by fund house
- Range: 0.1% - 2.5% (Indian market standard)
- Impact: Reduces investor returns
- Example: 0.45% means ₹45 per ₹10,000 invested annually

**5. Transaction Types**
- **SIP (Systematic Investment Plan):** Regular, recurring investments (monthly/quarterly)
- **LUMPSUM:** One-time, large investment
- **REDEMPTION:** Withdrawal/selling of units
- **SWITCH:** Moving funds between different schemes

### Fund Categories (Indian Mutual Fund Market)

| Category | Sub-Category | Risk Level | Typical Returns |
|----------|--------------|-----------|-----------------|
| Equity | Large Cap | Moderate | 12-15% |
| Equity | Mid Cap | High | 15-20% |
| Equity | Small Cap | Very High | 18-25% |
| Equity | Multi Cap | Moderate-High | 14-18% |
| Debt | Government Securities | Low | 5-7% |
| Debt | Corporate Bonds | Low-Moderate | 6-8% |
| Hybrid | Balanced | Moderate | 8-12% |
| Hybrid | Aggressive | High | 10-15% |

### Risk Grades (SEBI Classification)

- **Low:** Government bonds, liquid funds, short-term debt
- **Moderate:** Large-cap equity, balanced funds
- **High:** Mid-cap equity, sector funds
- **Very High:** Small-cap, micro-cap, leveraged funds

---

## Data Lineage & Sources

| Table | Source File | Extraction Frequency | Last Updated |
|-------|----------|------|------|
| dim_fund | fund_master.csv | Monthly | 2026-06-03 |
| fact_nav | nav_history.csv | Daily | 2026-06-03 |
| fact_transactions | investor_transactions.csv | Daily | 2026-06-03 |
| fact_performance | scheme_performance.csv | Daily | 2026-06-03 |
| fact_aum | aum_history.csv | Monthly | 2026-06-03 |
| dim_investor | investor_transactions.csv | Real-time | 2026-06-03 |

---

## Common Analytical Queries

### Example 1: Top 5 Funds by AUM
```sql
SELECT fund_name, AVG(aum_value) as avg_aum
FROM fact_aum 
JOIN dim_fund USING(fund_id)
GROUP BY fund_id
ORDER BY avg_aum DESC
LIMIT 5;
```

### Example 2: YoY SIP Growth
```sql
SELECT strftime('%Y', date) as year, SUM(amount) as sip_volume
FROM fact_transactions
JOIN dim_date ON date_id
WHERE transaction_type = 'SIP'
GROUP BY year;
```

### Example 3: Best Funds by 1-Year Return
```sql
SELECT fund_name, return_1y, expense_ratio
FROM fact_performance
JOIN dim_fund USING(fund_id)
WHERE return_1y IS NOT NULL
ORDER BY return_1y DESC
LIMIT 10;
```

---

## Data Refresh Schedule

- **Daily:** NAV, Performance, Transactions
- **Weekly:** Aggregated analytics
- **Monthly:** AUM, Fund Master updates
- **Quarterly:** Deep analysis, anomaly detection

---

## Contact & Maintenance

**Database Administrator:** Bluestock Analytics Team  
**Last Updated:** 2026-06-03  
**Version:** 1.0  
**Next Review:** 2026-07-03
