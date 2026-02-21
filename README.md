# AI & Machine Learning Exercises and Projects

This repository collects hands-on exercises, notebooks, and project solutions built while studying Artificial Intelligence (AI), Machine Learning (ML), and early MLOps practices.

The focus is practical: turn theory into working code, compare approaches, and build intuition through experiments on real datasets and project-style scenarios.

## What You Will Find

- `Exercises/`: focused practice on ML fundamentals, core algorithms, and MLOps basics.
- `Projects/`: solution folders applying ML workflows to realistic business-style cases.

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

```text
.
├─ README.md
├─ Exercises/
│  ├─ ML_foundamentals/
│  │  ├─ Linear Regression/
│  │  ├─ Logistic Regression/
│  │  └─ Clustering/
│  ├─ ML_Models&Algorithms/
│  │  ├─ SVM/
│  │  ├─ NaiveBayes/
│  │  ├─ Nearest Neighbors/
│  │  ├─ Mini Batch GD and Online Learning/
│  │  └─ Neural Networks/
│  └─ MLOps&ML_in_prod/
|     └─ Model_Testing/
└─ Projects/
   ├─ ContactEase_Solution/
   ├─ InsuraPro_Solution/
   ├─ RealEstateAI_Solution/
   └─ TropicTasteInc_Solution/
```