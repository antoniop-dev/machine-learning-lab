# MachineInnovatorsInc Solution

End-to-end sentiment analysis application for online reputation monitoring.

The project includes:
- data retrieval and preprocessing pipeline (TweetEval sentiment)
- base model retrieval from Hugging Face
- fine-tuning and evaluation pipelines
- FastAPI backend for inference
- React frontend for user interaction
- unit, integration, and smoke tests

## Implemented stack

- `datasets`, `transformers`, `torch`, `accelerate`
- `fastapi`, `uvicorn`
- `react`, `vite`
- `docker`, `docker compose`
- `pytest`

## Repository layout

```text
MachineInnovatorsInc_Solution/
├── Dockerfile                    # backend container image
├── docker-compose.yml            # backend + frontend orchestration
├── .dockerignore
├── configs/                      # JSON configs for data/model/train/eval/api
├── scripts/                      # CLI entrypoints (pipeline, api, test, smoke)
├── src/machineinnovatorsinc_solution/
│   ├── data/                     # fetch + validate + preprocess pipeline
│   ├── model/                    # retrieve + train + evaluate pipelines
│   ├── api/                      # FastAPI app, routes, predictor, schemas
│   └── utils/
├── frontend/                     # React + Vite client (+ Dockerfile + nginx.conf)
├── tests/                        # unit + integration tests
├── artifacts/                    # generated model artifacts (gitignored)
├── data/                         # generated datasets (gitignored)
└── reports/                      # generated evaluation outputs (gitignored)
```

## Quick start

Run everything from this folder (`Projects/MachineInnovatorsInc_Solution`).

1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Retrieve and preprocess data

```bash
python3 scripts/fetch_data.py --config configs/data.json
```

3. Retrieve base model artifacts

```bash
python3 scripts/retrieve_model.py --config configs/model.json
```

4. Fine-tune model

```bash
python3 scripts/train_model.py \
  --dataset-id-or-path data/processed/tweet_eval_sentiment \
  --model-id-or-path artifacts/model/base \
  --output-dir artifacts/model/finetuned \
  --num-train-epochs 1 \
  --train-batch-size 2 \
  --eval-batch-size 2
```

5. Evaluate fine-tuned model

```bash
python3 scripts/evaluate_model.py \
  --dataset-id-or-path data/processed/tweet_eval_sentiment \
  --model-id-or-path artifacts/model/finetuned \
  --output-dir reports
```

## Run with Docker

Build images:

```bash
docker compose build
```

Start the full stack (backend + frontend + monitoring):

```bash
docker compose up -d
```

Services:
- frontend: `http://localhost:8080`
- backend API: `http://localhost:8000/api/v1`
- startup traffic seeder: one-shot synthetic load against backend `/predict`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (`admin` / `admin`)

Stop containers:

```bash
docker compose down
```

Notes:
- frontend runs on Nginx and proxies `/api/*` to the `backend` service.
- the backend container starts with `uvicorn machineinnovatorsinc_solution.api.app:create_app --factory --host 0.0.0.0 --port 8000`.
- the `traffic-seeder` service waits for backend health and then sends 250 synthetic prediction requests at startup.
- first startup may take longer while model assets are downloaded.

## Run the backend API

Start server:

```bash
python3 scripts/serve.py --config configs/api.json
```

Default API base URL:
- `http://localhost:8000/api/v1`

Endpoints:
- `GET /health`
- `POST /predict`

Example:

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"I absolutely love this product"}'
```

Example response:

```json
{
  "label": "positive",
  "label_id": 2,
  "scores": {
    "negative": 0.01,
    "neutral": 0.08,
    "positive": 0.91
  }
}
```

Metrics endpoint:
- `GET /metrics`

Example:

```bash
curl http://localhost:8000/metrics
```

## Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite dev server runs at `http://localhost:5173` and proxies `/api/*` to the backend at `http://localhost:8000`.

For deployed setups, set:
- `VITE_API_BASE_URL` (defaults to `/api/v1`)

## Testing

Run all tests:

```bash
python3 scripts/test.py
```

