"""Create the local synthetic SQLite database used by the demonstration."""

import argparse

from customer_insights.synthetic_data import create_synthetic_database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="data/customers.db",
        help="database path to create (default: data/customers.db)",
    )
    args = parser.parse_args()
    target = create_synthetic_database(args.output)
    print(f"Created synthetic database at {target}")


if __name__ == "__main__":
    main()
