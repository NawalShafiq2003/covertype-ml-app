import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app import app, FEATURES

PAYLOAD = json.loads((ROOT / "backend/test_payload.json").read_text(encoding="utf-8"))


def test_health():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["features"] == len(FEATURES)


def test_predict_valid():
    response = app.test_client().post("/predict", json=PAYLOAD)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["prediction"] == 3          # known label for the sample row
    assert body["label"] == "Ponderosa Pine"
    assert len(body["probabilities"]) == 7
    assert abs(sum(body["probabilities"]) - 1) < 1e-6


def test_predict_missing_feature():
    incomplete = dict(PAYLOAD)
    incomplete.pop(FEATURES[0])
    response = app.test_client().post("/predict", json=incomplete)
    assert response.status_code == 400


def test_predict_invalid_json():
    response = app.test_client().post("/predict", data="not-json",
                                      content_type="application/json")
    assert response.status_code == 400


def test_predict_out_of_range():
    bad = dict(PAYLOAD, Elevation=99999)
    response = app.test_client().post("/predict", json=bad)
    assert response.status_code == 400


def test_predict_bad_soil_type():
    bad = dict(PAYLOAD, Soil_Type="8")     # soil 8 was removed from training data
    response = app.test_client().post("/predict", json=bad)
    assert response.status_code == 400
