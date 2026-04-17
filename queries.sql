USE ecommerce_dw;

-- ==========================================
-- 1. Top Customers Based on Total Spending
-- Demonstrates: INNER JOIN, GROUP BY, SUM, ORDER BY, LIMIT
-- ==========================================
SELECT 
    c.customer_id, 
    c.name, 
    c.city, 
    SUM(p.amount) AS total_spent
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN payments p ON o.order_id = p.order_id
GROUP BY c.customer_id, c.name, c.city
ORDER BY total_spent DESC
LIMIT 10;

-- ==========================================
-- 2. Monthly Revenue Trends
-- Demonstrates: Date formatting, Aggregations, GROUP BY
-- ==========================================
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') AS order_month, 
    SUM(p.amount) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS number_of_orders
FROM orders o
INNER JOIN payments p ON o.order_id = p.order_id
WHERE o.status != 'Cancelled'
GROUP BY order_month
ORDER BY order_month;

-- ==========================================
-- 3. Top-Selling Products by Category
-- Demonstrates: Window Functions (RANK), CTE (Common Table Expression)
-- ==========================================
WITH CategorySales AS (
    SELECT 
        pr.category,
        pr.product_id,
        pr.name,
        SUM(oi.quantity) AS total_quantity_sold,
        SUM(oi.quantity * oi.price) AS total_revenue
    FROM products pr
    INNER JOIN order_items oi ON pr.product_id = oi.product_id
    INNER JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status != 'Cancelled'
    GROUP BY pr.category, pr.product_id, pr.name
),
RankedProducts AS (
    SELECT 
        category,
        name,
        total_quantity_sold,
        total_revenue,
        RANK() OVER(PARTITION BY category ORDER BY total_quantity_sold DESC) as sales_rank
    FROM CategorySales
)
SELECT * 
FROM RankedProducts 
WHERE sales_rank <= 3;

-- ==========================================
-- 4. Customer Purchase Frequency Analysis
-- Demonstrates: Subqueries, CASE WHEN, Aggregations
-- ==========================================
SELECT 
    purchase_frequency_segment,
    COUNT(customer_id) as number_of_customers
FROM (
    SELECT 
        customer_id,
        COUNT(order_id) as total_orders,
        CASE
            WHEN COUNT(order_id) = 1 THEN 'One-time Buyer'
            WHEN COUNT(order_id) BETWEEN 2 AND 5 THEN 'Occasional Buyer'
            WHEN COUNT(order_id) > 5 THEN 'Frequent Buyer'
            ELSE 'No Orders'
        END AS purchase_frequency_segment
    FROM orders
    GROUP BY customer_id
) AS CustomerFrequency
GROUP BY purchase_frequency_segment;

-- ==========================================
-- 5. Order Status Distribution by City (Pivot-like analysis)
-- Demonstrates: complex join structure
-- ==========================================
SELECT 
    c.city,
    COUNT(o.order_id) as total_orders,
    SUM(CASE WHEN o.status = 'Completed' THEN 1 ELSE 0 END) AS completed_orders,
    SUM(CASE WHEN o.status = 'Shipped' THEN 1 ELSE 0 END) AS shipped_orders,
    SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.city
ORDER BY total_orders DESC
LIMIT 10;

-- ==========================================
-- 6. Performance Optimization Demonstration (EXPLAIN)
-- Demonstrates: Use of EXPLAIN to view the query execution plan
-- Notes: If the customer_id in 'orders' did not have an index,
-- the EXPLAIN plan would show a full table scan instead of using the index.
-- ==========================================
EXPLAIN SELECT 
    o.order_id, 
    o.order_date, 
    c.name 
FROM orders o 
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.customer_id = 15;
