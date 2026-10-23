"""Create a small, deterministic SQLite database containing fictional data."""

from pathlib import Path
import sqlite3


SYNTHETIC_CUSTOMERS = [
    (1, "Avery Example", "avery@example.com", "+1-202-555-0101", "Cyprus", "2025-01-10", "Basic", 9.99, "paid", 0, 1, "2025-05-10"),
    (2, "Blair Sample", "blair@example.com", "+1-202-555-0102", "Jordan", "2025-02-14", "Standard", 14.99, "late", 2, 0, None),
    (3, "Casey Demo", "casey@example.com", "+1-202-555-0103", "Cyprus", "2025-03-01", "Premium", 19.99, "paid", 1, 0, None),
    (4, "Devon Fiction", "devon@example.com", "+1-202-555-0104", "Lebanon", "2025-03-18", "Basic", 9.99, "failed", 3, 1, "2025-06-18"),
    (5, "Emery Sample", "emery@example.com", "+1-202-555-0105", "Jordan", "2025-04-02", "Standard", 14.99, "paid", 0, 0, None),
    (6, "Finley Example", "finley@example.com", "+1-202-555-0106", "Cyprus", "2025-04-22", "Premium", 19.99, "late", 2, 0, None),
    (7, "Gray Demo", "gray@example.com", "+1-202-555-0107", "Lebanon", "2025-05-08", "Basic", 9.99, "paid", 1, 1, "2025-08-08"),
    (8, "Harper Fiction", "harper@example.com", "+1-202-555-0108", "Jordan", "2025-06-12", "Standard", 14.99, "paid", 0, 0, None),
]

SYNTHETIC_COMMENTS = [
    (1, 1, "2025-04-20", "SYNTHETIC demo comment: payment failed on the fictional account."),
    (2, 1, "2025-05-01", "SYNTHETIC demo comment: the example video buffered."),
    (3, 2, "2025-05-12", "SYNTHETIC demo comment: a fictional question about a late payment."),
    (4, 4, "2025-06-01", "SYNTHETIC demo comment: example subtitles were out of sync."),
    (5, 7, "2025-07-15", "SYNTHETIC demo comment: the fictional support reply was delayed."),
]


def create_synthetic_database(path="data/customers.db"):
    """Create the documented schema and sample rows without overwriting a file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Exclusive creation prevents accidental replacement of an existing file.
    with target.open("xb"):
        pass

    try:
        connection = sqlite3.connect(target)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                connection.executescript(
                    """
                    CREATE TABLE customers (
                        customer_id INTEGER PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        country TEXT NOT NULL,
                        signup_date TEXT NOT NULL,
                        plan TEXT NOT NULL,
                        monthly_fee REAL NOT NULL,
                        last_payment_status TEXT NOT NULL,
                        support_tickets INTEGER NOT NULL,
                        cancelled INTEGER NOT NULL CHECK (cancelled IN (0, 1)),
                        cancelled_date TEXT
                    );

                    CREATE TABLE support_comments (
                        comment_id INTEGER PRIMARY KEY,
                        customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                        created_at TEXT NOT NULL,
                        comment_text TEXT NOT NULL
                    );

                    CREATE VIEW v_customers_analytics AS
                    SELECT customer_id, country, signup_date, plan, monthly_fee,
                           last_payment_status, support_tickets, cancelled, cancelled_date
                    FROM customers;
                    """
                )
                connection.executemany(
                    "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    SYNTHETIC_CUSTOMERS,
                )
                connection.executemany(
                    "INSERT INTO support_comments VALUES (?, ?, ?, ?)",
                    SYNTHETIC_COMMENTS,
                )
        finally:
            connection.close()
    except Exception:
        target.unlink(missing_ok=True)
        raise

    return target
