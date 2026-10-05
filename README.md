# AI & Machine Learning Exercises and Projects

This repository collects hands-on exercises, notebooks, and project solutions built while studying Artificial Intelligence (AI), Machine Learning (ML), and early MLOps practices.

The focus is practical: turn theory into working code, compare approaches, and build intuition through experiments on real datasets and project-style scenarios.

## What You Will Find

- `Exercises/`: focused practice on ML fundamentals, core algorithms, and MLOps basics. New to ML? Start with [`Exercises/README.md`](Exercises/README.md) for the recommended learning path and how each track links to a project below.
- `Projects/`: solution folders applying ML workflows to realistic business-style cases.

## Projects

| Project | Description |
|---|---|
| [`MachineInnovatorsInc_Solution`](Projects/MachineInnovatorsInc_Solution/README.md) | End-to-end sentiment analysis pipeline: fine-tuned transformer, FastAPI + React, Docker, CI/CD, monitoring |
| [`CyberEye_Solution`](Projects/CyberEye_Solution/README.md) | Synthetic data augmentation pipeline (BLIP captioning → T5 paraphrasing → SD-Turbo img2img) with CLIP quality gates, measured against a baseline classifier |
| [`DeepGuard_Solution`](Projects/DeepGuard_Solution/README.md) | RL-based automated cyber defense on gym-idsgame (SARSA and DDQN defenders vs. random/maximal attacker bots) |
| [`BancaVirtuosa_Solution`](Projects/BancaVirtuosa_Solution/README.md) | Audit-ready explainability for a transfer-learned DenseNet-121 classifier: five saliency techniques (Grad-CAM, Integrated Gradients, Occlusion, LIME, SHAP) compared on a fixed, seeded case set of correct and misclassified digits |
| [`RealEstateAI_Solution`](Projects/RealEstateAI_Solution/README.md) | House price prediction with Linear, Ridge, Lasso, and ElasticNet regression (4-notebook workflow) |
| [`GourmetAI_Solution`](Projects/GourmetAI_Solution/README.md) | Food image classification via transfer learning (ResNet50, MobileNetV3, EfficientNet-B0) |
| [`GreenTech_Solution`](Projects/GreenTech_Solution/README.md) | Image classification with ResNet50 and layer-4 fine-tuning on a Roboflow dataset |
| [`VisionTech_Solution`](Projects/VisionTech_Solution/README.md) | Computer vision notebook with a trained CNN (saved weights included) |
| [`TropicTasteInc_Solution`](Projects/TropicTasteInc_Solution/README.md) | Single-notebook ML classification project |
| [`InsuraPro_Solution`](Projects/InsuraPro_Solution/README.md) | C++17 terminal CRM with Doxygen-generated docs |
| [`ContactEase_Solution`](Projects/ContactEase_Solution/README.md) | Python console contact-book application |

## Compute Requirements

Most exercises and a few projects (RealEstateAI, TropicTasteInc, InsuraPro, ContactEase) are small enough to run comfortably on a laptop CPU. The deep-learning-heavy projects (transfer learning, diffusion, transformer fine-tuning) are a different story — training them from scratch on a CPU is realistic only if you're prepared to wait a long time. For those, use a GPU: either your own, or a free option like [Google Colab](https://colab.research.google.com/).

