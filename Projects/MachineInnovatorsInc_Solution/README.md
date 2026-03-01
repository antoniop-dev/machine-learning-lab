# Project Plan — Online Reputation Monitoring via Tweet Sentiment (MLOps-ready)

**Goal:** build a production-oriented sentiment analysis system for social media reputation monitoring (positive / neutral / negative), using:
- **Model (base):** `cardiffnlp/twitter-roberta-base-sentiment-latest` 
- **Dataset:** **TweetEval (sentiment)** (already split in train/validation/test)
- **Training loop:** Hugging Face **Trainer**
- **Deployment target:** Hugging Face Hub (model) + optional Hugging Face Space / Inference Endpoint (service)
- **MLOps:** monitoring + automated retraining pipeline (CI/CD)

---

## 0) Foundations and Repo Setup (before touching data) [DONE]
**Outcomes**
- A clean project structure and reproducible environment.
- Clear interfaces for training, evaluation, inference, and deployment.

**Steps**
1. Create repository structure (example) [DONE]:
   - `src/` (library code)
   - `scripts/` (CLI scripts: train/eval/push/infer)
   - `configs/` (JSON configs)
   - `tests/` (unit + integration)
   - `notebooks/` (Colab notebook for delivery)
2. Define environment management [DONE -> requirements.txt]:
   - `requirements.txt` or `pyproject.toml`
   - pin key libs: `transformers`, `datasets`, `evaluate`, `accelerate`, `torch`
3. Decide experiment logging strategy (at least one) [DONE -> minimal]:
   - minimal: JSON logs + saved metrics in repo artifacts
   - recommended: Weights & Biases / MLflow (optional but helpful)

---

## 1) Data Retrieval (TweetEval) [DONE]
**Outcome**
- Dataset downloaded locally (or via HF cache), inspected, and ready for tokenization.

**Steps**
1. Retrieve dataset using Hugging Face Datasets: [DONE]
   - load `tweet_eval` with subset `sentiment`
   - confirm splits: `train`, `validation`, `test`
2. Inspect dataset schema: [DONE]
   - text field name (usually `text`)
   - label field name (usually `label`)
   - label mapping (0/1/2 → neg/neu/pos)
3. Data governance notes (MLOps): [DONE]
   - store dataset “card” metadata in docs:
     - dataset version / source
     - license
     - label definitions
4. Define preprocessing rules: [DONE]
   - normalize whitespace
   - decide whether to keep emojis/hashtags (generally **keep** for Twitter sentiment)
   - decide max length (e.g., 128/256) based on cost vs performance

**Artifacts**
- `data/README.md` (what dataset, how loaded, label mapping)
- `configs/data.json` (dataset name, split names, fields)

---

## 2) Model Retrieval (from Hugging Face) [DONE]
**Outcome**
- Tokenizer + sequence classification model correctly loaded with label mappings.

**Steps**
1. Base model ID: `cardiffnlp/twitter-roberta-base-sentiment-latest`
2. Retrieve via:
   - `AutoTokenizer.from_pretrained(model_id)`
   - `AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=3)`
3. Set explicit label mappings (important for consistent eval + deployment):
   - `id2label = {0:"negative", 1:"neutral", 2:"positive"}`
   - `label2id = inverse mapping`
4. Confirm tokenizer settings:
   - padding/truncation strategy
   - special tokens handling

**Artifacts**
- `configs/model.json` (model id, num_labels, id2label/label2id, tokenizer settings)
- `scripts/retrieve_model.py` (CLI entrypoint)
- `artifacts/model/base/metadata.json` (retrieval metadata)

---

## 3) Fine-tune / Retrain (Trainer) [DONE]
**Outcome**
- A trained checkpoint saved locally, with training logs and metrics.

**Steps**
1. Tokenize dataset:
   - map tokenizer over `text` column
   - keep `labels` aligned with `label`
2. Define training configuration (general knobs):
   - batch size
   - learning rate
   - epochs
   - weight decay
   - warmup ratio/steps
   - evaluation strategy (e.g., per epoch)
   - early stopping (optional)
3. Define `compute_metrics`:
   - Accuracy
   - Macro F1 (recommended)
4. Train with `Trainer`:
   - set `output_dir` for checkpoints
   - enable best-checkpoint selection (based on macro F1 or accuracy)

**Artifacts**
- saved model checkpoint
- `training_args.json` (or config file)
- training logs (console + file)
- metric summary stored (JSON)
- `configs/training.json` (training config)
- `scripts/train_model.py` (CLI entrypoint)
- `artifacts/model/finetuned/metadata.json`
- `artifacts/model/finetuned/metrics.json`

