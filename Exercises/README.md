# Learning Path

This is the order I'd actually follow through this repo if I were starting over. Each exercise track builds a specific skill, and once you're comfortable with it, the linked project in `Projects/` shows that same skill applied to a more realistic, end-to-end problem. Do the exercises first, then go read (or run) the companion project — you'll recognize the same ideas, just under more real-world pressure (imbalanced classes, messy data, production constraints, etc.).

You don't have to follow this order strictly, but each stage generally assumes comfort with the ones before it.

## Prerequisites

- Python 3.10+ and Jupyter (`pip install notebook` or `jupyter notebook` via your environment manager of choice).
- A dedicated virtual environment (venv or conda) is strongly recommended — some exercises pull in heavy deep-learning dependencies (TensorFlow, PyTorch) that are easier to manage in isolation.
- No prior deep learning background assumed at step 1; tracks 4 onward assume you're comfortable with steps 1–3.

## The Path

| # | Track | Folder | What you'll learn | Companion project |
|---|-------|--------|--------------------|--------------------|
| 1 | ML Foundamentals | [`ML_foundamentals/`](ML_foundamentals) | Linear & logistic regression, clustering — the core ML workflow: fit, predict, evaluate. | [`RealEstateAI_Solution`](../Projects/RealEstateAI_Solution) |
| 2 | ML Models & Algorithms | [`ML_Models&Algorithms/`](ML_Models&Algorithms) | SVM, Naive Bayes, k-NN, SGD/mini-batch and online learning, basic neural networks. | [`TropicTasteInc_Solution`](../Projects/TropicTasteInc_Solution) |
| 3 | MLOps & ML in Prod | [`MLOps&ML_in_prod/`](MLOps&ML_in_prod) | Serving a trained model behind an API and testing it — your first taste of ML outside a notebook. | [`MachineInnovatorsInc_Solution`](../Projects/MachineInnovatorsInc_Solution) |
| 4 | Deep Learning and Neural Networks | [`DeepLearning and Neural Networks/`](DeepLearning%20and%20Neural%20Networks) | Feedforward nets, CNNs, RNNs/LSTMs/GRUs, seq2seq translation, OCR, transformer-based sentiment analysis (Keras/TensorFlow). | [`VisionTech_Solution`](../Projects/VisionTech_Solution) |
| 5 | Applied Deep Learning with PyTorch | [`Applied DeepLearning with PyTorch/`](Applied%20DeepLearning%20with%20PyTorch) | The same deep learning ideas rebuilt in PyTorch: regression/classification from scratch, CNNs on MNIST, data augmentation for scarce data, k-fold validation. | [`GourmetAI_Solution`](../Projects/GourmetAI_Solution) |
| 6 | Computer Vision | [`Computer Vision/`](Computer%20Vision) | Classical image filtering and Grad-CAM — how to look inside a CNN's decisions on image data. | [`GreenTech_Solution`](../Projects/GreenTech_Solution) |
| 7 | Reinforcement Learning | [`Reinforcement Learning/`](Reinforcement%20Learning) | Value/policy iteration, Q-learning, SARSA, Dyna-Q, DQN, REINFORCE — learning through interaction instead of labeled data. | [`DeepGuard_Solution`](../Projects/DeepGuard_Solution) |
| 8 | Generative AI | [`Generative AI/`](Generative%20AI) | Autoencoders, GANs, VAEs, diffusion models, GRU-based text generation, transformers — models that create rather than just predict. | [`CyberEye_Solution`](../Projects/CyberEye_Solution) |
| 9 | eXplainable AI (XAI) | [`eXplainable AI (XAI)/`](eXplainable%20AI%20%28XAI%29) | Whitebox models, LIME, SHAP, and CV attribution methods (saliency, integrated gradients, occlusion, Grad-CAM) — understanding *why* a model made a prediction, not just what it predicted. | [`BancaVirtuosa_Solution`](../Projects/BancaVirtuosa_Solution) |

Two projects sit outside this path entirely — `InsuraPro_Solution` (C++ terminal CRM) and `ContactEase_Solution` (Python console app) — general software-engineering practice rather than ML.

## Why This Order

- **1–3** cover the ML fundamentals almost every later track leans on: fitting a model, evaluating it honestly, and getting it to serve predictions outside a notebook. If you're new to ML, don't skip 3 — it's a small exercise, but "a model that runs in a notebook" and "a model that serves a request" are different problems, and the earlier you feel that difference the better.
- **4–6** are all deep learning, but deliberately from two angles: track 4 works in Keras/TensorFlow, track 5 rebuilds the same intuition in PyTorch, and track 6 narrows in on computer vision specifically. Seeing the same concepts in two frameworks is more useful than it sounds — it's what tells you which parts of your understanding were framework-specific habits versus the actual idea.
- **7–8** are less "predict a label" and more "learn a behavior" (RL) or "generate new data" (generative models) — conceptually a bigger jump, so they come after the supervised-learning foundation is solid.
- **9 (XAI)** comes last on purpose: explainability techniques are most useful once you've actually built and trained a few models and have felt the pain of not knowing why one failed.
