# AI & Machine Learning Exercises

This repository contains hands-on exercises, notebooks, and small projects created while studying Artificial Intelligence (AI), Machine Learning (ML), and early MLOps practices.

The goal is to turn theory into working code, compare approaches, and build intuition through experiments on real datasets.

## Topics Covered

- Core ML workflow: preprocessing, scaling, feature engineering, train/test splits, and evaluation.
- Supervised learning: linear regression, logistic regression, SVMs, Naive Bayes, k-nearest neighbors, and SGD-based models.
- Unsupervised learning: clustering with K-Means.
- Model evaluation: regression and classification metrics, confusion matrices, ROC curves, and learning curves.
- Domain exercises: tabular prediction, text classification (spam detection), digit recognition, and basic face recognition.
- MLOps foundations: serving a training endpoint with FastAPI and validating it with pytest.

## Technologies & Tools

- Language and environment: Python, Jupyter Notebooks.
- Core data stack: NumPy, Pandas.
- Visualization: Matplotlib, Seaborn.
- Machine learning: scikit-learn, SciPy.
- Data sources and helpers: ucimlrepo.
- App and APIs: FastAPI, Pydantic, Uvicorn.
- Testing: pytest, FastAPI TestClient.
- Computer vision (notebook experiments): OpenCV (`cv2`).

## Repository Structure

Below is a high-level map of the repository:

```text
.
├─ README.md
├─ ML_foundamentals/
│  ├─ Linear Regression/
│  ├─ Logistic Regression/
│  └─ Clustering/
├─ ML_Models&Algorithms/
│  ├─ SVM/
│  ├─ NaiveBayes/
│  ├─ Nearest Neighbors/
│  ├─ Mini Batch GD and Online Learning/
│  └─ Neural Networks/
└─ MLOps&ML_in_prod/
   └─ Model_Testing/
```