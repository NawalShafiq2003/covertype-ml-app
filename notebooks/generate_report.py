"""
Generates a visual report from model_comparison_results.json:
  - comparison_chart.png   (bar chart, viewable in VS Code)
  - report.md              (formatted table, viewable in VS Code preview)

Run this AFTER train_compare.py has produced model_comparison_results.json.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")  # no GUI needed, just save to file
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(BASE_DIR, "model_comparison_results.json")

with open(RESULTS_PATH) as f:
    results = json.load(f)

models = list(results.keys())
metrics = ["test_accuracy", "precision", "recall", "f1", "roc_auc"]
metric_labels = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]

# ---------------------------------------------------------------
# 1. Bar chart
# ---------------------------------------------------------------
x = np.arange(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5.5))
for i, model in enumerate(models):
    values = [results[model][m] * 100 for m in metrics]
    offset = width * (i - 0.5)
    bars = ax.bar(x + offset, values, width, label=model)
    ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=8)

ax.set_ylabel("Score (%)")
ax.set_title("Model Comparison: " + " vs ".join(models))
ax.set_xticks(x)
ax.set_xticklabels(metric_labels)
ax.set_ylim(0, 105)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()

chart_path = os.path.join(BASE_DIR, "comparison_chart.png")
plt.savefig(chart_path, dpi=150)
print(f"Saved chart -> {chart_path}")

# ---------------------------------------------------------------
# 2. Markdown report
# ---------------------------------------------------------------
lines = ["# Model Comparison Report\n"]
lines.append("![Comparison Chart](comparison_chart.png)\n")
lines.append("| Metric | " + " | ".join(models) + " |")
lines.append("|---" * (len(models) + 1) + "|")
for label, m in zip(metric_labels, metrics):
    row = [label] + [f"{results[model][m]*100:.2f}%" for model in models]
    lines.append("| " + " | ".join(row) + " |")

lines.append("\n## Overfitting Check (train accuracy - test accuracy)\n")
for model in models:
    gap = (results[model]["train_accuracy"] - results[model]["test_accuracy"]) * 100
    lines.append(f"- **{model}**: {gap:+.2f} points")

best = max(models, key=lambda m: results[m]["f1"])
lines.append(f"\n## Best Model: **{best}** (highest F1-score)")

report_path = os.path.join(BASE_DIR, "report.md")
with open(report_path, "w") as f:
    f.write("\n".join(lines))
print(f"Saved report -> {report_path}")
print("\nOpen 'report.md' in VS Code and click 'Open Preview' (top-right icon, or Ctrl+Shift+V)")
