# E-Commerce SQL & Power BI Analytics Project

An end-to-end data analytics and business intelligence project demonstrating database schema design, analytical SQL in MySQL 8.0, star schema dimensional modeling, automated ETL export pipelines using Python/pandas, and an executive-ready multi-page Power BI dashboard design.

---

## Project Overview

This project simulates a real-world e-commerce data platform. Starting from normalized transactional data (customers, orders, products, order items), the platform provides:
1. **Relational Data Warehouse & SQL Analytics**: Database schema, referential integrity, indexes, and analytical queries in MySQL (`schema.sql`, `queries.sql`).
2. **Business Intelligence (BI) SQL Layer**: Reusable MySQL 8 analytical views (`bi/views.sql`) providing denormalized fact tables, monthly summaries, product rankings, and customer metrics.
3. **Automated Star Schema ETL Pipeline**: A pandas-driven export script (`powerbi/export_for_powerbi.py`) that generates dimension tables, fact tables, and a continuous calendar table for Time Intelligence.
4. **Power BI Modeling & DAX Measures**: Ready-to-use DAX measures (`powerbi/measures.dax`) and an end-to-end dashboard specification (`powerbi/DASHBOARD_SPEC.md`) for building an interactive sales intelligence dashboard in Power BI Desktop.

---

## Architecture