**Run**
```bash
python3 scripts/train_model.py --config configs/training.json
```

Note: `configs/training.json` points to local pretrained artifacts (`artifacts/model/base`), so run model retrieval first.
Note: if your processed dataset was created with an older version of this pipeline, re-run `python3 scripts/fetch_data.py --config configs/data.json` so it is saved in native Hugging Face format.

---

## 4) Model Test (Functional + Integration)
**Outcome**
- Confidence that the pipeline works end-to-end (data → model → output).

**Steps**
1. **Smoke test** (very fast):
   - run inference on 5–10 sample tweets
   - verify outputs are one of {neg, neu, pos}
2. **Integration test**:
   - run a mini-training with a small subset (e.g., 1% of train) in CI
   - ensure training completes + produces artifacts
3. **Reproducibility test**:
   - set random seeds
   - ensure stable-ish metrics within tolerance

**Artifacts**
- `tests/test_inference.py`
- `tests/test_training_smoke.py`

---

## 5) Model Evaluation (Quantitative + Qualitative)
**Outcome**
- A clear performance report and error analysis suitable for documentation.

**Steps**
1. Evaluate on TweetEval `test` split:
   - report Accuracy + Macro F1
   - show confusion matrix
2. Error analysis:
   - inspect misclassified samples
   - identify common failure modes (sarcasm, negation, slang, topic-specific terms)
3. Bias / robustness checks (lightweight but useful):
   - check performance by tweet length bins
   - check sensitivity to emojis/hashtags
4. Define acceptance thresholds (MLOps):
   - minimum macro F1
   - maximum drop vs current “production” model

**Artifacts**
- `reports/eval_report.md`
- `reports/confusion_matrix.png`
- `reports/metrics.json`

---

## 6) Model Deployment (Hugging Face Hub)
**Outcome**
- Versioned model published with documentation and reproducible metadata.

**Steps**
1. Authenticate to HF (token in secrets for CI)
2. Push model artifacts:
   - weights + tokenizer + config (with id2label/label2id)
3. Add/update model card:
   - intended use (reputation monitoring)
   - training dataset (TweetEval)
   - metrics
   - limitations and ethical considerations
4. Tag releases / versions:
   - semantic versioning or date-based (e.g., `v1.0.0` / `2026-02-22`)

**Artifacts**
- HF repo with:
  - `config.json`
  - `tokenizer.json` / vocab files
  - `pytorch_model.bin` or safetensors
  - `README.md` (model card)

---

## 7) Model Inference (Local + Remote)
**Outcome**
- A repeatable method to run inference for new tweets.

**Steps**
1. Local inference:
   - script that loads the HF model and predicts sentiment on a list of texts
2. Remote inference options:
   - Hugging Face Inference API
   - Hugging Face Inference Endpoint (managed)
   - Hugging Face Space (demo UI)
3. Post-processing:
   - output label + confidence
   - optional thresholding (e.g., “uncertain” bucket for low confidence)

**Artifacts**
- `scripts/infer.py` (CLI)
- optional Space app (Gradio/Streamlit)

---

## 8) Model Implementation (Reputation Monitoring Application Layer)
**Outcome**
- A minimal “reputation monitoring” service workflow, ready for production integration.

**Steps**
1. Define ingestion sources (general):
   - social media APIs, internal company sources, or batch files
2. Data pipeline for incoming content:
   - ingestion → cleaning → inference → storage
3. Storage design (general):
   - store raw text (if allowed), timestamps, sentiment label, confidence, source metadata
4. Aggregation logic:
   - daily/weekly sentiment trend
   - share of negative sentiment
   - spike detection (sudden increase in negative)
5. Reporting:
   - dashboard (Grafana/Streamlit) or scheduled reports
   - alerts when thresholds exceeded

**Artifacts**
- `docs/architecture.md` (high-level diagram)
- `src/app/` modules: ingestion, inference, storage, analytics

---

## 9) Continuous Monitoring (MLOps layer)
**Outcome**
- A monitoring system that detects degradation and triggers retraining decisions.

**Steps**
1. **Model performance monitoring** (when you have labels):
   - periodic evaluation on a labeled validation stream (or curated samples)
2. **Data drift monitoring** (even without labels):
   - input length distribution
   - vocabulary shift / embedding drift proxy
   - confidence distribution shift
3. **Sentiment monitoring (business KPI)**:
   - rolling average of negative sentiment
   - spike detection
4. Alerting rules:
   - notify when drift exceeds threshold
   - notify when negative sentiment spikes abnormally
