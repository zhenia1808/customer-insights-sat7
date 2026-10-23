import sqlite3
from pathlib import Path

import pytest

from customer_insights.report import build
from customer_insights.synthetic_data import create_synthetic_database


def test_synthetic_database_has_expected_schema_and_fictional_rows(tmp_path):
    database_path = tmp_path / "nested" / "data" / "customers.db"

    created = create_synthetic_database(database_path)

    assert created == database_path
    with sqlite3.connect(database_path) as connection:
        customer_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(customers)")
        }
        analytics_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(v_customers_analytics)")
        }
        customer_count = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]
        cancelled_count = connection.execute(
            "SELECT COUNT(*) FROM customers WHERE cancelled = 1"
        ).fetchone()[0]
        active_analytics_count = connection.execute(
            "SELECT COUNT(*) FROM v_customers_analytics WHERE cancelled = 0"
        ).fetchone()[0]
        email_domains = {
            row[0].rsplit("@", 1)[-1]
            for row in connection.execute("SELECT email FROM customers")
        }
        phones = [row[0] for row in connection.execute("SELECT phone FROM customers")]

    assert customer_columns == {
        "customer_id", "full_name", "email", "phone", "country", "signup_date",
        "plan", "monthly_fee", "last_payment_status", "support_tickets",
        "cancelled", "cancelled_date",
    }
    assert {"full_name", "email", "phone"}.isdisjoint(analytics_columns)
    assert customer_count == 8
    assert cancelled_count == 3
    assert active_analytics_count == 5
    assert email_domains == {"example.com"}
    assert all("555-01" in phone for phone in phones)


def test_synthetic_database_refuses_to_overwrite_existing_file(tmp_path):
    database_path = create_synthetic_database(tmp_path / "customers.db")
    original_bytes = database_path.read_bytes()

    with pytest.raises(FileExistsError):
        create_synthetic_database(database_path)

    assert database_path.read_bytes() == original_bytes


def test_report_completes_without_model_and_marks_risk_as_skipped(tmp_path, monkeypatch):
    monkeypatch.delenv("MODEL_PATH", raising=False)
    database_path = create_synthetic_database(tmp_path / "data" / "customers.db")
    output_path = tmp_path / "outbox" / "summary.md"
    template_path = Path(__file__).resolve().parents[1] / "templates" / "weekly_summary.md.j2"

    summary = build(
        db_path=database_path,
        output_path=output_path,
        template_path=template_path,
    )

    assert output_path.is_file()
    assert "Customers in scope: 8" in summary
    assert "Cancellation rate: 37.5 %" in summary
    assert "Risk predictions skipped: no model is configured or available at the specified path." in summary
    assert "No risk scores were produced." in summary
    assert "Customers with higher predicted cancellation risk — review only" in summary
    assert "contact this week" not in summary.lower()
    assert "@example.com" not in summary


def test_report_with_model_uses_general_risk_and_contact_disclaimer(tmp_path, monkeypatch):
    database_path = create_synthetic_database(tmp_path / "data" / "customers.db")
    output_path = tmp_path / "outbox" / "summary.md"
    template_path = Path(__file__).resolve().parents[1] / "templates" / "weekly_summary.md.j2"

    monkeypatch.setattr(
        "customer_insights.analysis.configured_model_path",
        lambda: "models/test-only.joblib",
    )
    monkeypatch.setattr(
        "customer_insights.analysis.at_risk_customers",
        lambda customers, analytics_customers: [],
    )

    summary = build(
        db_path=database_path,
        output_path=output_path,
        template_path=template_path,
    )

    assert "This is a general estimate based on past data" in summary
    assert "not a prediction for a particular week" in summary
    assert "Do not use this list by itself to decide whom to contact." in summary
    assert "contact this week" not in summary.lower()
