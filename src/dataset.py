"""
Dataset loader and generator for the E-Commerce Knowledge Graph.
Generates comprehensive sample data covering:
- Products
- Brands
- Categories
- Vendors
- Orders
- Customers

Strict Requirement:
The word "banana" is added as a node/value in the knowledge graph EXACTLY 5 times:
1. Product Name: "Banana"
2. Brand Name: "Banana"
3. Category Name: "Banana"
4. Vendor Name: "Banana"
5. Customer Name: "Banana"
"""

import json
import os
import csv
from typing import Dict, Any, List


SAMPLE_DATA: Dict[str, List[Dict[str, Any]]] = {
    "brands": [
        {"id": "B01", "name": "Apple", "country": "USA", "rating": 4.9},
        {"id": "B02", "name": "Samsung", "country": "South Korea", "rating": 4.7},
        {"id": "B03", "name": "Sony", "country": "Japan", "rating": 4.8},
        {"id": "B04", "name": "TechCore", "country": "Germany", "rating": 4.6},
        {"id": "B05", "name": "ComfortLine", "country": "Sweden", "rating": 4.4},
        # Occurrence 1 of 'Banana'
        {"id": "B06", "name": "Banana", "country": "Ecuador", "rating": 4.9}
    ],
    "categories": [
        {"id": "C01", "name": "Electronics", "department": "Hardware"},
        {"id": "C02", "name": "Audio", "department": "Entertainment"},
        {"id": "C03", "name": "Home & Kitchen", "department": "Living"},
        {"id": "C04", "name": "Furniture", "department": "Office"},
        {"id": "C05", "name": "Home Entertainment", "department": "Living"},
        # Occurrence 2 of 'Banana'
        {"id": "C06", "name": "Banana", "department": "Fresh Produce"}
    ],
    "vendors": [
        {"id": "V01", "name": "Foxconn Logistics", "country": "Taiwan", "lead_time_days": 4},
        {"id": "V02", "name": "Apex Global Supplies", "country": "Singapore", "lead_time_days": 3},
        {"id": "V03", "name": "Pacific Freight Partners", "country": "USA", "lead_time_days": 5},
        {"id": "V04", "name": "Metro Wholesale Hub", "country": "United Kingdom", "lead_time_days": 6},
        # Occurrence 3 of 'Banana'
        {"id": "V05", "name": "Banana", "country": "Costa Rica", "lead_time_days": 2}
    ],
    "products": [
        {"id": "P01", "name": "MacBook Pro 16", "price": 2499.00, "brand_id": "B01", "category_id": "C01", "vendor_id": "V01", "stock": 45},
        {"id": "P02", "name": "iPhone 15 Pro", "price": 1199.00, "brand_id": "B01", "category_id": "C01", "vendor_id": "V01", "stock": 80},
        {"id": "P03", "name": "Galaxy S24 Ultra", "price": 1299.00, "brand_id": "B02", "category_id": "C01", "vendor_id": "V02", "stock": 60},
        {"id": "P04", "name": "OLED 4K Smart TV", "price": 1499.00, "brand_id": "B03", "category_id": "C05", "vendor_id": "V02", "stock": 25},
        {"id": "P05", "name": "AirPods Pro 2", "price": 249.00, "brand_id": "B01", "category_id": "C02", "vendor_id": "V03", "stock": 110},
        {"id": "P06", "name": "WH-1000XM5 Headphones", "price": 399.00, "brand_id": "B03", "category_id": "C02", "vendor_id": "V03", "stock": 40},
        {"id": "P07", "name": "Smart Air Fryer Pro", "price": 189.00, "brand_id": "B04", "category_id": "C03", "vendor_id": "V02", "stock": 70},
        {"id": "P08", "name": "Ergonomic Office Chair", "price": 349.00, "brand_id": "B05", "category_id": "C04", "vendor_id": "V04", "stock": 30},
        {"id": "P09", "name": "Wireless Mechanical Keyboard", "price": 129.00, "brand_id": "B04", "category_id": "C01", "vendor_id": "V02", "stock": 95},
        {"id": "P10", "name": "Ultra-Quiet Humidifier", "price": 79.00, "brand_id": "B04", "category_id": "C03", "vendor_id": "V03", "stock": 50},
        # Occurrence 4 of 'Banana'
        {"id": "P11", "name": "Banana", "price": 1.49, "brand_id": "B06", "category_id": "C06", "vendor_id": "V05", "stock": 500}
    ],
    "customers": [
        {"id": "U01", "name": "Alice Smith", "email": "alice.smith@example.com", "loyalty_tier": "Gold"},
        {"id": "U02", "name": "Bob Johnson", "email": "bob.johnson@example.com", "loyalty_tier": "Silver"},
        {"id": "U03", "name": "Charlie Brown", "email": "charlie.brown@example.com", "loyalty_tier": "Platinum"},
        {"id": "U04", "name": "Diana Prince", "email": "diana.prince@example.com", "loyalty_tier": "Bronze"},
        {"id": "U05", "name": "Evan Wright", "email": "evan.wright@example.com", "loyalty_tier": "Gold"},
        # Occurrence 5 of 'Banana'
        {"id": "U06", "name": "Banana", "email": "client.tropical@freshmail.org", "loyalty_tier": "VIP"}
    ],
    "orders": [
        {
            "id": "O01",
            "customer_id": "U01",
            "order_date": "2026-03-01",
            "items": [{"product_id": "P01", "quantity": 1, "unit_price": 2499.00}, {"product_id": "P05", "quantity": 1, "unit_price": 249.00}],
            "total_amount": 2748.00,
            "status": "DELIVERED"
        },
        {
            "id": "O02",
            "customer_id": "U02",
            "order_date": "2026-03-04",
            "items": [{"product_id": "P03", "quantity": 1, "unit_price": 1299.00}],
            "total_amount": 1299.00,
            "status": "DELIVERED"
        },
        {
            "id": "O03",
            "customer_id": "U03",
            "order_date": "2026-03-08",
            "items": [
                {"product_id": "P04", "quantity": 1, "unit_price": 1499.00},
                {"product_id": "P06", "quantity": 1, "unit_price": 399.00},
                {"product_id": "P07", "quantity": 1, "unit_price": 189.00}
            ],
            "total_amount": 2087.00,
            "status": "DELIVERED"
        },
        {
            "id": "O04",
            "customer_id": "U04",
            "order_date": "2026-03-12",
            "items": [
                {"product_id": "P09", "quantity": 1, "unit_price": 129.00},
                {"product_id": "P08", "quantity": 1, "unit_price": 349.00}
            ],
            "total_amount": 478.00,
            "status": "DELIVERED"
        },
        {
            "id": "O05",
            "customer_id": "U05",
            "order_date": "2026-03-15",
            "items": [
                {"product_id": "P10", "quantity": 1, "unit_price": 79.00},
                {"product_id": "P05", "quantity": 1, "unit_price": 249.00}
            ],
            "total_amount": 328.00,
            "status": "DELIVERED"
        },
        {
            "id": "O06",
            "customer_id": "U06",
            "order_date": "2026-03-20",
            "items": [
                {"product_id": "P11", "quantity": 10, "unit_price": 1.49}
            ],
            "total_amount": 14.90,
            "status": "DELIVERED"
        }
    ]
}


def export_sample_data(data_dir: str) -> None:
    """Exports dataset to JSON and CSV files."""
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "ecommerce_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_DATA, f, indent=2)

    # Export individual CSVs
    for entity_name, records in SAMPLE_DATA.items():
        csv_path = os.path.join(data_dir, f"{entity_name}.csv")
        if not records:
            continue
        # Extract flat fields (serialize items list for orders)
        fieldnames = list(records[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                row = dict(rec)
                if isinstance(row.get("items"), list):
                    row["items"] = json.dumps(row["items"])
                writer.writerow(row)


def load_dataset(data_dir: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """Loads dataset from JSON file or returns the default in-memory dataset."""
    if data_dir:
        json_path = os.path.join(data_dir, "ecommerce_data.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    return SAMPLE_DATA


def audit_banana_occurrences(data: Dict[str, Any]) -> int:
    """
    Audits the dataset and counts how many times the word 'banana' appears
    across all values, node attributes, and text fields (case-insensitive).
    """
    data_str = json.dumps(data).lower()
    # Count occurrences of the exact substring 'banana'
    return data_str.count("banana")
