# Power BI Sales Analytics Dashboard Specification

This document provides a comprehensive, step-by-step implementation guide to build a professional, executive-grade Power BI dashboard using the exported Star Schema files.

---

## 1. Data Architecture & Modeling

### 1.1 Source Files
Import the following four CSV files located in the `powerbi/` folder:
- `fact_sales.csv` (Fact table: 3,025 rows, line-item grain)
- `dim_customers.csv` (Dimension table: 500 rows)
- `dim_products.csv` (Dimension table: 100 rows)
- `dim_date.csv` (Dimension table: 2,191 rows, full calendar 2021–2026)

### 1.2 Step-by-Step Power BI Setup

#### Step 1: Import CSVs into Power BI Desktop
1. Open **Power BI Desktop**.
2. Click **Get Data** > **Text/CSV**.
3. Load the four files: `fact_sales.csv`, `dim_customers.csv`, `dim_products.csv`, and `dim_date.csv`.
4. In **Power Query Editor**, verify data types:
   - `fact_sales`: `order_date` (Date), `quantity` (Whole number), `unit_price` (Decimal number), `revenue` (Decimal number).
   - `dim_date`: `Date` (Date), `Year` (Whole number), `QuarterNumber` (Whole number), `MonthNumber` (Whole number), `Day` (Whole number).
   - `dim_products`: `product_id` (Whole number), `price` (Decimal number).
   - `dim_customers`: `customer_id` (Whole number), `signup_date` (Date).
5. Click **Close & Apply**.

#### Step 2: Establish Model Relationships (Star Schema)
Switch to the **Model View** and configure relationships (Cardinals: **1-to-many**, Cross filter direction: **Single**):

| From Table (Dimension) | From Column | To Table (Fact) | To Column | Cardinality | Cross Filter |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `dim_date` | `Date` | `fact_sales` | `order_date` | 1 to Many (`1:*`) | Single (`dim_date` filters `fact_sales`) |
| `dim_products` | `product_id` | `fact_sales` | `product_id` | 1 to Many (`1:*`) | Single (`dim_products` filters `fact_sales`) |
| `dim_customers` | `customer_id` | `fact_sales` | `customer_id` | 1 to Many (`1:*`) | Single (`dim_customers` filters `fact_sales`) |

> **Best Practice Check**: Do not create relationships between dimensions. Keep the strict hub-and-spoke star schema architecture.

```
       +------------------+
       |   dim_customers  |
       +------------------+
                | 1
                | *
+------------+  |  +----------------+
|  dim_date  |--+--|   fact_sales   |
+------------+  |  +----------------+
      1         |         *
      *         |         1
       +------------------+
       |   dim_products   |
       +------------------+
```

#### Step 3: Mark as Date Table and Set Column Sort Orders
1. In the Fields pane, select the `dim_date` table.
2. In the top ribbon, click **Table Tools** > **Mark as date table**.
3. Select `Date` as the date column and click **OK**.
4. Configure column sorting to avoid alphabetical month/day issues:
   - Select `MonthName` > Ribbon **Column Tools** > **Sort by Column** > choose `MonthNumber`.
   - Select `MonthShort` > **Sort by Column** > choose `MonthNumber`.
   - Select `Quarter` > **Sort by Column** > choose `QuarterNumber`.
   - Select `DayName` > **Sort by Column** > choose `DayOfWeek`.

#### Step 4: Create Measure Table
1. In the Home ribbon, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Create each measure from [`powerbi/measures.dax`](./measures.dax) using the **New Measure** button.
4. Delete the empty default column `Column1` from `_Measures` so it displays a calculator icon at the top of the Fields pane.

---

## 2. Report Pages & Visual Specifications

Canvas Setting for all pages: **16:9 Aspect Ratio (1280 x 720 px)**, Off-white canvas background (`#F8FAFC`).

---

### Page 1: Executive Overview

**Purpose**: High-level executive pulse check on overall revenue trajectory, sales volume, and order throughput.

#### Top Filter / Slicer Banner
- **Slicer 1 (Date Range)**: `dim_date[Date]` (Between / Slider mode)
- **Slicer 2 (Product Category)**: `dim_products[category]` (Dropdown)
- **Slicer 3 (Order Status)**: `fact_sales[status]` (Dropdown or Tile selection)

#### KPI Cards Row (Top)
1. **Total Revenue**:
   - Measure: `[Total Revenue]`
   - Format: `$#,##0.00`
   - Sub-label: Overall Gross Sales
2. **Total Orders**:
   - Measure: `[Total Orders]`
   - Format: `#,##0`
3. **Units Sold**:
   - Measure: `[Units Sold]`
   - Format: `#,##0`
4. **Average Order Value (AOV)**:
   - Measure: `[Average Order Value]`
   - Format: `$#,##0.00`
5. **MoM Revenue Growth**:
   - Measure: `[Revenue MoM %]`
   - Format: `+0.0%;-0.0%;0.0%`
   - Conditional color: Green if `>= 0`, Red if `< 0`

#### Main Visuals
1. **Monthly Revenue & Prior Month Comparison (Line and Clustered Column Chart)**:
   - **X-axis**: `dim_date[YearMonth]`
   - **Column Y-axis**: `[Total Revenue]` (Color: Slate Navy `#1E293B`)
   - **Line Y-axis**: `[Revenue Previous Month]` (Color: Electric Cyan `#0EA5E9`)
   - **Data labels**: Enabled, concise format ($K / $M)
2. **Orders Volume Trend by Month (Area or Clustered Column Chart)**:
   - **X-axis**: `dim_date[YearMonth]`
   - **Y-axis**: `[Total Orders]`
   - **Color**: Royal Indigo (`#6366F1`)
