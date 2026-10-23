import os
import sqlite3

import pandas as pd

from sklearn.model_selection import (train_test_split,StratifiedKFold,cross_validate,)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from xgboost import XGBClassifier
import joblib


# 1. Load data
DB_PATH = os.getenv("DB_PATH", "data/customers.db")

with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query("""
        SELECT country, signup_date, plan, monthly_fee, last_payment_status, support_tickets, cancelled
        FROM v_customers_analytics
    """,
    conn)

# 2. Prepare features

df = df.drop(columns=["signup_date"])

X = df.drop(columns=["cancelled"])
y = df["cancelled"]

# 3. Split data before model comparison
X_dev, X_test, y_dev, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42,
)

# 4. Define preprocessing
categorical_features = ["country", "plan", "last_payment_status"]

numerical_features = ["monthly_fee", "support_tickets"]

preprocessor = ColumnTransformer([
    ("categorical",
     Pipeline(
        [("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),]
    ),categorical_features),
    ("numerical",
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]),numerical_features)
])

# 5. Define three candidate models
models = {
    "Logistic Regression": LogisticRegression(solver='liblinear', C=0.1, max_iter=2000, class_weight="balanced", random_state=42),

    "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight="balanced_subsample", random_state=42, n_jobs=-1),

    "XGBoost": XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, scale_pos_weight=9, random_state=42, eval_metric="logloss", n_jobs=1)
}

# 6. Compare models using cross-validation
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

results = {}

print("\nMODEL COMPARISON")

for name, classifier in models.items():
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])

    scores = cross_validate(
        pipeline,
        X_dev,
        y_dev,
        cv=cv,
        scoring=["accuracy", "recall", "roc_auc"],
    )

    accuracy = scores["test_accuracy"].mean()
    recall = scores["test_recall"].mean()
    roc_auc = scores["test_roc_auc"].mean()

    results[name] = {
        "model": pipeline,
        "recall": recall,
        "roc_auc": roc_auc,
    }

    print(f"\n{name}")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Recall:   {recall:.3f}")
    print(f"ROC-AUC:  {roc_auc:.3f}")

# 7. Select the model using development-set CV results
best_name = None
best_score = -1

for name in results:
    score = results[name]["recall"]

    if score > best_score:
        best_score = score
        best_name = name

best_model = results[best_name]["model"]

print(f"\nSelected model by CV recall: {best_name}")

# 8. Evaluate the selected model once on the held-out test set
best_model.fit(X_dev, y_dev)

y_prob = best_model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

print("\nTEST SET RESULTS")

print("\nClassification report:")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0,
))

print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.3f}")

# 9. Refit the selected pipeline on all available historical data
best_model.fit(X, y)

# 10. Save the fitted pipeline for the reporting workflow
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "models/cancellation_model.joblib",
)

os.makedirs(os.path.dirname(MODEL_PATH) or ".", exist_ok=True)
joblib.dump(best_model, MODEL_PATH)

print(f"\nSaved model to {MODEL_PATH}")