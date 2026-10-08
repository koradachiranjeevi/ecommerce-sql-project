-- ========================================================================
-- E-COMMERCE BUSINESS INTELLIGENCE (BI) ANALYTICAL VIEWS
-- Database: ecommerce_dw (MySQL 8.0+)
--
-- This script creates reporting views that serve as the analytical foundation
-- for BI tools, SQL dashboards, and Power BI data models.
-- ========================================================================

USE ecommerce_dw;

-- ========================================================================
-- 1. Sales Fact View: vw_sales_fact
-- Denormalized line-item level transaction view joining order_items, orders,
-- products, and customers. Revenue is computed as quantity * unit price.
-- ========================================================================
CREATE OR REPLACE VIEW vw_sales_fact AS
SELECT 
    oi.order_item_id,
    o.order_id,
    o.order_date,
    o.customer_id,
    c.name AS customer_name,
    c.city AS customer_city,
    c.signup_date AS customer_signup_date,
    oi.product_id,
    p.name AS product_name,
    p.category AS product_category,
    oi.quantity,
    oi.price AS unit_price,
    ROUND(oi.quantity * oi.price, 2) AS line_revenue,
    o.status AS order_status
FROM order_items oi
INNER JOIN orders o 
    ON oi.order_id = o.order_id
INNER JOIN products p 
    ON oi.product_id = p.product_id
INNER JOIN customers c 
    ON o.customer_id = c.customer_id;


-- ========================================================================
-- 2. Monthly Revenue View: vw_monthly_revenue
-- Aggregates revenue, order volume, and average order value (AOV) by month.
-- Excludes cancelled orders for net performance reporting.
-- ========================================================================
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') AS order_month,
    YEAR(o.order_date) AS order_year,
    MONTH(o.order_date) AS order_month_num,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.quantity * oi.price), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * oi.price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
INNER JOIN order_items oi 
    ON o.order_id = oi.order_id
WHERE o.status != 'Cancelled'
GROUP BY 
    DATE_FORMAT(o.order_date, '%Y-%m'),
    YEAR(o.order_date),
    MONTH(o.order_date)
ORDER BY order_month ASC;


-- ========================================================================
-- 3. Product Performance View: vw_product_performance
-- Detailed product performance metrics with total units sold, gross/net
-- revenue, order count, and revenue ranking (overall & within category)
-- using MySQL 8 Window Functions (RANK()).
-- ========================================================================
CREATE OR REPLACE VIEW vw_product_performance AS
WITH product_aggregated_sales AS (
    SELECT 
        p.product_id,
        p.name AS product_name,
        p.category,
        p.price AS catalog_price,
        COALESCE(SUM(CASE WHEN o.status != 'Cancelled' THEN oi.quantity ELSE 0 END), 0) AS total_units_sold,
        COUNT(DISTINCT CASE WHEN o.status != 'Cancelled' THEN o.order_id END) AS total_orders,
        ROUND(COALESCE(SUM(CASE WHEN o.status != 'Cancelled' THEN oi.quantity * oi.price ELSE 0 END), 0), 2) AS total_revenue,
        ROUND(AVG(CASE WHEN o.status != 'Cancelled' THEN oi.quantity END), 2) AS avg_units_per_order
    FROM products p
    LEFT JOIN order_items oi 
        ON p.product_id = oi.product_id
    LEFT JOIN orders o 
        ON oi.order_id = o.order_id
    GROUP BY 
        p.product_id, 
        p.name, 
        p.category, 
        p.price
)
SELECT 
    product_id,
    product_name,
    category,
    catalog_price,
    total_units_sold,
    total_orders,
    total_revenue,
    avg_units_per_order,
    RANK() OVER (ORDER BY total_revenue DESC) AS overall_revenue_rank,
    RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS category_revenue_rank
FROM product_aggregated_sales;


-- ========================================================================
-- 4. Customer Summary View: vw_customer_summary
-- Comprehensive customer profile covering total completed orders, lifetime
-- revenue, first order date, last order date, and repeat customer classification.
-- ========================================================================
CREATE OR REPLACE VIEW vw_customer_summary AS
SELECT 
    c.customer_id,
    c.name AS customer_name,
    c.city,
    c.signup_date,
    COUNT(DISTINCT CASE WHEN o.status != 'Cancelled' THEN o.order_id END) AS total_orders,
    COALESCE(SUM(CASE WHEN o.status != 'Cancelled' THEN oi.quantity ELSE 0 END), 0) AS total_units_purchased,
    ROUND(COALESCE(SUM(CASE WHEN o.status != 'Cancelled' THEN oi.quantity * oi.price ELSE 0 END), 0), 2) AS lifetime_revenue,
    MIN(CASE WHEN o.status != 'Cancelled' THEN o.order_date END) AS first_order_date,
    MAX(CASE WHEN o.status != 'Cancelled' THEN o.order_date END) AS last_order_date,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN o.status != 'Cancelled' THEN o.order_id END) > 1 THEN 1 
        ELSE 0 
    END AS repeat_flag,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN o.status != 'Cancelled' THEN o.order_id END) = 0 THEN 'No Orders'
        WHEN COUNT(DISTINCT CASE WHEN o.status != 'Cancelled' THEN o.order_id END) = 1 THEN 'One-time Customer'
        ELSE 'Repeat Customer'
    END AS customer_segment
FROM customers c
LEFT JOIN orders o 
    ON c.customer_id = o.customer_id
LEFT JOIN order_items oi 
    ON o.order_id = oi.order_id
GROUP BY 
    c.customer_id, 
    c.name, 
    c.city, 
    c.signup_date;