3. **Order Status Distribution (Donut Chart)**:
   - **Legend**: `fact_sales[status]`
   - **Values**: `[Total Orders]`
   - **Data Labels**: Category & Percentage of total

---

### Page 2: Product Performance

**Purpose**: Deep-dive into catalog profitability, high-velocity items, and category revenue distribution.

#### Top Slicers
- **Date Slicer**: `dim_date[Date]`
- **Category Slicer**: `dim_products[category]`

#### Summary KPIs
1. **Catalog Active Products**: Count of `dim_products[product_id]`
2. **Top 10 Product Revenue Share**: `[Top 10 Product Revenue Share]` (Percentage format `0.0%`)
3. **Units Sold**: `[Units Sold]`

#### Visuals
1. **Top 10 Products by Revenue (Horizontal Clustered Bar Chart)**:
   - **Y-axis**: `dim_products[product_name]`
   - **X-axis**: `[Total Revenue]`
   - **Filter Pane**: Visual-level filter on `product_name` > Filter type: Top N > Top 10 by `[Total Revenue]`
   - **Bar Color**: Gradient fill based on `[Total Revenue]`
2. **Revenue by Category (Donut Chart or Treemap)**:
   - **Category/Group**: `dim_products[category]`
   - **Values**: `[Total Revenue]`
   - **Data Labels**: Category Name and Value ($)
3. **Product Performance Matrix Table**:
   - **Rows**: `dim_products[product_id]`, `dim_products[product_name]`, `dim_products[category]`
   - **Values**:
     - `Unit Price`: `Average of dim_products[price]`
     - `Units Sold`: `[Units Sold]`
     - `Total Revenue`: `[Total Revenue]`
     - `AOV Contribution`: `[Average Order Value]`
   - **Conditional Formatting**:
     - `Total Revenue`: Data bars in Blue/Cyan (`#0EA5E9`)
     - `Units Sold`: Soft green font or background gradient

---

### Page 3: Customer Insights

**Purpose**: Assess customer acquisition, repeat buyer retention, and geographical concentration.

#### Top Slicers
- **Date Slicer**: `dim_date[Date]`
- **City Slicer**: `dim_customers[city]` (Searchable dropdown)

#### Summary KPIs
1. **Unique Customers**: `[Unique Customers]`
2. **Repeat Customer Rate**: `[Repeat Customer Rate]` (Format: `0.0%`)
3. **Average Customer Lifetime Value**: `DIVIDE([Total Revenue], [Unique Customers], 0)`

#### Visuals
1. **Repeat vs One-Time Customers Breakdown (Donut Chart)**:
   - Visual calculation / Measure grouping:
     - Repeat buyers (`> 1` order) vs One-time buyers (`= 1` order)
   - **Legend**: Segment
   - **Values**: Customer Count
2. **Top Customers by Lifetime Revenue (Horizontal Bar Chart or Card Table)**:
   - **Y-axis / Rows**: `dim_customers[customer_name]`, `dim_customers[city]`
   - **X-axis / Values**: `[Total Revenue]`, `[Total Orders]`
   - **Visual Filter**: Top 10 by `[Total Revenue]`
3. **Geographical Revenue & Order Distribution (Clustered Bar Chart or Map)**:
   - **Y-axis / Location**: `dim_customers[city]`
   - **X-axis / Size**: `[Total Revenue]`
   - **Tooltips**: `[Total Orders]`, `[Unique Customers]`
   - **Sorting**: Descending by `[Total Revenue]`

---

## 3. Visual & Styling Design System

### 3.1 Color Palette
Use a modern, executive theme (Dark Slate / Slate Blue / Electric Accent):

| Role | Color Name | Hex Code | Usage |
| :--- | :--- | :--- | :--- |
| **Primary** | Midnight Slate | `#0F172A` | Page header, titles, primary text |
| **Secondary** | Deep Blue | `#1E293B` | Main chart columns, cards, primary series |
| **Accent Primary**| Electric Cyan | `#0EA5E9` | Trend lines, active highlights, data bars |
| **Accent Secondary**| Royal Indigo | `#6366F1` | Secondary chart series, secondary KPIs |
| **Positive / Growth** | Emerald Green | `#10B981` | Positive MoM growth, target exceedance |
| **Alert / Cancel**| Crimson Red | `#EF4444` | Negative growth, cancelled orders |
| **Card Fill** | Crisp Card Surface| `#FFFFFF` | Background fill for all visual containers |
| **Canvas Fill** | Cool Slate Grey | `#F8FAFC` | Page background |
| **Border / Divider**| Subtle Slate | `#E2E8F0` | Visual card outline (1px, radius 8px) |

### 3.2 Typography & Sizing
- **Report Title**: Segoe UI Bold, 20 pt, `#0F172A`
- **Section / Visual Titles**: Segoe UI Semibold, 13 pt, `#1E293B`
- **KPI Callout Values**: Segoe UI Bold, 24 pt, `#0F172A`
- **KPI Sub-labels / Data Labels**: Segoe UI Regular, 9–10 pt, `#64748B`
- **Table / Matrix Grid**: Segoe UI Regular, 10 pt

### 3.3 Layout & Card Styling Guidelines
1. **Card Container Polish**: Give all visual cards a clean 8px border-radius, 1px border stroke in `#E2E8F0`, and soft drop shadow (Offset 2px, Blur 4px, Color `#00000010`).
2. **Padding**: Maintain at least 12px margin between adjacent visual cards for a clean, non-cluttered executive layout.
3. **Interaction**: Set Cross-Filtering to **Cross-Highlight** on categorical charts and **Filter** on slicers.
