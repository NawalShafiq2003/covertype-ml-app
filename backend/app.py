import sys
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))  # lets joblib import preprocessing.py

BUNDLE = joblib.load(BASE / "models/model_bundle.joblib")
MODEL = BUNDLE["pipeline"]
FEATURES = BUNDLE["features"]
SCHEMA = BUNDLE.get("schema", {})
CLASS_NAMES = BUNDLE.get("class_names", {})
TASK = BUNDLE.get("task", "classification")
app = Flask(__name__)


def validate(data):
    """Range / category checks from the saved schema. Returns an error string or None."""
    for name in FEATURES:
        spec, value = SCHEMA.get(name), data[name]
        if spec is None:
            continue
        if spec["kind"] == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return f"{name} must be a number"
            if not (spec["min"] <= value <= spec["max"]):
                return f"{name} must be between {spec['min']} and {spec['max']}"
        elif str(value) not in spec["options"]:
            return f"{name} must be one of {spec['options']}"
    return None


@app.get("/health")
def health():
    return jsonify(status="ok", features=len(FEATURES), task=TASK)


@app.post("/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON object"), 400
    missing = [f for f in FEATURES if f not in data]
    extra = [f for f in data if f not in FEATURES]
    if missing or extra:
        return jsonify(error="Input schema mismatch", missing=missing, extra=extra), 400
    problem = validate(data)
    if problem:
        return jsonify(error="Invalid input", detail=problem), 400
    frame = pd.DataFrame([[data[f] for f in FEATURES]], columns=FEATURES)
    try:
        prediction = MODEL.predict(frame)[0]
        prediction = prediction.item() if hasattr(prediction, "item") else prediction
        result = {"prediction": prediction, "task": TASK,
                  "label": CLASS_NAMES.get(prediction, str(prediction)),
                  "disclaimer": "Research/teaching prototype only."}
        if TASK == "classification" and hasattr(MODEL, "predict_proba"):
            result["probabilities"] = MODEL.predict_proba(frame)[0].tolist()
            result["classes"] = [int(c) for c in MODEL.classes_]
            result["class_labels"] = [CLASS_NAMES.get(int(c), str(c)) for c in MODEL.classes_]
        return jsonify(result)
    except (ValueError, TypeError) as exc:
        return jsonify(error="Invalid input", detail=str(exc)), 400
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify(error="Prediction processing failed"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
