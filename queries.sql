-- Day 2: 10 Analytical SQL Queries for Mutual Fund Analytics
-- ============================================================

-- QUERY 1: Top 5 Funds by AUM
-- Purpose: Identify largest funds by Assets Under Management
SELECT 
    df.fund_name,
    df.fund_house,
    df.category,
    ROUND(AVG(fa.aum_value), 2) as avg_aum,
    ROUND(MAX(fa.aum_value), 2) as max_aum,
    COUNT(DISTINCT fa.date_id) as num_records
FROM fact_aum fa
JOIN dim_fund df ON fa.fund_id = df.fund_id
GROUP BY fa.fund_id, df.fund_name, df.fund_house, df.category
ORDER BY avg_aum DESC
LIMIT 5;

-- ============================================================

-- QUERY 2: Average NAV per Month for Top Fund
-- Purpose: Track NAV trends monthly for the largest fund
SELECT 
    strftime('%Y-%m', dd.date) as month,
    ROUND(AVG(fn.nav_value), 2) as avg_nav,
    ROUND(MIN(fn.nav_value), 2) as min_nav,
    ROUND(MAX(fn.nav_value), 2) as max_nav,
    COUNT(DISTINCT fn.date_id) as trading_days
FROM fact_nav fn
JOIN dim_date dd ON fn.date_id = dd.date_id
JOIN dim_fund df ON fn.fund_id = df.fund_id
WHERE df.fund_name LIKE '%Top 100%'
GROUP BY strftime('%Y-%m', dd.date)
ORDER BY month DESC;

-- ============================================================

-- QUERY 3: SIP Year-over-Year Growth
-- Purpose: Compare SIP transaction volumes YoY
SELECT 
    strftime('%Y', dd.date) as year,
    strftime('%m', dd.date) as month,
    COUNT(DISTINCT ft.transaction_id) as sip_count,
    ROUND(SUM(ft.amount), 2) as sip_volume,
    ROUND(AVG(ft.amount), 2) as avg_sip_amount
FROM fact_transactions ft
JOIN dim_date dd ON ft.date_id = dd.date_id
WHERE ft.transaction_type = 'SIP'
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- ============================================================

-- QUERY 4: Transactions by State
-- Purpose: Geographic distribution of investor transactions
SELECT 
    di.investor_state,
    COUNT(DISTINCT ft.transaction_id) as transaction_count,
    COUNT(DISTINCT ft.investor_id) as investor_count,
    ROUND(SUM(ft.amount), 2) as total_amount,
    ROUND(AVG(ft.amount), 2) as avg_transaction_amount
FROM fact_transactions ft
JOIN dim_investor di ON ft.investor_id = di.investor_id
WHERE di.investor_state IS NOT NULL
GROUP BY di.investor_state
ORDER BY total_amount DESC;

-- ============================================================

-- QUERY 5: Funds with Expense Ratio < 1%
-- Purpose: Identify low-cost fund options
SELECT 
    df.fund_name,
    df.fund_house,
    df.category,
    ROUND(AVG(fp.expense_ratio), 3) as avg_expense_ratio,
    ROUND(MAX(fp.return_1y), 2) as return_1y,
    ROUND(MAX(fp.return_3y), 2) as return_3y,
    COUNT(DISTINCT fp.date_id) as num_records
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
GROUP BY fp.fund_id, df.fund_name, df.fund_house, df.category
HAVING AVG(fp.expense_ratio) < 1.0
ORDER BY avg_expense_ratio ASC;

-- ============================================================

-- QUERY 6: Redemption vs Lumpsum Ratio by Fund
-- Purpose: Analyze investor behavior (buying vs selling)
SELECT 
    df.fund_name,
    df.fund_house,
    SUM(CASE WHEN ft.transaction_type = 'LUMPSUM' THEN ft.amount ELSE 0 END) as lumpsum_amount,
    SUM(CASE WHEN ft.transaction_type = 'REDEMPTION' THEN ft.amount ELSE 0 END) as redemption_amount,
    COUNT(CASE WHEN ft.transaction_type = 'LUMPSUM' THEN 1 END) as lumpsum_count,
    COUNT(CASE WHEN ft.transaction_type = 'REDEMPTION' THEN 1 END) as redemption_count,
    ROUND(
        SUM(CASE WHEN ft.transaction_type = 'LUMPSUM' THEN ft.amount ELSE 0 END) /
        NULLIF(SUM(CASE WHEN ft.transaction_type = 'REDEMPTION' THEN ft.amount ELSE 0 END), 0),
        2
    ) as inflow_outflow_ratio
