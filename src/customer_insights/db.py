"""Database access."""
import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "data/customers.db")


def connect(db_path=None):
    return sqlite3.connect(db_path or DB_PATH)


def get_customers(conn):
    return conn.execute("SELECT * FROM customers").fetchall()


def get_customers_by_country(conn, country):
    return conn.execute(
        "SELECT * FROM customers WHERE country = ?",
        (country,)
    ).fetchall()

def get_comments(conn):
    return conn.execute("SELECT * FROM support_comments").fetchall()

def get_analytics_customers(conn):
    return conn.execute("""
        SELECT customer_id, country, plan, monthly_fee, last_payment_status, support_tickets
        FROM v_customers_analytics
        WHERE cancelled = 0
    """).fetchall()
