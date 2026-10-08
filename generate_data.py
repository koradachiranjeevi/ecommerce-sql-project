"""
generate_data.py
Synthetic Data Generator for E-Commerce Analytics Project

Purpose:
Adds realistic extra orders and line items to expand the dataset across at least 24 months
while preserving strict relational integrity (valid foreign keys, order_date >= signup_date,
realistic status distributions, and product pricing).

Output:
Saves the augmented dataset into the `/data` directory, leaving the original CSVs untouched.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set random seeds for deterministic, reproducible data generation
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

def generate_augmented_data(
    base_dir=".",
    output_dir="./data",
    extra_orders_count=1000,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2025, 12, 31)
):
    """
    Generates realistic extra orders and order items and saves them alongside
    customers and products in output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load original data
    customers_path = os.path.join(base_dir, "customers.csv")
    products_path = os.path.join(base_dir, "products.csv")
    orders_path = os.path.join(base_dir, "orders.csv")
    order_items_path = os.path.join(base_dir, "order_items.csv")
    
    customers_df = pd.read_csv(customers_path)
    products_df = pd.read_csv(products_path)
    orders_df = pd.read_csv(orders_path)
    order_items_df = pd.read_csv(order_items_path)
    
    print(f"Loaded existing data:")
    print(f" - Customers: {len(customers_df)} rows")
    print(f" - Products: {len(products_df)} rows")
    print(f" - Orders: {len(orders_df)} rows")
    print(f" - Order Items: {len(order_items_df)} rows")
    
    # Ensure signup_date is datetime for validation
    customers_df["signup_date_dt"] = pd.to_datetime(customers_df["signup_date"])
    customer_signups = dict(zip(customers_df["customer_id"], customers_df["signup_date_dt"]))
    
    # Product lookup for prices
    product_price_map = dict(zip(products_df["product_id"], products_df["price"]))
    product_ids = products_df["product_id"].tolist()
    customer_ids = customers_df["customer_id"].tolist()
    
    # Order status choices with realistic weights matching empirical data
    statuses = ["Completed", "Shipped", "Processing", "Cancelled"]
    status_weights = [0.72, 0.15, 0.09, 0.04]
    
    max_order_id = orders_df["order_id"].max()
    max_item_id = order_items_df["order_item_id"].max()
    
    total_days = (end_date - start_date).days
    
    new_orders = []
    new_order_items = []
    
    current_order_id = max_order_id + 1
    current_item_id = max_item_id + 1
    
    for _ in range(extra_orders_count):
        cust_id = random.choice(customer_ids)
        signup_dt = customer_signups[cust_id]
        
        # Pick order date between max(start_date, signup_dt) and end_date
        effective_start = max(start_date, signup_dt)
        if effective_start >= end_date:
            random_days = random.randint(0, 30)
            order_dt = effective_start + timedelta(days=random_days)
        else:
            diff = (end_date - effective_start).days
            order_dt = effective_start + timedelta(days=random.randint(0, diff))
            
        status = random.choices(statuses, weights=status_weights)[0]
        
        new_orders.append({
            "order_id": current_order_id,
            "customer_id": cust_id,
            "order_date": order_dt.strftime("%Y-%m-%d"),
            "status": status
        })
        
        # 1 to 4 items per order
        num_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.35, 0.15, 0.05])[0]
        chosen_products = random.sample(product_ids, k=min(num_items, len(product_ids)))
        
        for pid in chosen_products:
            qty = random.choices([1, 2, 3, 4, 5], weights=[0.50, 0.25, 0.15, 0.07, 0.03])[0]
            price = product_price_map[pid]
            new_order_items.append({
                "order_item_id": current_item_id,
                "order_id": current_order_id,
                "product_id": pid,
                "quantity": qty,
                "price": price
            })
            current_item_id += 1
            
        current_order_id += 1
        
    extra_orders_df = pd.DataFrame(new_orders)
    extra_order_items_df = pd.DataFrame(new_order_items)
    
    # Combined augmented datasets
    augmented_orders_df = pd.concat([orders_df, extra_orders_df], ignore_index=True)
    augmented_order_items_df = pd.concat([order_items_df, extra_order_items_df], ignore_index=True)
    
    # Drop helper column before export
    clean_customers_df = customers_df.drop(columns=["signup_date_dt"])
    
    # Write to /data directory
    clean_customers_df.to_csv(os.path.join(output_dir, "customers.csv"), index=False)
    products_df.to_csv(os.path.join(output_dir, "products.csv"), index=False)
    augmented_orders_df.to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    augmented_order_items_df.to_csv(os.path.join(output_dir, "order_items.csv"), index=False)
    
    print(f"\nSuccessfully generated augmented dataset in '{output_dir}':")
    print(f" - Total Orders: {len(augmented_orders_df)} (Original: {len(orders_df)} + Extra: {len(extra_orders_df)})")
    print(f" - Total Order Items: {len(augmented_order_items_df)} (Original: {len(order_items_df)} + Extra: {len(extra_order_items_df)})")
    print(f" - Augmented Order Date Range: {augmented_orders_df['order_date'].min()} to {augmented_orders_df['order_date'].max()}")
    print(" - Original files remain completely untouched.")

if __name__ == "__main__":
    generate_augmented_data()
