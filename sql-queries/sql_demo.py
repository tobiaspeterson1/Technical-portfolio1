"""
SQL Portfolio – Databashantering med SQLite
==========================================
Skapar en lokal SQLite-databas med exempeldata och kör
ett antal SQL-queries som demonstrerar praktisk SQL-kompetens.
"""

import sqlite3
import os

DB_PATH = "portfolio.db"


def create_database():
    """Skapar tabeller och fyller med exempeldata."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        -- Rensa gamla tabeller om de finns
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        -- Kunder
        CREATE TABLE customers (
            customer_id   INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            city          TEXT,
            created_at    TEXT DEFAULT (date('now'))
        );

        -- Produkter
        CREATE TABLE products (
            product_id    INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            category      TEXT,
            price         REAL NOT NULL
        );

        -- Ordrar
        CREATE TABLE orders (
            order_id      INTEGER PRIMARY KEY,
            customer_id   INTEGER REFERENCES customers(customer_id),
            order_date    TEXT,
            status        TEXT CHECK(status IN ('pending','processing','shipped','delivered','cancelled'))
        );

        -- Orderrader
        CREATE TABLE order_items (
            item_id       INTEGER PRIMARY KEY,
            order_id      INTEGER REFERENCES orders(order_id),
            product_id    INTEGER REFERENCES products(product_id),
            quantity      INTEGER NOT NULL,
            unit_price    REAL NOT NULL
        );

        -- Exempeldata: kunder
        INSERT INTO customers (name, email, city) VALUES
            ('Anna Svensson',   'anna@example.com',   'Stockholm'),
            ('Erik Lindgren',   'erik@example.com',   'Göteborg'),
            ('Maria Nilsson',   'maria@example.com',  'Malmö'),
            ('Johan Karlsson',  'johan@example.com',  'Stockholm'),
            ('Sara Eriksson',   'sara@example.com',   'Uppsala');

        -- Exempeldata: produkter
        INSERT INTO products (name, category, price) VALUES
            ('Laptop Pro 15',       'Elektronik',   12999.00),
            ('Trådlöst headset',    'Elektronik',    899.00),
            ('Ergonomisk stol',     'Möbler',       4499.00),
            ('Stående skrivbord',   'Möbler',       6999.00),
            ('USB-C Hub',           'Tillbehör',     349.00),
            ('Webbkamera 4K',       'Elektronik',   1299.00);

        -- Exempeldata: ordrar
        INSERT INTO orders (customer_id, order_date, status) VALUES
            (1, '2024-01-15', 'delivered'),
            (1, '2024-03-02', 'shipped'),
            (2, '2024-02-10', 'delivered'),
            (3, '2024-02-20', 'cancelled'),
            (4, '2024-03-05', 'processing'),
            (5, '2024-03-10', 'pending');

        -- Exempeldata: orderrader
        INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
            (1, 1, 1, 12999.00),
            (1, 5, 2,   349.00),
            (2, 6, 1,  1299.00),
            (3, 2, 1,   899.00),
            (3, 5, 3,   349.00),
            (4, 3, 1,  4499.00),
            (5, 4, 2,  6999.00),
            (6, 2, 1,   899.00);
    """)

    conn.commit()
    conn.close()
    print("✅ Databas skapad med exempeldata.\n")


def run_query(conn, title, sql, params=()):
    """Kör en query och skriver ut resultatet snyggt."""
    print(f"{'─'*60}")
    print(f"📌 {title}")
    print(f"{'─'*60}")
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]

    # Enkel tabellformatering
    col_widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
                  for i, c in enumerate(cols)]
    header = "  ".join(str(c).ljust(w) for c, w in zip(cols, col_widths))
    print(header)
    print("  ".join("─" * w for w in col_widths))
    for row in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, col_widths)))
    print(f"({len(rows)} rader)\n")


def main():
    create_database()
    conn = sqlite3.connect(DB_PATH)

    # --- Query 1: Grundläggande SELECT med filtrering ---
    run_query(conn, "Alla levererade ordrar",
        """
        SELECT o.order_id, c.name AS kund, o.order_date, o.status
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status = 'delivered'
        ORDER BY o.order_date DESC
        """
    )

    # --- Query 2: Aggregering – totalt ordervärde per kund ---
    run_query(conn, "Totalt ordervärde per kund (TOP 5)",
        """
        SELECT
            c.name                              AS kund,
            COUNT(DISTINCT o.order_id)          AS antal_ordrar,
            SUM(oi.quantity * oi.unit_price)    AS total_kronor
        FROM customers c
        JOIN orders o        ON c.customer_id = o.customer_id
        JOIN order_items oi  ON o.order_id    = oi.order_id
        WHERE o.status != 'cancelled'
        GROUP BY c.customer_id, c.name
        ORDER BY total_kronor DESC
        LIMIT 5
        """
    )

    # --- Query 3: Mest sålda produkter ---
    run_query(conn, "Mest sålda produkter efter antal sålda enheter",
        """
        SELECT
            p.name                      AS produkt,
            p.category                  AS kategori,
            SUM(oi.quantity)            AS sålda_enheter,
            SUM(oi.quantity * oi.unit_price) AS intäkt
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o       ON oi.order_id  = o.order_id
        WHERE o.status != 'cancelled'
        GROUP BY p.product_id, p.name, p.category
        ORDER BY sålda_enheter DESC
        """
    )

    # --- Query 4: Subquery – kunder som beställt mer än en gång ---
    run_query(conn, "Återkommande kunder (fler än 1 order)",
        """
        SELECT name, email, city
        FROM customers
        WHERE customer_id IN (
            SELECT customer_id
            FROM orders
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        )
        """
    )

    # --- Query 5: Ordrar med status och totalt värde ---
    run_query(conn, "Ordersammanfattning med beräknat totalvärde",
        """
        SELECT
            o.order_id,
            c.name          AS kund,
            o.status,
            SUM(oi.quantity * oi.unit_price) AS ordervärde
        FROM orders o
        JOIN customers c    ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id    = oi.order_id
        GROUP BY o.order_id, c.name, o.status
        ORDER BY o.order_id
        """
    )

    conn.close()

    # Städa upp
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    print("✅ Klart! Alla queries kördes utan fel.")


if __name__ == "__main__":
    main()
