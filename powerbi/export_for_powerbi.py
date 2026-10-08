"""
powerbi/export_for_powerbi.py
Star Schema Data Transformation and Export for Power BI Desktop

Purpose:
Loads the relational e-commerce dataset, constructs an analytical Star Schema,
and exports clean CSV files to the `/powerbi` directory:
  - fact_sales.csv (Sales transactions grain: order line items)
  - dim_customers.csv (Customer profile dimension)
  - dim_products.csv (Product catalog dimension)
  - dim_date.csv (Continuous date dimension for Time Intelligence)

Also prints summary metrics (row counts, total revenue) for cross-checking in Power BI.
"""

import os
import argparse
import pandas as pd
import numpy as np

def build_star_schema(input_dir=".", output_dir="powerbi"):
    """
    Transforms relational CSV tables into a clean Power BI Star Schema.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("POWER BI STAR SCHEMA EXPORT PIPELINE")
    print(f"Reading source data from : {os.path.abspath(input_dir)}")
    print(f"Writing Star Schema to   : {os.path.abspath(output_dir)}")
    print("=" * 60)
    
    # 1. Read source CSVs
    customers_df = pd.read_csv(os.path.join(input_dir, "customers.csv"))
    products_df = pd.read_csv(os.path.join(input_dir, "products.csv"))
    orders_df = pd.read_csv(os.path.join(input_dir, "orders.csv"))
    order_items_df = pd.read_csv(os.path.join(input_dir, "order_items.csv"))
    
    # 2. Build Fact Table: fact_sales
    # Grain: 1 row per order line item
    fact_sales = order_items_df.merge(
        orders_df[["order_id", "customer_id", "order_date", "status"]],
        on="order_id",
        how="inner"
    )
    
    # Standardize column naming and compute line revenue
    fact_sales["unit_price"] = fact_sales["price"].round(2)
    fact_sales["revenue"] = (fact_sales["quantity"] * fact_sales["unit_price"]).round(2)
    
    fact_sales = fact_sales[[
        "order_item_id",
        "order_id",
        "order_date",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "revenue",
        "status"
    ]].sort_values(by=["order_id", "order_item_id"])
    
    # 3. Build Dimension Table: dim_customers
    dim_customers = customers_df.copy()
    dim_customers = dim_customers.rename(columns={"name": "customer_name"})
    dim_customers = dim_customers[[
        "customer_id",
        "customer_name",
        "city",
        "signup_date"
    ]].sort_values(by="customer_id")
    
    # 4. Build Dimension Table: dim_products
    dim_products = products_df.copy()
    dim_products = dim_products.rename(columns={"name": "product_name"})
    dim_products["price"] = dim_products["price"].round(2)
    dim_products = dim_products[[
        "product_id",
        "product_name",
        "category",
        "price"
    ]].sort_values(by="product_id")
    
    # 5. Build Continuous Dimension Table: dim_date
    # Find min and max date across orders and customer signups
    all_dates = pd.concat([
        pd.to_datetime(orders_df["order_date"]),
        pd.to_datetime(customers_df["signup_date"])
    ])
    
    # Anchor to start of first year and end of last year for full calendar year integrity
    min_year = all_dates.min().year
    max_year = all_dates.max().year
    
    start_calendar = f"{min_year}-01-01"
    end_calendar = f"{max_year}-12-31"
    
    date_range = pd.date_range(start=start_calendar, end=end_calendar, freq="D")
    
    dim_date = pd.DataFrame({"Date": date_range})
    dim_date["Year"] = dim_date["Date"].dt.year
    dim_date["QuarterNumber"] = dim_date["Date"].dt.quarter
    dim_date["Quarter"] = "Q" + dim_date["QuarterNumber"].astype(str)
    dim_date["MonthNumber"] = dim_date["Date"].dt.month
    dim_date["MonthName"] = dim_date["Date"].dt.strftime("%B")
    dim_date["MonthShort"] = dim_date["Date"].dt.strftime("%b")
    dim_date["YearMonth"] = dim_date["Date"].dt.strftime("%Y-%m")
    dim_date["WeekNumber"] = dim_date["Date"].dt.isocalendar().week.astype(int)
    dim_date["Day"] = dim_date["Date"].dt.day
    dim_date["DayOfWeek"] = dim_date["Date"].dt.dayofweek + 1  # 1 = Monday, 7 = Sunday
    dim_date["DayName"] = dim_date["Date"].dt.strftime("%A")
    dim_date["IsWeekend"] = dim_date["DayOfWeek"].isin([6, 7]).astype(int)
    
    # Format Date column as YYYY-MM-DD
    dim_date["Date"] = dim_date["Date"].dt.strftime("%Y-%m-%d")
    
    # 6. Save Star Schema CSV files to output_dir
    fact_sales_path = os.path.join(output_dir, "fact_sales.csv")
    dim_customers_path = os.path.join(output_dir, "dim_customers.csv")
    dim_products_path = os.path.join(output_dir, "dim_products.csv")
    dim_date_path = os.path.join(output_dir, "dim_date.csv")
    
    fact_sales.to_csv(fact_sales_path, index=False)
    dim_customers.to_csv(dim_customers_path, index=False)
    dim_products.to_csv(dim_products_path, index=False)
    dim_date.to_csv(dim_date_path, index=False)
    
    # 7. Print summary and reconciliation metrics
    total_gross_revenue = fact_sales["revenue"].sum()
    net_sales_df = fact_sales[fact_sales["status"] != "Cancelled"]
    total_net_revenue = net_sales_df["revenue"].sum()
    total_orders = fact_sales["order_id"].nunique()
    total_units = fact_sales["quantity"].sum()
    unique_customers = fact_sales["customer_id"].nunique()
    
    print("\n" + "=" * 60)
    print("STAR SCHEMA EXPORT COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("Exported Files & Row Counts:")
    print(f"  • fact_sales.csv     : {len(fact_sales):>6} rows")
    print(f"  • dim_customers.csv  : {len(dim_customers):>6} rows")
    print(f"  • dim_products.csv   : {len(dim_products):>6} rows")
    print(f"  • dim_date.csv       : {len(dim_date):>6} rows (Range: {start_calendar} to {end_calendar})")
    print("\nBenchmark Totals (for Power BI Verification):")
    print(f"  • Total Gross Revenue (All Orders)       : ${total_gross_revenue:,.2f}")
    print(f"  • Total Net Revenue (Excl. Cancelled)   : ${total_net_revenue:,.2f}")
    print(f"  • Cancelled Order Revenue               : ${fact_sales[fact_sales['status'] == 'Cancelled']['revenue'].sum():,.2f}")
    print(f"  • Total Orders                          : {total_orders:,}")
    print(f"  • Total Units Sold                      : {total_units:,}")
    print(f"  • Unique Customers with Orders          : {unique_customers:,}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Star Schema CSVs for Power BI")
    parser.add_argument("--input-dir", default=".", help="Directory containing source CSVs (default: .)")
    parser.add_argument("--output-dir", default="powerbi", help="Output directory for Star Schema CSVs (default: powerbi)")
    args = parser.parse_args()
    
    build_star_schema(input_dir=args.input_dir, output_dir=args.output_dir)
