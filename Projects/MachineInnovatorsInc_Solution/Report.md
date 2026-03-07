# Project Report - MachineInnovatorsInc Solution

## 1. Project Objective

The goal of this solution is to build an end-to-end sentiment analysis system for social-media-like text, with an MLOps focus on:
- automation of data/model pipelines
- application deployment (API + user interface)
- reliability through testing
- periodic monitoring with retraining decision logic

## 2. Choice to Build Separate Pipelines with JSON Configs

I split the workflow into separate pipelines:
- data retrieval and preprocessing
- base model retrieval
- training
- evaluation

Each pipeline is configurable through JSON files in `configs/`.

Why:
- clear separation of responsibilities
- easier maintenance and extension
- reproducible runs
- parameter changes without code edits

Practical impact:
- the same codebase supports local development, CI runs, nightly jobs, and manual execution.

## 3. Choice to Expose CLI Scripts for Automation

I created CLI-executable scripts (`scripts/*.py`) as operational entrypoints.

Why:
- simpler integration with GitHub Actions and Docker
- standardized run commands across environments
- runtime overrides from CLI for different contexts (for example, reduced samples in CI)

Practical impact:
- workflow YAML files stay clean, while business logic remains in Python.

## 4. Choice to Build a Simple Backend + Frontend App

To simulate a real business environment, I implemented:
- a FastAPI backend for inference (`/api/v1/health`, `/api/v1/predict`)
- a React frontend for user interaction and sentiment visualization

Why:
- validates the model in a full application flow
- makes the project easier to demo to non-technical stakeholders
- proves integration between ML components and a serving application

## 5. Choice to Add Docker and Docker Compose

I containerized both services:
- backend Dockerfile (Python 3.11)
- frontend multi-stage Dockerfile (Vite build + Nginx serving)
- `docker-compose.yml` for service orchestration

Why:
- reproducible runtime environment
- quick full-stack startup
- reduced local setup issues

Practical impact:
- standard startup with `docker compose up -d`.

## 6. Technology Choices

### Backend
- FastAPI, Uvicorn, Pydantic
- Hugging Face Transformers + Datasets
- PyTorch / Accelerate

Rationale:
- robust stack for modern NLP training and inference
- native compatibility with the Hugging Face ecosystem

### Frontend
- React + Vite
- Fetch API for backend communication
- Nginx for containerized production serving

Rationale:
- lightweight UI suitable for PoC and operational demos
- simple setup with room for future expansion

## 7. Testing Strategy (Unit, Integration, Smoke)

I implemented three testing layers:
- unit tests (modules, utilities, API contracts)
- integration test (train/eval pipeline on reduced data)
- smoke test (runtime API check on a running service)

Why:
- reduces regressions
- validates both isolated components and end-to-end behavior
- keeps CI reliable even in CPU-only environments

## 8. Retraining Choice: Mock in CI, Real Retraining Outside CI

Due to hardware limits on standard GitHub runners (no suitable GPU for full retraining), the automated retraining workflow is intentionally a **mock retraining**:
- very small sample sizes
- 1 epoch
- CPU-friendly parameters
- no push/deploy of the mock model

Why:
- validates MLOps orchestration without excessive compute cost
- keeps CI execution time manageable

### Recommended approach for real retraining

Full retraining should be run manually in a GPU environment (for example, Google Colab), and then the new model version can be pushed to Hugging Face Hub.

Typical approach:
- run full training with a dedicated config (for example `configs/hf_training.json`)
- push using `hf_model_repo_id`

This cleanly separates:
- automation validation (CI)
- production-grade retraining (GPU environment)

## 9. GitHub Workflows Choice

I implemented modular workflows:
- `(MachineInnovatorsInc_Solution) Test Suite`
: unit + integration tests on push/PR/manual trigger
- `(MachineInnovatorsInc_Solution) Nightly Evaluation`
: nightly model evaluation + threshold check
- `(MachineInnovatorsInc_Solution) Mock Retraining`
: CPU-friendly mock retraining, callable manually or from nightly evaluation

I also added `check_retrain_needed.py` to:
- parse evaluation metrics
- compare them to configurable thresholds
- expose `retrain_needed=true/false` for conditional workflow triggering

## 10. Conclusion

The implementation choices prioritize modularity, reproducibility, automation, and practical compute constraints.

The project meets the core requirements with a realistic MLOps strategy:
- fast and reliable CI
- nightly monitoring with threshold-based decisions
- mock retraining in automation
- full retraining delegated to GPU-enabled environments (such as Colab) with versioning on Hugging Face Hub.
