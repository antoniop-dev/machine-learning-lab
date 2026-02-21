# RealEstateAI Solution

RealEstateAI is a notebook-based machine learning project for house price prediction.
The project focuses on building and comparing linear models on a real-estate dataset, with a full workflow from exploratory analysis to model evaluation.

## Project Goal

- Predict `price` from housing features.
- Compare two preprocessing strategies for `furnishingstatus`.
- Dataset A uses numeric encoding (`0/1/2`).
- Dataset B uses one-hot encoding.
- Evaluate which model and encoding perform best.

## Dataset

- Source file included in this repo: `data/housing.csv`.
- Shape: `545` rows, `13` columns.
- Target: `price`.
- Main features: `area`, `bedrooms`, `bathrooms`, `stories`, `parking`, binary amenities, and `furnishingstatus`.

## Workflow

Run notebooks in this order:

1. `notebooks/01_data_analysis.ipynb`
2. `notebooks/02_data_preprocessing.ipynb`
3. `notebooks/03_training.ipynb`
4. `notebooks/04_test_and_evaluate.ipynb`

What each notebook does:

- `01_data_analysis.ipynb`: sanity checks, summary statistics, correlation analysis.
- `02_data_preprocessing.ipynb`: train/test split, scaling, and Dataset A/B creation.
- `03_training.ipynb`: trains Linear Regression, Ridge, Lasso, and ElasticNet; includes basic hyperparameter search for regularized models.
- `04_test_and_evaluate.ipynb`: test metrics, cross-validation, coefficient analysis, residual plots, and learning curves.

## Main Results

- Test `R²` is around `0.72 - 0.74` across models.
- Ridge and ElasticNet are generally the strongest performers.
- Dataset A and Dataset B perform very similarly, suggesting limited predictive impact from alternative furnishing encoding in this dataset.

## Requirements

- Python 3.9+
- Jupyter Notebook or JupyterLab
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`
- `seaborn`

Example setup:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter
```

## Run

From `Projects/RealEstateAI_Solution`:

```bash
jupyter notebook
```

Then open and run the notebooks in the workflow order above.

## Notes

- `01_data_analysis.ipynb` and `02_data_preprocessing.ipynb` currently load the dataset from a remote URL; you can switch to `data/housing.csv` for fully local runs.
- Notebooks `03_training.ipynb` and `04_test_and_evaluate.ipynb` import helper modules from `../src` (`preprocessing.py`, `training.py`).
- If those modules are not present in your local setup, either add them or inline the preprocessing/training logic directly in the notebooks.

## Project Structure

```text
RealEstateAI_Solution/
├─ README.md
├─ data/
│  └─ housing.csv
├─ notebooks/
│  ├─ 01_data_analysis.ipynb
│  ├─ 02_data_preprocessing.ipynb
│  ├─ 03_training.ipynb
│  └─ 04_test_and_evaluate.ipynb
├─ learningCurves_setA.png
└─ learningCurves_setB.png
```