5. Feedback loop:
   - incorporate user/analyst corrections as new labeled data

**Artifacts**
- `docs/monitoring_plan.md`
- monitoring dashboards / alert rules (implementation-dependent)

---

## 10) CI/CD Pipeline (Automated Retraining + Testing + Deployment)
**Outcome**
- A pipeline that can retrain the model, run checks, evaluate, and deploy automatically.

### A) CI: every push / PR
**Steps**
1. Lint + format (e.g., ruff/black)
2. Unit tests
3. Lightweight integration test:
   - load dataset
   - run tokenization
   - run a tiny train step (or forward pass)
4. Build artifacts:
   - package / verify scripts runnable

### B) CD: scheduled or trigger-based retraining
**Trigger options**
- schedule (e.g., weekly/monthly)
- manual trigger (workflow_dispatch)
- conditional trigger (only if drift detected / new labeled data available)

**Steps**
1. Fetch latest training data snapshot:
   - base dataset (TweetEval) + optional newly collected labeled samples
2. Train with `Trainer` using saved config
3. Evaluate on test set + compare vs current production metrics
4. Gate deployment:
   - deploy only if metrics improve or do not degrade beyond tolerance
5. Push to Hugging Face Hub:
   - new version tag
   - updated model card with metrics
6. Notify:
   - post summary in GitHub Actions logs
   - optional Slack/Teams/Email notification

**Artifacts**
- `.github/workflows/ci.yml`
- `.github/workflows/retrain_and_deploy.yml`
- evaluation report as pipeline artifact

---

## 11) Delivery Requirements (per project statement)
**Outcome**
- A clean submission path: public repo + Colab notebook referencing it.

**Steps**
1. GitHub repo is public and well documented:
   - install instructions
   - how to train/evaluate/deploy
2. Colab notebook:
   - contains link to GitHub repo
   - shows: dataset load → fine-tune → evaluate → inference example
3. Documentation:
   - design choices (why model, why metrics, why thresholds)
   - results (tables/plots)
   - limitations and future improvements

**Artifacts**
- `notebooks/Project_Delivery.ipynb` (Colab-ready)
- `docs/decisions.md`
- `docs/results.md`

---

# Additions based on the Company Scenario (Reputation Monitoring + MLOps)

The scenario implies extra steps worth explicitly adding to your plan:

## A) Define “Business” KPIs and SLAs (before deployment)
- What is “reputation” operationally?
  - % negative sentiment over time
  - net sentiment score: (pos - neg) / total
  - time-to-detect spikes
- Define alert thresholds and response workflow:
  - when to alert
  - who gets notified
  - how to validate false positives

## B) Data Collection Strategy for “Real” Company Monitoring
Even if training is on TweetEval, production will ingest new data:
- define sources (X/Twitter, Instagram comments, Reddit, reviews, internal tickets)
- define sampling strategy (keywords, brand mentions, competitors)
- define storage retention and privacy rules (PII handling)

## C) Human-in-the-loop Labeling Loop (for meaningful retraining)
To retrain on *company-specific language*:
- create a small annotation workflow:
  - analysts label uncertain or high-impact samples
  - store corrections as a growing dataset
- prioritize samples:
  - low confidence predictions
  - spikes in negative sentiment
  - new slang/product names

## D) Model Governance: Versioning + Rollback
- keep a “production” pointer (latest stable)
- support rollback if the new model underperforms
- log model version used for each prediction (traceability)

## E) Safety / Compliance Considerations (lightweight but necessary)
- document limitations: sarcasm, irony, domain shift
- avoid over-claiming: sentiment ≠ truth
- handle abusive content safely (filter/log policy)

## F) Optional Baseline Comparison (helps your report)
Even if you ship RoBERTa:
- evaluate a simple baseline (e.g., lexicon-based or a smaller model)
- show that fine-tuning provides measurable gain
This strengthens the “choices and results” section in the documentation.

---

## Final Checklist (high-level)
- [ DONE ] Dataset loaded + inspected (TweetEval sentiment)
- [ DONE ] Model loaded + label mapping fixed
- [ ] Trainer fine-tune works end-to-end
- [ ] Metrics reported (accuracy, macro F1, confusion matrix)
- [ ] Error analysis documented
- [ ] Model pushed to HF Hub with model card
- [ ] Inference script + optional Space demo
- [ ] Monitoring plan (drift + KPI + alert rules)
- [ ] CI tests on PRs + scheduled retrain workflow
- [ ] Public GitHub repo + Colab notebook linking repo

---
