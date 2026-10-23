import pytest
from customer_insights import analysis


def test_empty_customers_canc_rate():
    assert analysis.cancellation_rate([]) == 0


def test_customers_canc_rate():
    customers = [
        (1, "A", "a@test.com", '111', "CY", "2026-01-01", "Basic", 10, "paid", 0, 1, "2026-02-01"),
        (2, "B", "b@test.com", '111', "CY", "2026-01-01", "Basic", 10, "paid", 0, 0, "2026-02-01"),
        (3, "C", "c@test.com", '111', "CY", "2026-01-01", "Basic", 10, "paid", 0, 0, "2026-02-01"),
        (4, "D", "d@test.com", '111', "CY", "2026-01-01", "Basic", 10, "paid", 0, 1, "2026-02-01"),
    ]
    assert analysis.cancellation_rate(customers) == 50

def test_cancellation_reasons():
    customers = [
        (1, "A", "a@test.com", "111", "CY", "2026-01-01", "Basic", 10, "paid", 0, 1, "2026-02-01"),
        (2, "B", "b@test.com", "222", "CY", "2026-01-01", "Basic", 10, "paid", 0, 0, None),
    ]
    comments = [
        (1, 1, "2026-01-10", "Payment failed twice."),
        (2, 1, "2026-01-11", "App keeps buffering."),
        (3, 2, "2026-01-12", "Payment failed twice."),
    ]
    result = analysis.cancellation_reasons(customers, comments)
    assert result["Billing/Payment Issues"]==1
    assert result["Buffering Issues"]==1
    assert result["Other/Unclassified"]==0
