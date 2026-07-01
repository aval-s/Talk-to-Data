from pathlib import Path
import random
import sqlite3
from faker import Faker

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "talk_to_data.db"

fake = Faker()
categories = ["Electronics", "Clothing", "Home", "Books", "Toys"]

conn = sqlite3.connect(DB_PATH)
print(f"Connected to database: {DB_PATH}")
cursor = conn.cursor()

for table in ["order_items", "orders", "products", "customers"]:#deleting existing data from tables to avoid duplicates when populating new data
    cursor.execute(f"DELETE FROM {table}")

for _ in range(100): #populating customers table with 100 random customers
    cursor.execute(
        "INSERT INTO customers (name, email, city, signup_date) VALUES (?, ?, ?, ?)",
        (
            fake.name(),
            fake.email(),
            fake.city(),
            fake.date_between(start_date="-2y", end_date="today").isoformat(),
        ),
    )

for _ in range(30): #populating products table with 30 random products
    category = random.choice(categories)
    cursor.execute(
        "INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)",
        (
            f"{fake.word().capitalize()} {category}",
            round(random.uniform(5, 500), 2),
            fake.random_int(min=0, max=100),
            category,
        ),
    )

cursor.execute("SELECT customer_id FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT product_id, price FROM products")
products = cursor.fetchall()

for _ in range(200):#populating orders and order_items tables with 200 random orders
    customer_id = random.choice(customer_ids)
    status = random.choices(
        ["shipped", "pending", "cancelled", "returned"],
        weights=[70, 15, 10, 5],
    )[0]
    cursor.execute(
        "INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)",
        (
            customer_id,
            fake.date_between(start_date="-2y", end_date="today").isoformat(),
            status,
        ),
    )
    order_id = cursor.lastrowid

    for _ in range(random.randint(1, 4)):#populating order_items table with 1 to 4 random products for each order
        product_id, unit_price = random.choice(products)
        quantity = random.randint(1, 5)
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, unit_price),
        )

conn.commit()
conn.close()

