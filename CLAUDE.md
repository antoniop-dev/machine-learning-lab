# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A learning lab for AI/ML exercises and project solutions. Content is organized into:
- `Exercises/`: focused notebooks and scripts covering ML fundamentals through deep learning and MLOps basics.
- `Projects/`: solution folders for business-style ML problems.

Data files, model artifacts (`.h5`, `.pkl`, `.pt`, etc.), and most generated outputs are gitignored.

---

## Exercises

All notebook-based exercises run via Jupyter:

```bash
jupyter notebook
```

### Structure

| Folder | Topics |
|--------|--------|
| `Exercises/ML_foundamentals/` | Linear/Logistic Regression, Clustering |
| `Exercises/ML_Models&Algorithms/` | SVM, Naive Bayes, kNN, SGD/Mini-batch, Neural Networks |
| `Exercises/DeepLearning/NNs/` | Feedforward networks with callbacks |
| `Exercises/DeepLearning/CNNs/` | AlexNet, transfer learning, rural/urban image classification |
| `Exercises/DeepLearning/RNNs/` | RNNs, LSTMs, GRUs, bidirectional |
| `Exercises/DeepLearning/MachineTranslation/` | Seq2seq translation |
| `Exercises/DeepLearning/OCR/` | EMNIST-based character recognition |
| `Exercises/DeepLearning/Transformers/` | Sentiment analysis with BERT |
| `Exercises/MLOps&ML_in_prod/Model_Testing/` | FastAPI training endpoint + pytest |

### MLOps/Model Testing exercise

Run the test from `Exercises/MLOps&ML_in_prod/Model_Testing/`:

```bash
pytest tests/test_app_training.py -v
```

The exercise exposes a `/training` POST endpoint via FastAPI that fits a `LinearRegression` and returns MSE. Tests use `fastapi.testclient.TestClient`.

---

## Projects

### MachineInnovatorsInc_Solution (main MLOps project)

End-to-end sentiment analysis (TweetEval dataset, fine-tuned transformer). Full docs in `Projects/MachineInnovatorsInc_Solution/README.md`.

Run everything from `Projects/MachineInnovatorsInc_Solution/`.

**Setup:**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Pipeline scripts** (in `scripts/`):
```bash
python3 scripts/fetch_data.py --config configs/data.json
python3 scripts/retrieve_model.py --config configs/model.json
python3 scripts/train_model.py --dataset-id-or-path data/processed/tweet_eval_sentiment \
  --model-id-or-path artifacts/model/base --output-dir artifacts/model/finetuned
python3 scripts/evaluate_model.py --dataset-id-or-path data/processed/tweet_eval_sentiment \
  --model-id-or-path artifacts/model/finetuned --output-dir reports
```

**Serve API:**
```bash
python3 scripts/serve.py --config configs/api.json
# → http://localhost:8000/api/v1  (GET /health, POST /predict)
```

**Tests:**
```bash
python3 scripts/test.py                        # all tests
python3 scripts/test.py tests/test_api.py -v   # single file
python3 scripts/smoke_test.py                  # smoke test against live backend
```

**Docker (full stack: backend + frontend + Prometheus + Grafana):**
```bash
docker compose build
docker compose up -d
# frontend: http://localhost:8080  backend: http://localhost:8000/api/v1
# Prometheus: http://localhost:9090  Grafana: http://localhost:3000 (admin/admin)
docker compose down
```

**Architecture:**
- `src/machineinnovatorsinc_solution/` — Python package with `api/`, `data/`, `model/`, `utils/` submodules.
- `scripts/` — CLI entrypoints that import from the package.
- `configs/` — JSON configs for each pipeline stage (`data.json`, `model.json`, `training.json`, `api.json`).
- `frontend/` — React + Vite app; Nginx proxies `/api/*` to backend in Docker.
- `monitoring/` — Prometheus scrape config and Grafana provisioning.
- `tests/` — unit, integration, and smoke tests; CI uploads JUnit XML artifacts.
- Generated paths (`data/`, `artifacts/`, `reports/`) are gitignored.

**GitHub Actions** (defined in repo-root `.github/workflows/`, scoped to `Projects/MachineInnovatorsInc_Solution/**`):
- Test Suite — runs on push/PR; separate unit and integration jobs.
- Nightly Evaluation — evaluates model, triggers mock retraining if accuracy < `NIGHTLY_MIN_ACCURACY` or macro-F1 < `NIGHTLY_MIN_MACRO_F1`.
- Mock Retraining — CPU-friendly tiny-sample retrain; no model push or deploy.

### RealEstateAI_Solution

Notebook workflow for house price prediction (Linear/Ridge/Lasso/ElasticNet). Run notebooks in order `01 → 04` from `Projects/RealEstateAI_Solution/`:

```bash
jupyter notebook
```

Notebooks `03` and `04` import helpers from `../src/` (`preprocessing.py`, `training.py`).

### InsuraPro_Solution

C++17 terminal CRM. Build and run from `Projects/InsuraPro_Solution/`:

```bash
g++ -std=c++17 -Wall -Wextra -Iinclude main.cpp src/*.cpp src/utilities/*.cpp -o insurapro
./insurapro
```

Generate Doxygen docs:
```bash
doxygen Doxyfile
# → open docs/html/index.html
```

### ContactEase_Solution

Python console contact book. Run from `Projects/ContactEase_Solution/`:

```bash
python main.py
```

### TropicTasteInc_Solution

Single notebook (`TropicalTasteInc.ipynb`) — open with `jupyter notebook`.
