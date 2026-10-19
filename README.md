# Forest Cover Type Prediction — ML → Flask → Angular → GitHub CI/CD

Predicts forest cover type (7 classes) from terrain data using a Random Forest
(compared with Logistic Regression). Teaching/research prototype, not an operational tool.

## Dataset
UCI Covertype: https://archive.ics.uci.edu/dataset/31/covertype
The CSVs are not included (the train file is 215 MB). Only a 1-row sample is in `data/`.

## Model provenance
- Trained with `notebooks/train_compare.py` (RandomForest: 100 trees, max_depth 11, min_samples_leaf 15).
- Saved estimator was trained with scikit-learn 1.9.1 -> pinned in `backend/requirements.txt`.
- Training data was pre-standardized; the scaler was recovered exactly (`docs/scaler_recovery.md`)
  and packaged with the model as `backend/models/model_bundle.joblib`.

## Input schema (12 raw fields)
10 numeric terrain values in real units (Elevation, Aspect, Slope, 4 distances, 3 hillshades),
`Wilderness_Area` (1-4) and `Soil_Type` (1-6, 9-14, 16-35, 37-40). Engineered features
(Distance_To_Hydrology, Hillshade_Mean) and scaling are computed server-side.

## Results (test set)
| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 72.54% | 71.32% | 72.54% | 71.59% | 93.67% |
| Random Forest | 76.00% | 75.23% | 76.00% | 74.80% | 95.88% |

## Run locally (Windows, PowerShell; Python 3.12, Node 24 LTS)
```powershell
# Terminal 1 - Flask
py -3.12 -m venv .venv ; .\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python backend\app.py

# Terminal 2 - Angular
cd frontend ; npm install ; ng serve --open --proxy-config proxy.conf.json

# Terminal 3 - tests
python -m pytest -q backend\tests
```

## Deployment limits
GitHub Pages hosts only the static Angular UI; the "Run prediction" button is disabled there.
Predictions need Flask running locally. Pages URL: _add after Stage 14_. Repo: _add URL_.

## Disclaimer
Research/teaching prototype. 76% accuracy; do not use for land-management decisions.

## Contributors
- Nawal Shafiq
