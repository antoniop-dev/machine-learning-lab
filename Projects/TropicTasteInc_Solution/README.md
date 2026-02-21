# TropicTasteInc Solution

TropicTasteInc is a notebook-based classification project that predicts fruit type from physical and taste-related measurements.
The pipeline uses a K-Nearest Neighbors (KNN) model with cross-validated hyperparameter selection.

## Project Goal

- Classify fruits into 5 categories: `Mela`, `Banana`, `Arancia`, `Uva`, `Kiwi`.
- Build a reliable KNN classifier with proper scaling.
- Select the best `K` through stratified cross-validation using macro F1-score.

## Dataset

- Local file: `fruits.csv`.
- Shape: `500` rows, `6` columns.
- Class distribution: balanced (`100` samples per fruit class).
- Target column: `Frutto`.
- Features include `Peso (g)`, `Diametro medio (mm)`, `Lunghezza media (mm)`, `Durezza buccia (1-10)`, `Dolcezza (1-10)`.

## Workflow

The full workflow is in `TropicalTasteInc.ipynb`:

1. Load and inspect dataset.
2. Exploratory analysis (data quality checks, descriptive statistics, correlation matrix).
3. Train/test split (`80/20`, stratified).
4. PCA projection (diagnostic visualization only).
5. Model selection by evaluating odd `K` values from `1` to `25`.
6. 5-fold stratified CV with `f1_macro`.
7. Select `best_k`.
8. Final training and evaluation on held-out test set.
9. Metrics and confusion matrix visualization.
10. Optional model export (pickle artifact).

## Model and Results

- Model: `Pipeline(StandardScaler -> KNeighborsClassifier)`.
- Hyperparameter tuning: cross-validation over odd `K` values.
- Reported notebook performance on test set: Accuracy `0.94`, Macro F1-score `0.94`.

## Requirements

- Python 3.9+
- Jupyter Notebook or JupyterLab
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`
- `seaborn`

Install example:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter
```

## Run

From `Projects/TropicTasteInc_Solution`:

```bash
jupyter notebook TropicalTasteInc.ipynb
```

Run all cells in order.

## Notes

- The notebook currently loads data from a remote URL; you can switch to local `fruits.csv` if preferred.
- Model artifacts are generated locally and ignored by Git (`*.pickle`).
- To export a model from the notebook, set `DOWNLOAD = True` in the final cell.

## Project Structure

```text
TropicTasteInc_Solution/
├─ README.md
├─ TropicalTasteInc.ipynb
└─ fruits.csv
```
