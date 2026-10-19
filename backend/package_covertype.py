"""Build backend/models/model_bundle.joblib from the trained Random Forest (.pkl)
plus the recovered preprocessing. Run from project root:
    python backend\package_covertype.py
"""
from pathlib import Path
import joblib
from sklearn.pipeline import Pipeline

from preprocessing import (CovertypePrep, OUTPUT_COLUMNS, RAW_FEATURES, RAW_NUMERIC,
                           SOIL_VALUES, WILDERNESS_VALUES)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "models" / "covertype_best_model.pkl"

rf = joblib.load(SOURCE)  # trusted artifact only (trained by this project)
assert list(rf.feature_names_in_) == OUTPUT_COLUMNS, "Model columns != preprocessing output"
assert rf.n_features_in_ == 50

RANGES = {
    "Elevation": (1859, 3858), "Aspect": (0, 359), "Slope": (0, 66),
    "Horizontal_Distance_To_Hydrology": (0, 1397),
    "Vertical_Distance_To_Hydrology": (-173, 601),
    "Horizontal_Distance_To_Roadways": (0, 7117),
    "Hillshade_9am": (0, 255), "Hillshade_Noon": (0, 255), "Hillshade_3pm": (0, 255),
    "Horizontal_Distance_To_Fire_Points": (0, 7173),
}
schema = {n: {"kind": "number", "min": RANGES[n][0], "max": RANGES[n][1]} for n in RAW_NUMERIC}
schema["Wilderness_Area"] = {"kind": "category", "options": [str(v) for v in WILDERNESS_VALUES]}
schema["Soil_Type"] = {"kind": "category", "options": [str(v) for v in SOIL_VALUES]}

CLASS_NAMES = {1: "Spruce/Fir", 2: "Lodgepole Pine", 3: "Ponderosa Pine",
               4: "Cottonwood/Willow", 5: "Aspen", 6: "Douglas-fir", 7: "Krummholz"}

pipeline = Pipeline([("prep", CovertypePrep()), ("model", rf)])
bundle = {
    "pipeline": pipeline,
    "features": RAW_FEATURES,
    "schema": schema,
    "class_names": {int(c): CLASS_NAMES[int(c)] for c in rf.classes_},
    "task": "classification",
    "model_version": "1.0",
}
joblib.dump(bundle, ROOT / "models" / "model_bundle.joblib", compress=3)
print("Saved model bundle:", len(RAW_FEATURES), "raw features ->", 50, "model inputs")
