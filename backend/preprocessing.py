"""
Covertype preprocessing: RAW form values -> the 50 standardized columns the
Random Forest was trained on.

The training CSVs were already standardized and the StandardScaler was never
saved. Its mean/scale were recovered EXACTLY from the CSVs (every recovered raw
value is an integer inside the known Covertype range; max residual ~1e-14).
See docs/scaler_recovery.md.

Training-time data preparation that this class reproduces:
  * rows with Soil_Type 7, 8, 15, 36 were removed (rare/constant soils)
  * Wilderness_Area_1 and Soil_Type_1 are the one-hot baselines (all zeros)
  * Distance_To_Hydrology = sqrt(H_dist^2 + V_dist^2)
  * Hillshade_Mean = mean(9am, noon, 3pm)
  * 12 numeric columns standardized with StandardScaler (ddof=0)
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

RAW_NUMERIC = [
    "Elevation", "Aspect", "Slope",
    "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology",
    "Horizontal_Distance_To_Roadways", "Hillshade_9am", "Hillshade_Noon",
    "Hillshade_3pm", "Horizontal_Distance_To_Fire_Points",
]
RAW_FEATURES = RAW_NUMERIC + ["Wilderness_Area", "Soil_Type"]

WILDERNESS_VALUES = [1, 2, 3, 4]
SOIL_VALUES = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22,
               23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 40]

SCALED_NUMERIC = RAW_NUMERIC + ["Distance_To_Hydrology", "Hillshade_Mean"]
WILDERNESS_COLS = [f"Wilderness_Area_{i}" for i in (2, 3, 4)]
SOIL_COLS = [f"Soil_Type_{i}" for i in SOIL_VALUES if i != 1]
OUTPUT_COLUMNS = SCALED_NUMERIC + WILDERNESS_COLS + SOIL_COLS  # exact training order

SCALER = {
    "Elevation": (2959.3085603662375, 280.0092230033446),
    "Aspect": (155.63642642342668, 111.91960095297212),
    "Slope": (14.108021618791394, 7.487535712463221),
    "Horizontal_Distance_To_Hydrology": (269.31716689114467, 212.45857284647576),
    "Vertical_Distance_To_Hydrology": (46.42814748728047, 58.301825570589074),
    "Horizontal_Distance_To_Roadways": (2348.8608333362035, 1558.8909520332134),
    "Hillshade_9am": (212.13942845923032, 26.777148271851505),
    "Hillshade_Noon": (223.30953865443973, 19.77114840374319),
    "Hillshade_3pm": (142.5242746371893, 38.28605556026046),
    "Horizontal_Distance_To_Fire_Points": (1979.231392717264, 1323.1933902635471),
    "Distance_To_Hydrology": (275.957195482567, 216.96240126711885),
    "Hillshade_Mean": (192.65774725028666, 14.46785159834941),
}


class CovertypePrep(BaseEstimator, TransformerMixin):
    """Stateless (already-fitted) preprocessing step."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = pd.DataFrame(X).copy()
        missing = [c for c in RAW_FEATURES if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        out = pd.DataFrame(index=df.index)
        num = df[RAW_NUMERIC].astype(float)
        eng = num.copy()
        eng["Distance_To_Hydrology"] = np.sqrt(
            num["Horizontal_Distance_To_Hydrology"] ** 2
            + num["Vertical_Distance_To_Hydrology"] ** 2)
        eng["Hillshade_Mean"] = num[["Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm"]].mean(axis=1)
        for col in SCALED_NUMERIC:
            mean, scale = SCALER[col]
            out[col] = (eng[col] - mean) / scale
        wild = df["Wilderness_Area"].astype(float).astype(int)
        soil = df["Soil_Type"].astype(float).astype(int)
        if not wild.isin(WILDERNESS_VALUES).all():
            raise ValueError(f"Wilderness_Area must be one of {WILDERNESS_VALUES}")
        if not soil.isin(SOIL_VALUES).all():
            raise ValueError(f"Soil_Type must be one of {SOIL_VALUES}")
        for i in (2, 3, 4):
            out[f"Wilderness_Area_{i}"] = (wild == i)
        for i in SOIL_VALUES:
            if i != 1:
                out[f"Soil_Type_{i}"] = (soil == i)
        return out[OUTPUT_COLUMNS]
