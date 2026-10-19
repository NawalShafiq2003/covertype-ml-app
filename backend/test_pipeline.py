from pathlib import Path
import json
import sys
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))  # for preprocessing.py

bundle = joblib.load(ROOT / "backend/models/model_bundle.joblib")
payload = json.loads((ROOT / "backend/test_payload.json").read_text(encoding="utf-8"))
features = bundle["features"]
assert set(features) == set(payload), "Payload keys must match features"
frame = pd.DataFrame([[payload[f] for f in features]], columns=features)
model = bundle["pipeline"]
pred = model.predict(frame).tolist()
print("Prediction:", pred, "->", bundle["class_names"][pred[0]])
print("Probabilities:", [round(float(p), 4) for p in model.predict_proba(frame)[0]])
assert pred == [3], "Known sample (test row 0) must be class 3 (Ponderosa Pine)"
print("PASS: local inference")
