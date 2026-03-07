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
python3 scripts/train_model.py --config configs/training.json
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

Start the full stack (backend + frontend):

```bash
docker compose up -d
```

Services:
- frontend: `http://localhost:8080`
- backend API: `http://localhost:8000/api/v1`

Stop containers:

```bash
docker compose down
```

Notes:
- frontend runs on Nginx and proxies `/api/*` to the `backend` service.
- the backend container starts with `uvicorn machineinnovatorsinc_solution.api.app:create_app --factory --host 0.0.0.0 --port 8000`.
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

## Config files

- `configs/data.json`: data pipeline settings (`dataset_name`, splits, `data_dir`, preprocessing knobs)
- `configs/model.json`: base model retrieval settings (`model_id`, label mapping, output artifacts path)
- `configs/training.json`: fine-tuning settings (`processed_data_dir`, hyperparameters, output path)
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
