"""
Model comparison on the preprocessed Forest Cover Type dataset.
Compares Logistic Regression (linear baseline) vs Random Forest (ensemble).
Saves the best model as a .pkl file for deployment.
"""
import os
# Limit BLAS thread count BEFORE importing numpy/sklearn to avoid
# memory-allocation crashes on machines with limited RAM
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import pandas as pd
import numpy as np
import joblib
import time
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, classification_report)
from sklearn.preprocessing import label_binarize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_PATH = os.path.join(BASE_DIR, "covertype_train.csv")
TEST_PATH = os.path.join(BASE_DIR, "covertype_test.csv")
TARGET = "Cover_Type"

train = pd.read_csv(TRAIN_PATH)
test = pd.read_csv(TEST_PATH)
print("Train:", train.shape, "| Test:", test.shape)

X_train = train.drop(columns=[TARGET])
y_train = train[TARGET]
X_test = test.drop(columns=[TARGET])
y_test = test[TARGET]

classes = sorted(y_train.unique())
y_test_bin = label_binarize(y_test, classes=classes)

results = {}

# ---------------------------------------------------------------
# Model 1: Logistic Regression (linear baseline)
# ---------------------------------------------------------------
print("\n=== Training Logistic Regression ===")
t0 = time.time()
lr = LogisticRegression(max_iter=500, solver="lbfgs",
                         C=5.0, random_state=42)
lr.fit(X_train.values, y_train.values)
print(f"Trained in {time.time()-t0:.1f}s")

# Change lines 52-54 to:
lr_train_pred = lr.predict(X_train.values)
lr_test_pred = lr.predict(X_test.values)
lr_test_proba = lr.predict_proba(X_test.values)

results["Logistic Regression"] = {
    "train_accuracy": accuracy_score(y_train, lr_train_pred),
    "test_accuracy": accuracy_score(y_test, lr_test_pred),
    "precision": precision_score(y_test, lr_test_pred, average="weighted", zero_division=0),
    "recall": recall_score(y_test, lr_test_pred, average="weighted", zero_division=0),
    "f1": f1_score(y_test, lr_test_pred, average="weighted", zero_division=0),
    "roc_auc": roc_auc_score(y_test_bin, lr_test_proba, average="macro", multi_class="ovr"),
}

# ---------------------------------------------------------------
# Model 2: Random Forest (ensemble; depth-capped to avoid overfitting)
# ---------------------------------------------------------------
print("\n=== Training Random Forest ===")
t0 = time.time()
rf = RandomForestClassifier(
    n_estimators=100, max_depth=11, min_samples_leaf=15,
    max_features="sqrt", n_jobs=2, random_state=42
)
rf.fit(X_train, y_train)
print(f"Trained in {time.time()-t0:.1f}s")

rf_train_pred = rf.predict(X_train)
rf_test_pred = rf.predict(X_test)
rf_test_proba = rf.predict_proba(X_test)

results["Random Forest"] = {
    "train_accuracy": accuracy_score(y_train, rf_train_pred),
    "test_accuracy": accuracy_score(y_test, rf_test_pred),
    "precision": precision_score(y_test, rf_test_pred, average="weighted", zero_division=0),
    "recall": recall_score(y_test, rf_test_pred, average="weighted", zero_division=0),
    "f1": f1_score(y_test, rf_test_pred, average="weighted", zero_division=0),
    "roc_auc": roc_auc_score(y_test_bin, rf_test_proba, average="macro", multi_class="ovr"),
}

# ---------------------------------------------------------------
# Report
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print(f"{'Metric':<15}{'Logistic Regression':<22}{'Random Forest':<15}")
print("=" * 70)
for metric in ["train_accuracy", "test_accuracy", "precision", "recall", "f1", "roc_auc"]:
    lr_v = results["Logistic Regression"][metric]
    rf_v = results["Random Forest"][metric]
    print(f"{metric:<15}{lr_v*100:<22.2f}{rf_v*100:<15.2f}")

print("\nOverfitting check (train acc - test acc):")
for name in results:
    gap = results[name]["train_accuracy"] - results[name]["test_accuracy"]
    print(f"  {name}: {gap*100:.2f} pts")

# ---------------------------------------------------------------
# Save best model (by test F1) as .pkl
# ---------------------------------------------------------------
best_name = max(results, key=lambda k: results[k]["f1"])
best_model = rf if best_name == "Random Forest" else lr
joblib.dump(best_model, os.path.join(BASE_DIR, "covertype_best_model.pkl"))
print(f"\nSaved best model ({best_name}) -> covertype_best_model.pkl")

import json
with open(os.path.join(BASE_DIR, "model_comparison_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print("Saved metrics -> model_comparison_results.json")
