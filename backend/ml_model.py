import numpy as np
import joblib
import os
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL_PATH = "cai_anomaly_model.joblib"

# ── FEATURE ENGINEERING ───────────────────────────────────────
# These are the features we extract from each invoice
# to determine if it's anomalous
#
# Feature 1: amount_zscore     — how unusual is this amount?
# Feature 2: round_number      — suspiciously round amounts (1.0 = yes)
# Feature 3: amount_log        — log-scaled amount (handles wide range)
# Feature 4: is_large          — amount > 1 lakh (1.0 = yes)
# Feature 5: gst_type_encoded  — 0=PURCHASE, 1=SALES, 2=OTHER


def extract_features(invoices: list[dict]) -> np.ndarray:
    """
    Convert a list of invoice dicts into a feature matrix.
    Each row = one invoice. Each column = one feature.

    This is what XGBoost will learn patterns from.
    """
    features = []

    amounts = [float(inv.get("amount", 0)) for inv in invoices]
    mean_amount = np.mean(amounts) if amounts else 1
    std_amount = np.std(amounts) if amounts else 1

    for inv in invoices:
        amount = float(inv.get("amount", 0))
        gst_type = inv.get("gst_type", "").upper()

        # Z-score: how many standard deviations from the mean?
        # High z-score = unusual amount
        zscore = (amount - mean_amount) / (std_amount + 1e-9)

        # Round number detection: ₹10,000 is more suspicious than ₹10,243
        is_round = 1.0 if amount % 1000 == 0 else 0.0

        # Log transform: compress the wide range of invoice amounts
        log_amount = np.log1p(amount)

        # Large invoice flag
        is_large = 1.0 if amount > 100000 else 0.0

        # GST type encoding
        gst_enc = {"PURCHASE": 0, "SALES": 1}.get(gst_type, 2)

        features.append([zscore, is_round, log_amount, is_large, gst_enc])

    return np.array(features, dtype=np.float32)


# ── MODEL CLASS ───────────────────────────────────────────────

class AnomalyDetector:
    """
    XGBoost-based anomaly detector for GST invoices.

    In production: trained on real historical filing data
    In demo: trained on synthetic data that mimics real patterns
    """

    def __init__(self):
        self.model = None
        self.is_trained = False

    def train_dummy_model(self):
        """
        Train on synthetic data for demo purposes.

        We generate two classes:
        - Class 0 = normal invoice (majority)
        - Class 1 = anomalous invoice (minority — ~15%)

        Real anomalies look like:
        - Very high z-score (unusually large amount)
        - Round numbers with large amounts
        - Mismatched GST type patterns
        """
        np.random.seed(42)
        n_normal = 850
        n_anomaly = 150

        # Normal invoices — typical business transactions
        normal = np.column_stack([
            np.random.normal(0, 1, n_normal),      # z-score near 0
            np.random.binomial(1, 0.1, n_normal),  # rarely round
            np.random.normal(9, 2, n_normal),      # log amount ~₹8,000
            np.zeros(n_normal),                    # not large
            np.random.randint(0, 2, n_normal),     # purchase or sales
        ])

        # Anomalous invoices — suspicious patterns
        anomaly = np.column_stack([
            np.random.normal(3, 1, n_anomaly),     # high z-score
            np.random.binomial(1, 0.7, n_anomaly),  # often round numbers
            np.random.normal(12, 2, n_anomaly),    # log amount ~₹160,000
            np.ones(n_anomaly),                    # large amounts
            np.random.randint(0, 3, n_anomaly),    # any type
        ])

        X = np.vstack([normal, anomaly]).astype(np.float32)
        y = np.array([0]*n_normal + [1]*n_anomaly)

        # XGBoost classifier
        # scale_pos_weight handles class imbalance (6:1 ratio here)
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            scale_pos_weight=n_normal/n_anomaly,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )

        self.model.fit(X, y)
        self.is_trained = True
        print("Anomaly model trained on synthetic data")
        return self

    def predict_anomaly(self, invoices: list[dict]) -> list[dict]:
        """
        Score each invoice for anomaly probability.

        Returns the same invoices with two new fields added:
        - anomaly_score: float 0-100 (risk score)
        - is_anomaly: bool (True if score > 50)
        """
        if not self.is_trained or self.model is None:
            # If model not ready, fall back to rule-based scoring
            return self._rule_based_fallback(invoices)

        features = extract_features(invoices)
        if len(features) == 0:
            return invoices

        # Get probability of class 1 (anomaly)
        probs = self.model.predict_proba(features)[:, 1]

        results = []
        for invoice, prob in zip(invoices, probs):
            score = round(float(prob) * 100, 1)
            results.append({
                **invoice,
                "anomaly_score": score,
                "is_anomaly": score > 50,
            })

        return results

    def _rule_based_fallback(self, invoices: list[dict]) -> list[dict]:
        """
        Simple rule-based scoring when model isn't trained.
        Used as a safety net.
        """
        results = []
        for inv in invoices:
            amount = float(inv.get("amount", 0))
            score = 0

            if amount > 500000:
                score += 40   # very large
            if amount > 100000:
                score += 20   # large
            if amount % 10000 == 0:
                score += 15  # suspiciously round
            if amount == 0:
                score += 50          # zero amount invoice

            results.append({
                **inv,
                "anomaly_score": min(score, 100),
                "is_anomaly": score > 50,
            })
        return results

    def save(self, path: str = MODEL_PATH):
        if self.model:
            joblib.dump(self.model, path)
            print(f"Model saved to {path}")

    def load(self, path: str = MODEL_PATH):
        if os.path.exists(path):
            self.model = joblib.load(path)
            self.is_trained = True
            print(f"Model loaded from {path}")
        else:
            print(f"No saved model found at {path} — train first")
        return self


# ── SINGLETON ─────────────────────────────────────────────────
# One model instance shared across the whole app
# Loaded once at startup, reused on every request

detector = AnomalyDetector()


def get_detector() -> AnomalyDetector:
    """
    Returns a trained detector.
    Loads from disk if available, trains dummy model if not.
    """
    if not detector.is_trained:
        if os.path.exists(MODEL_PATH):
            detector.load()
        else:
            detector.train_dummy_model()
            detector.save()
    return detector
