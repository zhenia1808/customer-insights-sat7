"""Build the weekly summary into outbox/summary.md."""
from pathlib import Path
from jinja2 import Template
from . import db
from . import analysis


def build(db_path=None, output_path="outbox/summary.md", template_path="templates/weekly_summary.md.j2"):
    """Build a report; paths may be supplied for isolated tests and runs."""
    conn = db.connect(db_path)
    try:
        customers = db.get_customers(conn)
        comments = db.get_comments(conn)
        analytics_customers = db.get_analytics_customers(conn)
        model_path = analysis.configured_model_path()
        at_risk = analysis.at_risk_customers(customers, analytics_customers)

        if model_path is None:
            risk_message = (
                "Risk predictions skipped: no model is configured or available at the specified path. "
                "No risk scores were produced."
            )
        elif not analytics_customers:
            risk_message = "No active customers with analytics data were available for risk prediction."
        else:
            risk_message = (
                "This is a general estimate based on past data, not a prediction "
                "for a particular week. Do not use this list by itself to decide "
                "whom to contact."
            )

        template = Template(Path(template_path).read_text(encoding="utf-8"))
        out = template.render(
            total=len(customers),
            cancellation_rate=analysis.cancellation_rate(customers),
            drivers=analysis.cancellation_reasons(customers, comments),
            at_risk=at_risk,
            risk_message=risk_message,
        )
    finally:
        conn.close()

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target}")
    return out


if __name__ == "__main__":
    build()
