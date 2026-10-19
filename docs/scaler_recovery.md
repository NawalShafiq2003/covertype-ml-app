# Preprocessing recovery (evidence)

The training CSVs (`covertype_train.csv`, `covertype_test.csv`) were already standardized
and the fitted `StandardScaler` was never saved. Because the Flask form takes real-world
values, the scaler was recovered from the CSVs instead of being re-fitted on a single record.

Method
1. Each of the 10 original numeric columns is integer-valued in the raw UCI data, so the
   gap between consecutive distinct standardized values equals 1/scale exactly.
2. The raw minimum of each column is known (Elevation 1859, Slope 0, Vertical_Distance -173 ...),
   which fixes the integer offset; a least-squares fit of z on raw x gives mean and scale.
3. `Distance_To_Hydrology = sqrt(H^2+V^2)` and `Hillshade_Mean = mean(3 hillshades)` were
   fitted the same way from the reconstructed raw values.
4. One-hot baselines: `Wilderness_Area_1` and `Soil_Type_1` are all-zero baselines; rows with
   Soil_Type 7, 8, 15, 36 (105+179+3+119 = 406 rows) were removed before training.

Verification
* Maximum fit residual about 1e-14 for all 12 scaled columns.
* Recovered raw ranges match the published Covertype ranges.
* Raw-input pipeline vs. original CSV->RandomForest path on all 116,122 test rows:
  max probability difference 3.3e-16, 100% identical predictions.
* Test accuracy through the raw-input pipeline: 0.759959 (identical to model_comparison_results.json).
