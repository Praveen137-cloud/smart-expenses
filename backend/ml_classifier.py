"""Reusable prediction helpers around the trained scikit-learn pipeline."""
import logging
import threading

import joblib

from backend.train_classifier import MODEL_PATH, train_and_save

logger = logging.getLogger("expense_tracker.ml")

LOW_CONFIDENCE_THRESHOLD = 0.45
_model = None
_lock = threading.Lock()


def load_model():
    """Load the saved model; train (and save) it automatically if missing or unreadable."""
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                if MODEL_PATH.exists():
                    try:
                        _model = joblib.load(MODEL_PATH)
                    except Exception:  # corrupt file or incompatible scikit-learn version
                        logger.warning("Could not load saved model - retraining.")
                        _model = train_and_save()
                else:
                    logger.info("Model file not found - training a new model.")
                    _model = train_and_save()
    return _model


def predict_category(description: str) -> dict:
    """Return {"category", "confidence", "low_confidence"} for a transaction description."""
    text = (description or "").strip()
    if not text:
        raise ValueError("Description must not be empty")
    model = load_model()

    # Descriptions with no known words (e.g. "Random XYZ purchase") fall back to Other.
    if model.named_steps["vectorizer"].transform([text]).nnz == 0:
        return {"category": "Other", "confidence": 0.0, "low_confidence": True}

    probabilities = model.predict_proba([text])[0]
    best = int(probabilities.argmax())
    category = str(model.classes_[best])
    confidence = round(float(probabilities[best]), 4)
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        return {"category": "Other", "confidence": confidence, "low_confidence": True}
    return {"category": category, "confidence": confidence, "low_confidence": False}