- **GourmetAI_Solution**, **GreenTech_Solution** — PyTorch transfer learning; trained on Colab (see each project's own README for a "Compute" section with Colab setup steps).
- **BancaVirtuosa_Solution** — the notebook ships a `PROTOTYPE_CONFIG` (small, fast, runs locally) and a `FULL_CONFIG` (the full run, intended for Colab); it also auto-installs missing packages and mounts Drive when it detects it's on Colab.
- **CyberEye_Solution** — picks CUDA → Apple MPS → CPU automatically, so the same notebooks run on a laptop for local validation at reduced scale, then uncapped on Colab for the full pipeline.
- **MachineInnovatorsInc_Solution** — the CI/CD pipeline intentionally uses a CPU-friendly mock retrain (see its README); a real fine-tuning run of `scripts/train_model.py` should be done on a GPU machine or Colab, not CI.

If you're new to this: you don't need to buy a GPU to work through this repo. Colab's free tier covers everything here.

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

- Core ML workflow: preprocessing, scaling, feature engineering, train/test splits and evaluation.
- Supervised learning: linear regression, logistic regression, SVMs, Naive Bayes, k-nearest neighbors, and SGD-based models.
- Unsupervised learning: clustering with K-Means.
- Model evaluation: regression and classification metrics, confusion matrices, ROC curves, and learning curves.
- Domain exercises: tabular prediction, text classification (spam detection, sentiment analysis), digit recognition, and basic face recognition.
- Deep learning: neural networks with callbacks, convolutional networks (AlexNet, transfer learning), recurrent networks (RNNs, LSTMs, GRUs, bidirectional), sequence-to-sequence machine translation, image captioning with mixed CNN+RNN architectures, food classification, and optical character recognition (OCR).
- Applied deep learning with PyTorch: regression and classification, CNNs on MNIST, data augmentation for data-scarce settings, and K-fold cross-validation.
- Generative AI: autoencoders, generative adversarial networks (GANs), variational autoencoders (VAE, conditional VAE) on MNIST/CIFAR-10, and diffusion models (DDPM-style U-Net denoising).
- Sequence models and transformers: GRU-based character-level text generation, transformer encoder/decoder blocks with attention visualisation, and encoder-decoder machine translation.
- LLM applications: prompt engineering with local on-device inference (MLX) and abstractive summarization (T5/GPT-2/encoder-decoder models).
- Explainable AI (XAI): whitebox interpretable models (logistic regression, decision trees), post-hoc explainability with LIME (tabular data, kNN and MLP models) and SHAP (linear/tree models and XGBoost regression/classification), and computer-vision attribution methods (saliency maps, integrated gradients, occlusion, Grad-CAM) on CIFAR-10; plus a compliance-oriented case study that runs five attribution techniques (Grad-CAM, integrated gradients, occlusion, LIME, SHAP) over one fixed case set to explain a transfer-learned classifier's errors, and weighs post-hoc explanation against explainable-by-design alternatives.
- Synthetic data generation: multi-model pipeline chaining image captioning (BLIP), caption paraphrasing (T5), and diffusion img2img (SD-Turbo), with CLIPScore quality gates and a controlled baseline-vs-augmented classifier experiment to measure whether the generated data actually helps.
- Computer vision: classical image filtering and Grad-CAM gradient visualisation.
- Reinforcement learning: value iteration and policy iteration on tabular/grid-world environments, and RL-based cyber defense (SARSA, DDQN) on a Markov-game intrusion environment.
- MLOps foundations: serving a training endpoint with FastAPI and validating it with pytest.

## Technologies & Tools

- Languages and environment: Python, C++17, Jupyter Notebooks.
- Core data stack: NumPy, Pandas.
- Visualization: Matplotlib, Seaborn.
- Machine learning: scikit-learn, SciPy, XGBoost.
- Deep learning: TensorFlow, Keras, PyTorch (with TensorBoard logging).
- NLP/LLM tooling: Hugging Face Transformers, Datasets, Accelerate, MLX (local LLM inference), BertViz (attention visualization).
- Generative model tooling: Hugging Face Diffusers, NLTK and rouge-score for text-similarity metrics.
- Explainability: SHAP, LIME, Captum (saliency maps, integrated gradients, occlusion, Grad-CAM).
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
│  ├─ eXplainable AI (XAI)/
│  │  ├─ Computer Vision/
│  │  ├─ LIME/
│  │  ├─ SHAP/
│  │  └─ WhiteBox/
│  ├─ Generative AI/
│  │  ├─ Autoencoders/
│  │  ├─ Diffusion Models/
│  │  ├─ Gated Recurrent Unit (GRU)/
│  │  ├─ Generative Adversarial Networks (GANs)/
│  │  ├─ Large Language Models (LLMs)/
│  │  ├─ Transformers/
│  │  └─ Variational Autoencoders (VAE)/
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
│     ├─ Deep Q-Network/
│     ├─ Dyna-Q/
│     ├─ Policy Iteration/
│     ├─ Q-Learning/
│     ├─ Reinforce (Monte Carlo Policy Gradient)/
│     ├─ SARSA/
│     └─ Value Iteration/
└─ Projects/
   ├─ BancaVirtuosa_Solution/
   ├─ ContactEase_Solution/
   ├─ CyberEye_Solution/
   ├─ DeepGuard_Solution/
   ├─ GourmetAI_Solution/
   ├─ GreenTech_Solution/
   ├─ InsuraPro_Solution/
   ├─ MachineInnovatorsInc_Solution/
   ├─ RealEstateAI_Solution/
   ├─ TropicTasteInc_Solution/
   └─ VisionTech_Solution/
```
