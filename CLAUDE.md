# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Coding Guidelines

When generating new code or modifying existing code you should follow this guidelines:
- Single Responsibility Principle: each function and/or method should have one and only one job, it should have a clear name to give an idea of what it is doing.
- Documentation: each function and/or method should be documented with doc strings (and comments when needed), always remeber to update the docs when you update code.
- Type Hinting: type hinting for the functions and/or methods parameters is mandatory. Not every variable in your code must be type hinted, but the parameters are a must.
- Reduce, Reuse, Recycle: before starting an implementation you should check if there are any portion of code you can reuse for your task, avoiding boilerplates and code duplication.

## Repository Overview

A learning lab for AI/ML exercises and project solutions, organized as a beginner-to-advanced curriculum. Content is organized into:
- `Exercises/`: topic-by-topic notebooks, ordered as a learning path from ML fundamentals through deep learning, RL, generative AI, and XAI. See `Exercises/README.md` for the recommended order and how each track links to a `Projects/` solution.
- `Projects/`: solution folders for business-style ML problems. Most mirror the skills built in one `Exercises/` track (see `Exercises/README.md` for the mapping); two (`InsuraPro_Solution`, `ContactEase_Solution`) are general software-engineering exercises unrelated to ML.

Each project folder has its own `README.md` with setup, run commands, and test instructions — check there first before re-deriving commands. Full project catalog, topics, and stack are documented in the root `README.md`.

Data files, model artifacts (`.h5`, `.pkl`, `.pt`, etc.), and most generated outputs are gitignored.

---

## Running Exercises

All notebook-based exercises run via Jupyter:

```bash
jupyter notebook
```

Exception — `Exercises/MLOps&ML_in_prod/Model_Testing/` is a FastAPI + pytest exercise, not a notebook. It exposes a `/training` POST endpoint that fits a `LinearRegression` and returns MSE; tests use `fastapi.testclient.TestClient`.

```bash
cd "Exercises/MLOps&ML_in_prod/Model_Testing"
pytest tests/test_app_training.py -v
```

## Running Projects

Run each project's commands from inside that project's own folder, following its `README.md`. `MachineInnovatorsInc_Solution` is the exception worth knowing up front: it's the only Dockerized, full-stack project with a pipeline of CLI scripts, a FastAPI+React app, and GitHub Actions CI/CD (workflows in repo-root `.github/workflows/`, scoped to `Projects/MachineInnovatorsInc_Solution/**`) — see its README for the pipeline scripts, Docker Compose stack, and CI details.
