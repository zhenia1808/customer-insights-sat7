"""Customer cancellation analysis and optional model-based risk estimates."""
import os

def cancellation_rate(customers):
    if not customers:
        return 0
    cancelled = sum(customer[10] for customer in customers)
    total_customers = len(customers)
    return (cancelled/total_customers)*100


def cancellation_reasons(customers, comments):
    """Return the main factors associated with cancelling."""
    cancelled_ids = {c[0] for c in customers if c[10]==1}
    cancelled_comments = [c for c in comments if c[1] in cancelled_ids]
    themes = {
        'Billing/Payment Issues': 0, 'Technical/Login Issues': 0,
        'Buffering Issues': 0, 'Language/Audio Issues': 0,
        'Subtitle Issues': 0, 'Customer Support Issues': 0,
        'Pricing/Value': 0, 'Service Availability': 0,
        'Content Repetition': 0, 'Positive Feedback': 0,
        'No Issues Reported': 0, 'Other/Unclassified': 0
    }
    theme_rules = {
        "Billing/Payment Issues": ["payment failed", "charged me twice"],
        "Technical/Login Issues": ["can't log in"], "Buffering Issues": ["buffering", "buffered"],
        "Language/Audio Issues": ["audio track is missing"],
        "Subtitle Issues": ["subtitles", "out of sync"],
        "Customer Support Issues": ["support", "reply"],
        "Pricing/Value": ["price went up", "worth it"],
        "Service Availability": ["available there", "moving abroad"],
        "Content Repetition": ["too many repeats"],
        "Positive Feedback": ["love the new programmes"],
        "No Issues Reported": ["no complaints", "works fine"]
    }
    for comment in cancelled_comments:
        text = comment[3].lower()
        match = False
        for theme, keywords in theme_rules.items():
            if any(keyword in text for keyword in keywords):
                themes[theme] += 1
                match = True
                break
        if not match:
            themes["Other/Unclassified"] += 1
    return themes


def at_risk_customers(customers, analytics_customers, limit=10):
    """Rank active customers using a deliberately configured, trusted model.

    Optional model dependencies are imported only when a model is configured.
    Serialized model files can execute code when loaded; configure MODEL_PATH
    only for an artifact that has been reviewed and is compatible with this code.
    """
    model_path = configured_model_path()
    if not analytics_customers or model_path is None:
        return []

    import joblib
    import pandas as pd
    import shap

    model = joblib.load(model_path)

    columns = ["customer_id", "country", "plan", "monthly_fee", "last_payment_status", "support_tickets"]

    analytics_df = pd.DataFrame(analytics_customers, columns=columns)

    features = analytics_df[["country", "plan", "monthly_fee", "last_payment_status", "support_tickets"]]

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    transformed = preprocessor.transform(features)
    feature_names = preprocessor.get_feature_names_out()

    # The training script can select either a linear model or a tree model.
    # Use the matching SHAP explainer so each choice can produce reasons.
    if classifier.__class__.__name__ == "LogisticRegression":
        explainer = shap.LinearExplainer(classifier, transformed)
        explanations = explainer(transformed)
        shap_values = explanations.values
    else:
        tree_data = transformed.toarray() if hasattr(transformed, "toarray") else transformed
        explainer = shap.TreeExplainer(classifier, tree_data)
        explanations = explainer(tree_data)
        shap_values = explanations.values

    positive_class = list(classifier.classes_).index(1)
    # SHAP versions differ: some return a list per class, some include a
    # final class dimension, and some binary explainers return 2-D values.
    if isinstance(shap_values, list):
        shap_values = shap_values[positive_class]
    elif getattr(shap_values, "ndim", 0) == 3:
        shap_values = shap_values[:, :, positive_class]

    probabilities = model.predict_proba(features)[:, list(classifier.classes_).index(1)]

    customer_by_id = {customer[0]: customer for customer in customers}
    results = []

    # Select the customers with the highest predicted risk.
    top_indices = probabilities.argsort()[::-1][:limit]

    for i in top_indices:
        customer_id = analytics_df.iloc[i]["customer_id"]
        customer = customer_by_id.get(customer_id)

        if customer is None:
            continue

        # Find the three strongest SHAP contributions pushing risk upward.
        values = shap_values[i]
        top_features = sorted(
            range(len(values)),
            key=lambda j: values[j],
            reverse=True,
        )

        reasons = []

        for j in top_features:
            if values[j] <= 0:
                continue

            feature = feature_names[j]

            # Only report categorical values that apply to this customer.
            if feature.startswith("categorical__") and transformed[i, j] < 0.5:
                continue

            if feature == "numerical__support_tickets":
                reason = "Support tickets increase predicted risk"

            elif feature == "numerical__monthly_fee":
                reason = "Monthly fee increases predicted risk"

            elif feature.startswith("categorical__last_payment_status_"):
                status = feature.replace(
                    "categorical__last_payment_status_", ""
                )
                reason = f"Payment status: {status}"

            elif feature.startswith("categorical__plan_"):
                plan = feature.replace("categorical__plan_", "")
                reason = f"Plan: {plan}"

            elif feature.startswith("categorical__country_"):
                country = feature.replace("categorical__country_", "")
                reason = f"Country: {country}"

            else:
                continue

            reasons.append(reason)

            if len(reasons) == 3:
                break

        results.append({
            "full_name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "plan": customer[6],
            "reason": ", ".join(reasons) if reasons else "No positive SHAP contributions",
        })

    return results


def configured_model_path():
    """Return an existing model path only when the operator explicitly sets it."""
    model_path = os.getenv("MODEL_PATH")
    if not model_path or not os.path.isfile(model_path):
        return None
    return model_path
