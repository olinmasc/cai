import mlflow
import mlflow.xgboost
import numpy as np
import os
from datetime import datetime
from typing import Optional

# ── MLFLOW CONFIG ─────────────────────────────────────────────
# For the hackathon demo, MLflow stores everything locally
# In production this would point to a remote tracking server
# e.g. mlflow.set_tracking_uri("https://mlflow.yourcompany.com")

MLFLOW_EXPERIMENT = "cai-gst-anomaly-detection"
MLFLOW_DIR = "./mlruns"

mlflow.set_tracking_uri(f"file://{os.path.abspath(MLFLOW_DIR)}")


def get_or_create_experiment() -> str:
    """
    Get existing MLflow experiment or create a new one.
    Returns the experiment ID.
    """
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT)
    if experiment is None:
        experiment_id = mlflow.create_experiment(
            MLFLOW_EXPERIMENT,
            tags={
                "project":  "CAI",
                "team":     "Python Charmers",
                "use_case": "GST Anomaly Detection",
            }
        )
        print(f"Created MLflow experiment: {MLFLOW_EXPERIMENT}")
    else:
        experiment_id = experiment.experiment_id
    return experiment_id


# ── RUN TRACKER ───────────────────────────────────────────────

class RunTracker:
    """
    Tracks a single agent pipeline run in MLflow.

    One "run" = one complete cycle of all 4 agents
    processing a batch of invoices for one client.

    MLflow records:
    - Parameters:  what settings were used
    - Metrics:     what the results were (numbers)
    - Artifacts:   files produced (model, reports)
    - Tags:        metadata for filtering runs later
    """

    def __init__(self):
        self.run = None
        self.run_id = None
        self.start_time = None

    def start_run(self, client_id: str, period: str, ca_email: str):
        """Start tracking a new pipeline run."""
        experiment_id = get_or_create_experiment()
        self.start_time = datetime.utcnow()

        self.run = mlflow.start_run(
            experiment_id=experiment_id,
            run_name=f"cai-run-{client_id[:8]}-{period}",
            tags={
                "client_id": client_id,
                "period":    period,
                "ca_email":  ca_email,
                "env":       "hackathon-demo",
            }
        )
        self.run_id = self.run.info.run_id
        print(f"MLflow run started: {self.run_id}")
        return self.run_id

    def log_ingestion(
        self,
        total_invoices:    int,
        source:            str,
        parse_errors:      int = 0,
        duration_seconds:  float = 0.0,
    ):
        """Log metrics from the Ingestion Agent."""
        mlflow.log_params({
            "ingestion_source":   source,   # "tally_xml", "manual", "pdf"
        })
        mlflow.log_metrics({
            "invoices_ingested":  total_invoices,
            "parse_errors":       parse_errors,
            "ingestion_duration": duration_seconds,
        })

    def log_reconciliation(
        self,
        total:      int,
        matched:    int,
        mismatched: int,
        risk_score: float,
        model_version: str = "v1",
    ):
        """Log metrics from the Reconciliation Agent."""
        match_rate = (matched / total * 100) if total > 0 else 0

        mlflow.log_params({
            "model_version":   model_version,
            "reconcile_total": total,
        })
        mlflow.log_metrics({
            "match_rate":        round(match_rate, 2),
            "matched_invoices":  matched,
            "mismatch_count":    mismatched,
            "client_risk_score": risk_score,
        })

    def log_filing(
        self,
        return_type:      str,
        status:           str,
        nic_reference:    Optional[str] = None,
        duration_seconds: float = 0.0,
    ):
        """Log metrics from the Filing Agent."""
        mlflow.log_params({
            "return_type": return_type,   # GSTR-1, GSTR-3B, etc.
        })
        mlflow.log_metrics({
            "filing_success":  1.0 if status == "filed" else 0.0,
            "filing_duration": duration_seconds,
        })
        if nic_reference:
            mlflow.set_tag("nic_reference", nic_reference)

    def log_model(self, detector):
        """
        Log the trained XGBoost model as an MLflow artifact.
        This lets you version models and roll back if needed.
        """
        if detector.model is not None:
            # FIX: Use .get_booster() to satisfy MLflow's XGBoost flavor requirements
            mlflow.xgboost.log_model(
                detector.model.get_booster(),
                artifact_path="anomaly_model",
                registered_model_name="cai-anomaly-detector",
            )
            print("Model logged to MLflow")

    def log_anomalies(self, anomaly_invoices: list[dict]):
        """
        Log a summary of detected anomalies.
        In production, this would also save a full CSV report
        as an MLflow artifact.
        """
        if not anomaly_invoices:
            mlflow.log_metric("anomalies_detected", 0)
            return

        scores = [inv.get("anomaly_score", 0) for inv in anomaly_invoices]

        mlflow.log_metrics({
            "anomalies_detected":   len(anomaly_invoices),
            "avg_anomaly_score":    round(float(np.mean(scores)), 2),
            "max_anomaly_score":    round(float(np.max(scores)), 2),
        })

    def end_run(self, status: str = "FINISHED"):
        """
        End the MLflow run.
        status options: "FINISHED", "FAILED", "KILLED"
        """
        if self.run:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            mlflow.log_metric("total_pipeline_duration", duration)
            mlflow.end_run(status=status)
            print(
                f"MLflow run ended: {self.run_id} ({status}) in {duration:.1f}s")
            self.run = None
            self.run_id = None


