"""Evidence script: raw-input pipeline must reproduce the original CSV -> RandomForest results.
Needs data/covertype_test.csv (git-ignored). Run from project root:
    python backend\verify_against_csv.py
"""
from pathlib import Path
import sys
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from preprocessing import RAW_NUMERIC, SCALER, SOIL_VALUES

te = pd.read_csv(ROOT / "data/covertype_test.csv")
y = te.pop("Cover_Type")
raw = pd.DataFrame({c: np.round(te[c] * SCALER[c][1] + SCALER[c][0]).astype(int) for c in RAW_NUMERIC})
raw["Wilderness_Area"] = 1
for i in (2, 3, 4):
    raw.loc[te[f"Wilderness_Area_{i}"], "Wilderness_Area"] = i
raw["Soil_Type"] = 1
for i in SOIL_VALUES:
    if i != 1:
        raw.loc[te[f"Soil_Type_{i}"], "Soil_Type"] = i

pipe = joblib.load(ROOT / "backend/models/model_bundle.joblib")["pipeline"]
rf = pipe.named_steps["model"]
diff = np.abs(pipe.predict_proba(raw) - rf.predict_proba(te)).max()
acc = (pipe.predict(raw) == y.values).mean()
print(f"rows={len(te)}  max prob diff={diff:.2e}  accuracy={acc:.6f}")
assert diff < 1e-9 and abs(acc - 0.7599593530941596) < 1e-9, "Pipeline != original model"
print("PASS: raw-input pipeline reproduces the original 76.00% test accuracy")
