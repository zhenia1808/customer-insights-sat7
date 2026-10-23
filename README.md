# Customer Insights

A small local demo for understanding customer cancellations. The included database generator makes fictional sample data; it does not copy customer records.

## Project files

- `src/customer_insights/` — database access, cancellation analysis, optional risk predictions, and report generation
- `scripts/create_synthetic_db.py` — creates the fictional sample database
- `scripts/train_cancellation_model.py` — compares three models and saves the selected one
- `scripts/post_summary.py` — adds the report to a local channel log; it does not send a real message
- `templates/weekly_summary.md.j2` — controls the report’s layout
- `tests/` — checks the analysis and report using fictional data
- `DATA_DICTIONARY.md` — explains the database tables and fields

Generated databases, models, reports, and logs are ignored by Git. The project does not post to Slack or connect to other external services.

## Getting started

Use Python 3.10 or later. Run these commands from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
python scripts/create_synthetic_db.py
python -m customer_insights.report
python scripts/post_summary.py
python -m pytest
```

These steps use fictional sample data. The database generator creates the `data/` folder if needed, and won’t replace a database that already exists. The report is saved to `outbox/summary.md`, and each simulated post adds another entry to `outbox/channel_log.md`.

`requirements.txt` points to the same project setup for anyone who prefers installing with `python -m pip install -r requirements.txt`.

## Cancellation analysis and risk predictions

The report calculates how many customers cancelled and the cancellation rate. It also groups comments from customers who cancelled into themes using simple keyword rules. Each comment is counted under the first theme it matches. These themes can point to possible issues, but they don’t prove why a customer cancelled.

The themes are assigned by matching words and phrases in comments. The rules may miss comments that use different wording. A language model could be explored to assign themes more flexibly, but its results would need to be checked. Sending comments to an online model would also need privacy safeguards.

The training program and the customer database are separate files. The training program is in the staging folder. It uses the database named by `DB_PATH`; if you don’t set it, it looks for `data/customers.db` in the folder you run it from. The staging sample database has only 8 customers, so it is for demos and tests, not model training.

The model run used the local customer database provided with the project. The training script compared Logistic Regression, Random Forest, and XGBoost, selected Logistic Regression using cross-validation, evaluated it on held-out data, and then retrained it on all records in the local database. The saved model is included at `models/cancellation_model.joblib` and is used by default to build the report. The training database is not included.

To repeat the model run, use the local training database provided for the project. It is not included in the staging repository. Replace the example path below with the local path to that database. The 8-customer database created for demos and tests is too small for training.

```bash
python -m pip install -e ".[risk,test]"
DB_PATH="/path/to/authorized/training-database.db" MODEL_PATH="models/cancellation_model.joblib" python scripts/train_cancellation_model.py
DB_PATH="/path/to/authorized/training-database.db" MODEL_PATH="models/cancellation_model.joblib" python -m customer_insights.report
python scripts/post_summary.py
```

The report uses the database named by `DB_PATH` for the cancellation rate, comment themes, and active-customer risk list. If `DB_PATH` is not set, the report uses `data/customers.db` from the folder it is run in. The simulated post adds the report to the local channel log; it does not send it anywhere.

The report loads the bundled model with `joblib` by default and shows estimated risk scores for active customers in the summary; the simulated channel log includes those results too. Set `MODEL_PATH` to use a different model. Only use a model you created or trust. It estimates general cancellation risk from past data; it cannot predict who will cancel in a particular week. Its predictions can be wrong, so do not use the list by itself to decide whom to contact. Performance can vary on other data.

### Why these models?

The project compares three approaches: Logistic Regression as a simple starting point, Random Forest using many decision trees, and XGBoost building trees in steps. It chooses the model with the highest average recall. Recall measures how many customers who cancelled the model catches, though it can also flag customers who would not cancel.

The data records whether a customer cancelled, but not when they were likely to cancel. The model estimates general cancellation risk; it cannot say who will cancel in a particular week. Review its list as one imperfect input, and do not use it by itself to decide whom to contact.

## Data handling

The generated sample records and comments are fictional. Reports made from the project’s local customer database may include identifying details. Keep those reports private and check them before sharing. Use customer data only when you have permission and can protect it appropriately.
