# AI & Machine Learning Exercises and Projects

This repository collects hands-on exercises, notebooks, and project solutions built while studying Artificial Intelligence (AI), Machine Learning (ML), and early MLOps practices.

The focus is practical: turn theory into working code, compare approaches, and build intuition through experiments on real datasets and project-style scenarios.

## What You Will Find

- `Exercises/`: focused practice on ML fundamentals, core algorithms, and MLOps basics.
- `Projects/`: solution folders applying ML workflows to realistic business-style cases.

## Projects

| Project | Description |
|---|---|
| `MachineInnovatorsInc_Solution` | End-to-end sentiment analysis pipeline: fine-tuned transformer, FastAPI + React, Docker, CI/CD, monitoring |
| `RealEstateAI_Solution` | House price prediction with Linear, Ridge, Lasso, and ElasticNet regression (4-notebook workflow) |
| `GourmetAI_Solution` | Food image classification via transfer learning (ResNet50, MobileNetV3, EfficientNet-B0) |
| `GreenTech_Solution` | Image classification with ResNet50 and layer-4 fine-tuning on a Roboflow dataset |
| `VisionTech_Solution` | Computer vision notebook with a trained CNN (saved weights included) |
| `TropicTasteInc_Solution` | Single-notebook ML classification project |
| `InsuraPro_Solution` | C++17 terminal CRM with Doxygen-generated docs |
| `ContactEase_Solution` | Python console contact-book application |

### Highlighted MLOps Project

`Projects/MachineInnovatorsInc_Solution` is an end-to-end sentiment analysis project that includes:

- data retrieval and preprocessing pipeline
- model retrieval, fine-tuning, and evaluation pipelines
- FastAPI backend and React frontend
- Dockerized full-stack setup
- test suite (unit + integration + smoke)
- GitHub Actions workflows (nightly evaluation with threshold-based retrain decision & CPU-friendly mock retraining (no push/deploy))
- project-scoped CI test runs

Project docs:
- `Projects/MachineInnovatorsInc_Solution/README.md`

Repository: [MachineInnovators-SentimentAnalysis](https://github.com/antoniop-dev/machine-innovators-sentiment-analysis)

## Topics Covered

- Core ML workflow: preprocessing, scaling, feature engineering, train/test splits, and evaluation.
- Supervised learning: linear regression, logistic regression, SVMs, Naive Bayes, k-nearest neighbors, and SGD-based models.
- Unsupervised learning: clustering with K-Means.
- Model evaluation: regression and classification metrics, confusion matrices, ROC curves, and learning curves.
- Domain exercises: tabular prediction, text classification (spam detection, sentiment analysis), digit recognition, and basic face recognition.
- Deep learning: neural networks with callbacks, convolutional networks (AlexNet, transfer learning), recurrent networks (RNNs, LSTMs, GRUs, bidirectional), sequence-to-sequence machine translation, image captioning with mixed CNN+RNN architectures, food classification, and optical character recognition (OCR).
- Applied deep learning with PyTorch: regression and classification, CNNs on MNIST, data augmentation for data-scarce settings, and K-fold cross-validation.
- Computer vision: classical image filtering and Grad-CAM gradient visualisation.
- Reinforcement learning: value iteration and policy iteration on tabular/grid-world environments.
- MLOps foundations: serving a training endpoint with FastAPI and validating it with pytest.

## Technologies & Tools

- Languages and environment: Python, C++17, Jupyter Notebooks.
- Core data stack: NumPy, Pandas.
- Visualization: Matplotlib, Seaborn.
- Machine learning: scikit-learn, SciPy.
- Deep learning: TensorFlow, Keras, PyTorch.
- NLP/LLM tooling: Hugging Face Transformers, Datasets, Accelerate.
- Data sources and helpers: ucimlrepo.
- App and APIs: FastAPI, Pydantic, Uvicorn.
- Frontend and build: React, Vite.
- Containerization: Docker, Docker Compose, Nginx.
- Testing: pytest, FastAPI TestClient.
- CI/CD automation: GitHub Actions.
- Computer vision (notebook experiments): OpenCV (`cv2`).

## Repository Structure

```text
.
├─ README.md
├─ Exercises/
│  ├─ Applied DeepLearning with PyTorch/
│  │  ├─ CNNs/
│  │  ├─ Data Scarcity/
│  │  ├─ PyTorch101/
│  │  └─ Validation/
│  ├─ Computer Vision/
│  │  ├─ Filters/
│  │  └─ GradCAM/
│  ├─ DeepLearning and Neural Networks/
│  │  ├─ CNNs/
│  │  ├─ FoodOrNoFood/
│  │  ├─ MachineTranslation/
│  │  ├─ MixedArchitectures/
│  │  ├─ NNs/
│  │  ├─ OCR/
│  │  ├─ RNNs/
│  │  └─ Transformers/
│  ├─ ML_foundamentals/
│  │  ├─ Clustering/
│  │  ├─ Linear Regression/
│  │  └─ Logistic Regression/
│  ├─ ML_Models&Algorithms/
│  │  ├─ Mini Batch GD and Online Learning/
│  │  ├─ NaiveBayes/
│  │  ├─ Nearest Neighbors/
│  │  ├─ Neural Networks/
│  │  └─ SVM/
│  ├─ MLOps&ML_in_prod/
│  │  └─ Model_Testing/
│  └─ Reinforcement Learning/
│     ├─ Policy Iteration/
│     └─ Value Iteration/
└─ Projects/
   ├─ ContactEase_Solution/
   ├─ GourmetAI_Solution/
   ├─ GreenTech_Solution/
   ├─ InsuraPro_Solution/
   ├─ MachineInnovatorsInc_Solution/
   ├─ RealEstateAI_Solution/
   ├─ TropicTasteInc_Solution/
   └─ VisionTech_Solution/
```