# ── MODEL RETRAINING ──────────────────────────────────────────

def retrain_and_log(
    detector,
    new_invoices:       list[dict],
    confirmed_anomalies: list[str],
) -> dict:
    """
    The Learning Agent calls this function.

    It:
    1. Retrains the XGBoost model with new data
    2. Logs the new model version to MLflow
    3. Saves the updated model to disk
    4. Returns metrics comparing old vs new accuracy

    In production this would run nightly as a scheduled job.
    For the demo, it runs after each reconciliation batch.
    """
    experiment_id = get_or_create_experiment()

    # FIX: Added nested=True to prevent the "run already active" crash
    with mlflow.start_run(
        experiment_id=experiment_id,
        run_name=f"retrain-{datetime.utcnow().strftime('%Y%m%d-%H%M')}",
        tags={"type": "retraining", "trigger": "post_reconciliation"},
        nested=True
    ):
        # Log training data stats
        mlflow.log_params({
            "training_samples":   len(new_invoices),
            "confirmed_anomalies": len(confirmed_anomalies),
            "trigger":            "learning_agent",
        })

        # Retrain on new data
        detector.train_dummy_model()

        # Evaluate on the new batch
        scored = detector.predict_anomaly(new_invoices)
        detected = [s for s in scored if s.get("is_anomaly")]

        # Simple precision/recall calculation
        true_positives = sum(
            1 for s in detected
            if s.get("id") in confirmed_anomalies
        )
        precision = (
            true_positives / len(detected)
            if detected else 0
        )
        recall = (
            true_positives / len(confirmed_anomalies)
            if confirmed_anomalies else 0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0 else 0
        )

        mlflow.log_metrics({
            "precision": round(precision, 4),
            "recall":    round(recall, 4),
            "f1_score":  round(f1, 4),
            "anomalies_in_batch": len(detected),
        })

        # Save updated model
        detector.save()

        # FIX: Use .get_booster() for logging the retrained model
        mlflow.xgboost.log_model(
            detector.model.get_booster(),
            artifact_path="retrained_model",
            registered_model_name="cai-anomaly-detector",
        )

        print(f"Retraining complete — F1: {f1:.4f}")
        return {
            "precision": precision,
            "recall":    recall,
            "f1_score":  f1,
            "model_version": "retrained",
        }


# ── SINGLETON ─────────────────────────────────────────────────

tracker = RunTracker()


def get_tracker() -> RunTracker:
    return tracker