FROM fact_transactions ft
JOIN dim_fund df ON ft.fund_id = df.fund_id
GROUP BY ft.fund_id, df.fund_name, df.fund_house
HAVING lumpsum_amount > 0 AND redemption_amount > 0
ORDER BY inflow_outflow_ratio DESC;

-- ============================================================

-- QUERY 7: Best Performing Funds by 1-Year Return
-- Purpose: Identify top performers in the last year
SELECT 
    df.fund_name,
    df.fund_house,
    df.category,
    ROUND(MAX(fp.return_1y), 2) as best_1y_return,
    ROUND(AVG(fp.return_1y), 2) as avg_1y_return,
    ROUND(AVG(fp.expense_ratio), 3) as expense_ratio,
    ROUND(MAX(fp.return_1y) - AVG(fp.expense_ratio), 2) as net_return_after_expense
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
WHERE fp.return_1y IS NOT NULL
GROUP BY fp.fund_id, df.fund_name, df.fund_house, df.category
ORDER BY net_return_after_expense DESC
LIMIT 10;

-- ============================================================

-- QUERY 8: Risk Grade Distribution with Average Returns
-- Purpose: Analyze risk vs return relationship
SELECT 
    df.risk_grade,
    COUNT(DISTINCT df.fund_id) as fund_count,
    ROUND(AVG(fp.return_1y), 2) as avg_1y_return,
    ROUND(AVG(fp.return_3y), 2) as avg_3y_return,
    ROUND(AVG(fp.expense_ratio), 3) as avg_expense_ratio,
    ROUND(AVG(fa.aum_value), 2) as avg_aum
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
LEFT JOIN fact_aum fa ON fp.fund_id = fa.fund_id
GROUP BY df.risk_grade
ORDER BY df.risk_grade;

-- ============================================================

-- QUERY 9: Investor KYC Status Distribution
-- Purpose: Monitor investor verification status
SELECT 
    di.kyc_status,
    COUNT(DISTINCT di.investor_id) as investor_count,
    COUNT(DISTINCT ft.transaction_id) as transaction_count,
    ROUND(SUM(ft.amount), 2) as total_investment,
    ROUND(AVG(ft.amount), 2) as avg_investment,
    ROUND(SUM(ft.amount) / COUNT(DISTINCT di.investor_id), 2) as avg_per_investor
FROM dim_investor di
LEFT JOIN fact_transactions ft ON di.investor_id = ft.investor_id
GROUP BY di.kyc_status
ORDER BY investor_count DESC;

-- ============================================================

-- QUERY 10: Fund Category Performance Comparison
-- Purpose: Compare performance across different fund categories
SELECT 
    df.category,
    COUNT(DISTINCT df.fund_id) as fund_count,
    ROUND(AVG(fp.return_1y), 2) as avg_1y_return,
    ROUND(AVG(fp.return_3y), 2) as avg_3y_return,
    ROUND(MAX(fp.return_1y), 2) as best_1y_return,
    ROUND(MIN(fp.return_1y), 2) as worst_1y_return,
    ROUND(STDDEV(fp.return_1y), 2) as return_volatility,
    ROUND(AVG(fp.expense_ratio), 3) as avg_expense_ratio,
    ROUND(SUM(fa.aum_value) / COUNT(DISTINCT fa.date_id), 2) as avg_category_aum
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
LEFT JOIN fact_aum fa ON fp.fund_id = fa.fund_id AND fp.date_id = fa.date_id
WHERE fp.return_1y IS NOT NULL
GROUP BY df.category
ORDER BY avg_1y_return DESC;

-- ============================================================
-- ADDITIONAL USEFUL QUERIES
-- ============================================================

-- Query A: Latest NAV for All Funds
SELECT 
    df.fund_name,
    fn.nav_value,
    dd.date
FROM fact_nav fn
JOIN dim_fund df ON fn.fund_id = df.fund_id
JOIN dim_date dd ON fn.date_id = dd.date_id
WHERE dd.date = (SELECT MAX(date) FROM dim_date)
ORDER BY df.fund_name;

-- Query B: Monthly Transaction Volume Trend
SELECT 
    strftime('%Y-%m', dd.date) as month,
    COUNT(DISTINCT ft.transaction_id) as total_transactions,
    ROUND(SUM(ft.amount), 2) as total_amount,
    COUNT(DISTINCT df.category) as categories_active
FROM fact_transactions ft
JOIN dim_date dd ON ft.date_id = dd.date_id
JOIN dim_fund df ON ft.fund_id = df.fund_id
GROUP BY strftime('%Y-%m', dd.date)
ORDER BY month DESC;