Run a specific test file:

```bash
python3 scripts/test.py tests/test_api.py -v
```

Run smoke test against a running backend:

```bash
python3 scripts/smoke_test.py
```

## Monitoring with Prometheus and Grafana

The Docker Compose stack includes:
- `traffic-seeder`, which sends one-shot synthetic `/predict` traffic at startup for dashboard seeding
- `prometheus`, which scrapes backend metrics from `http://backend:8000/metrics`
- `grafana`, preconfigured with Prometheus as the default datasource

The startup traffic generator can also be run manually:

```bash
python3 scripts/seed_prediction_traffic.py --base-url http://localhost:8000/api/v1 --count 250
```

Useful API metrics:
- `prediction_requests_total{status, predicted_label}`: number of served predictions, split by result label
- `prediction_request_duration_seconds{status}`: prediction latency histogram
- `prediction_input_chars`: input text-length histogram

## GitHub Actions Workflows

The repository includes CI/CD workflows for this project under `.github/workflows/`:

- `(MachineInnovatorsInc_Solution) Test Suite` (`.github/workflows/test_machineinnovatorsinc_solution.yml`)
- `(MachineInnovatorsInc_Solution) Nightly Evaluation` (`.github/workflows/nightly_evaluate.yml`)
- `(MachineInnovatorsInc_Solution) Mock Retraining` (`.github/workflows/retrain_model.yml`)

### Test Suite workflow

Purpose:
- runs project tests on push/PR changes affecting `Projects/MachineInnovatorsInc_Solution/**`
- also supports manual trigger with `workflow_dispatch`

Behavior:
- unit test job runs `test_utils`, `test_data`, `test_model`, `test_api`
- integration job prepares a small processed dataset and runs `test_integration_pipeline.py`
- uploads JUnit XML reports as build artifacts

### Nightly Evaluation workflow

Purpose:
- runs scheduled model evaluation each night
- decides whether mock retraining should be triggered

Behavior:
- fetches/preprocesses data
- runs `scripts/evaluate_model.py`
- runs `scripts/check_retrain_needed.py` against `reports/nightly/eval_metrics.json`
- uploads `reports/nightly` artifacts (evaluation log + decision JSON)
- conditionally calls the mock retraining workflow when thresholds are not met

Thresholds:
- default minimum accuracy: `0.80`
- default minimum macro F1: `0.78`
- configurable via repo variables:
- `NIGHTLY_MIN_ACCURACY`
- `NIGHTLY_MIN_MACRO_F1`
- `NIGHTLY_MODEL_ID_OR_PATH`
- `NIGHTLY_MAX_EVAL_SAMPLES`

### Mock Retraining workflow

Purpose:
- validate retraining automation in CI with CPU-friendly settings
- avoid production-level GPU training in GitHub Actions

Behavior:
- supports manual trigger (`workflow_dispatch`) and reusable trigger (`workflow_call`)
- runs data fetch (if processed data is missing)
- runs tiny-sample training and evaluation
- uploads logs and model metadata artifacts

Important constraints:
- no push to Hugging Face
- no deployment
- intended only for automation validation

## Config files

- `configs/data.json`: data pipeline settings (`dataset_name`, splits, `data_dir`, preprocessing knobs)
- `configs/model.json`: base model retrieval settings (`model_id`, label mapping, output artifacts path)
- `configs/training.json`: fine-tuning settings for local runs (dataset/model/output paths and hyperparameters)
- `configs/hf_training.json`: fine-tuning settings for Hugging Face-oriented runs (`hf_model_repo_id` included)
- `configs/api.json`: API settings (`model_repo_id`, `max_length`, `device`, `log_level`)
- `configs/hf_data.json`: data pipeline config variant with `hf_dataset_repo_id` for push to Hugging Face Hub

## Generated outputs

Main generated outputs:
- `data/raw/tweet_eval_sentiment/`
- `data/processed/tweet_eval_sentiment/`
- `artifacts/model/base/`
- `artifacts/model/finetuned/`
- `reports/eval_metrics.json`

These paths are gitignored at repository level.