```
+-----------------------------------------------------------------------------------+
|                                 DATA INGESTION                                    |
|   Raw Relational CSVs (customers, products, orders, order_items)                  |
|   [Optional: Synthetic Scaled Data via generate_data.py -> /data]                 |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                            MYSQL 8.0 RELATIONAL DW                                |
|   schema.sql  -> Database schema, primary & foreign keys, performance indexes    |
|   queries.sql -> Analytical queries (Window functions, CTEs, Aggregations)        |
|   bi/views.sql-> Analytical BI Views (vw_sales_fact, vw_monthly_revenue, etc.)     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                           PYTHON / PANDAS ETL LAYER                               |
|   powerbi/export_for_powerbi.py -> Star Schema Builder                            |
|     - Transforms transactions into Fact & Dimension structures                    |
|     - Generates continuous Dim Date calendar for Time Intelligence                |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                            POWER BI DESKTOP LAYER                                 |
|   Star Schema CSVs: fact_sales, dim_customers, dim_products, dim_date             |
|   DAX Measures Library: powerbi/measures.dax (Total Revenue, MoM %, YTD, AOV, etc.)|
|   Dashboard Design: powerbi/DASHBOARD_SPEC.md                                     |
|     * Page 1: Executive Overview                                                  |
|     * Page 2: Product Performance                                                 |
|     * Page 3: Customer Insights                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Tables & Schemas

### Relational Schema (MySQL)
- **`customers`** (`customer_id` PK, `name`, `city`, `signup_date`): 500 rows.
- **`products`** (`product_id` PK, `name`, `category`, `price`): 100 rows.
- **`orders`** (`order_id` PK, `customer_id` FK, `order_date`, `status`): 1,000 rows spanning May 2021 to April 2026.
- **`order_items`** (`order_item_id` PK, `order_id` FK, `product_id` FK, `quantity`, `price`): 3,025 line items.
- **`payments`** (Defined in `schema.sql` for transaction tracking).

### Generated Sample Data (`/data/`)
- A deterministic, seeded generator (`generate_data.py`) is provided. If larger volumes are required, it synthesizes realistic orders across 24+ months with verified referential integrity into the `/data` folder without modifying the original root CSVs.

### MySQL BI Views (`bi/views.sql`)
- **`vw_sales_fact`**: Denormalized line-item level transaction fact table with calculated revenue (`quantity * unit_price`).
- **`vw_monthly_revenue`**: Monthly aggregation of gross and net revenue, order volume, and Average Order Value (AOV).
- **`vw_product_performance`**: Aggregated product performance with overall and category revenue rankings using MySQL 8 `RANK()` window functions.
- **`vw_customer_summary`**: Customer lifetime metrics, order counts, first/last purchase dates, and repeat buyer flags.

---

## How to Run

### 1. MySQL Database & Views Setup
1. Open MySQL Workbench or your terminal:
   ```bash
   mysql -u root -p < schema.sql
   ```
2. Import the root CSV files (`customers.csv`, `products.csv`, `orders.csv`, `order_items.csv`) into their respective MySQL tables.
3. Run the analytical queries:
   ```bash
   mysql -u root -p ecommerce_dw < queries.sql
   ```
4. Deploy the BI analytical views:
   ```bash
   mysql -u root -p ecommerce_dw < bi/views.sql
   ```

### 2. (Optional) Generate Expanded Sample Data
To generate extra realistic orders into a separate `/data` folder:
```bash
python generate_data.py
```
*(Original CSVs remain completely untouched).*

### 3. Export Star Schema for Power BI
Run the export script to transform relational files into an optimized dimensional star schema:
```bash
python powerbi/export_for_powerbi.py
```
This writes the following Star Schema files to `powerbi/`:
- `powerbi/fact_sales.csv` (3,025 rows)
- `powerbi/dim_customers.csv` (500 rows)
- `powerbi/dim_products.csv` (100 rows)
- `powerbi/dim_date.csv` (2,191 rows: continuous calendar 2021–2026)

The script prints summary totals (gross revenue, net revenue, order counts) for verification against Power BI.

### 4. Build Dashboard in Power BI Desktop
1. Open **Power BI Desktop** and follow the step-by-step instructions in [`powerbi/DASHBOARD_SPEC.md`](powerbi/DASHBOARD_SPEC.md).
2. Load the CSVs from the `powerbi/` folder.
3. Establish 1-to-many single relationships between dimensions (`dim_customers`, `dim_products`, `dim_date`) and the fact table (`fact_sales`).
4. Mark `dim_date` as the official Date Table.
5. Create a `_Measures` table and copy the DAX measures from [`powerbi/measures.dax`](powerbi/measures.dax).
6. Build the 3 report pages: **Executive Overview**, **Product Performance**, and **Customer Insights**.

---

## Power BI Dashboard

Follow [`powerbi/DASHBOARD_SPEC.md`](powerbi/DASHBOARD_SPEC.md) to build the 3 report pages. Place your dashboard export screenshots inside `docs/images/` to display them here:

### 1. Executive Overview
Key performance indicators (Revenue, Orders, Units Sold, AOV, MoM Growth), monthly revenue trend with previous month comparison, and order fulfillment breakdown.

![Executive Overview](docs/images/executive_overview.png)

### 2. Product Performance
Top 10 revenue-generating products, category revenue distribution, and detailed catalog matrix table with conditional data bars.

![Product Performance](docs/images/product_performance.png)

### 3. Customer Insights
New vs. repeat customer distribution, top lifetime spending customers, and geographic order concentration by city.

![Customer Insights](docs/images/customer_insights.png)

---

## Key Insights

> *Note: Metrics below are placeholders to be filled after viewing the interactive dashboard.*

- **Executive Revenue Trend**: `[fill after viewing dashboard]`
- **Top Category & Product Contribution**: `[fill after viewing dashboard]`
- **Customer Repeat Rate & Retention**: `[fill after viewing dashboard]`
- **Geographic Order Concentration**: `[fill after viewing dashboard]`
- **Order Fulfillment / Cancellation Rate**: `[fill after viewing dashboard]`

---

## Tools & Technologies
- **Database**: MySQL 8.0 / MySQL Workbench
- **ETL & Data Processing**: Python 3, Pandas, NumPy
- **Data Modeling & BI**: Power BI Desktop, DAX (Data Analysis Expressions)
- **Architecture**: Star Schema Dimensional Modeling
