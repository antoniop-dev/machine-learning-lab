# BancaVirtuosa Solution

BancaVirtuosa is a compliance-oriented explainability case study: a bank deploying models in processes subject to supervisory review needs to answer *"why was this specific case classified this way?"* with evidence pointed at the input, not just an accuracy score. The project builds that answer trail end to end on a controlled task — handwritten digit classification (MNIST) with a transfer-learned DenseNet-121 — then explains the model's decisions with five independent attribution techniques and compares what they agree and disagree on.

## Project Goal

- Train an auditable image classifier and evaluate it honestly (accuracy, per-class precision/recall, confusion structure).
- Explain individual predictions — both correct and incorrect — with five different post-hoc attribution techniques: **Grad-CAM, Integrated Gradients, Occlusion, LIME, and SHAP**.
- Compare the five techniques against each other on the *same* fixed set of cases, to see where they agree, where they diverge, and what that says about trusting any single one.
- Diagnose *why* the model makes its specific errors, using the attribution maps as evidence.
- Weigh this post-hoc explainability approach against explainable-by-design alternatives (decision trees, EBMs, NAMs, ProtoPNet) for a compliance-grade use case.

## Approach

### 1. Model

A `densenet121` backbone pre-trained on ImageNet, frozen, with its 1000-class head replaced by a 10-class linear layer trained on MNIST. Because the backbone is frozen, each image only needs to pass through it once: embeddings are cached to disk (`outputs/cache/`) and the linear head is trained on the cached 1024-d vectors instead of re-running the backbone every epoch. Images are resized from MNIST's native 28×28 grayscale to 3×224×224 and normalized with **ImageNet statistics** (not MNIST's own) — a deliberate choice, since the frozen convolutions were calibrated on that distribution.

Result: **97.26% test accuracy** on the 10,000-image MNIST test set, with per-class F1 ranging from 0.936 (digit 5) to 0.990 (digit 1).

### 2. Fixed, seeded case set

Rather than explaining random predictions, every technique runs on the same **40 fixed cases**, selected once and reused throughout:

- **30 correct cases** — 3 per digit class, class-balanced by construction.
- **10 incorrect cases** — drawn from the model's **most frequent confusion pairs** (5→3, 2→5, 3→5, 2→7, 7→1), rather than random errors, so the analysis targets systematic weaknesses instead of one-off oddities.

Every random step (splitting, sampling, LIME/SHAP's internal sampling) is seeded, so the notebook is fully reproducible and re-running it only redraws figures from cached attribution arrays instead of recomputing them.

### 3. Five attribution techniques

| Technique | What it does | Library |
|---|---|---|
| **Grad-CAM** | Gradient-weighted class activation on the last dense block, upsampled to input resolution. Positive-only by construction. | `captum` |
| **Integrated Gradients** | Attributes along the straight path from a black baseline to the input image. | `captum` |
| **Occlusion** | Slides an occluding window over the image and measures the logit change — also run twice per error (once for the predicted class, once for the true class) to isolate exactly what tipped the decision. | `captum` |
| **LIME** | Fits a local linear surrogate over image superpixels. | `lime` |
| **SHAP** | Game-theoretic attribution using a background sample. | `shap` |

Each map is visualized on its own scale (the five techniques produce incompatible units — activations, logit deltas, regression weights — so a shared scale would blank out the smaller ones); the question the visual comparison answers is *where* the evidence sits, not how large it is.

### 4. Diagnosing the errors

Running Occlusion twice per misclassified case (predicted class vs. true class) isolates the exact region that tipped each decision. The five confusion pairs studied all share the same failure pattern: **the evidence for the wrong class sits on the stroke the two digits share, and the stroke that should distinguish them is missing, malformed, or outvoted** — e.g., in 7→1 errors, the model ignores the (faint or absent) crossing bar that should separate a 7 from a 1. The diagnosis: a frozen ImageNet backbone only has features built for natural-image texture, not stroke topology — fine-tuning the last dense block, rather than freezing it, is the fix this analysis points to.

### 5. Explainable-by-design alternative

The notebook closes by weighing post-hoc explanation against building an inherently interpretable model instead — shallow decision trees, Explainable Boosting Machines, Neural Additive Models, and prototype-based networks (ProtoPNet) — concluding that for a compliance-grade classifier like this one, an EBM is the closest fit: an additive, feature-by-feature breakdown an auditor could re-derive by hand, without giving up as much accuracy as a single decision tree would.

## Tech Stack

- **Modeling**: PyTorch, torchvision (`densenet121`, `DenseNet121_Weights`, MNIST dataset loader)
- **Explainability**: Captum (Grad-CAM, Integrated Gradients, Occlusion), LIME, SHAP
- **Data/metrics**: scikit-learn (`train_test_split`, `confusion_matrix`, `classification_report`), pandas, NumPy
- **Visualization**: Matplotlib (custom single-hue colormaps for magnitude encodings)
- **Environment**: developed locally on Apple Silicon (MPS), executed in full on Google Colab (CUDA); pinned dependency versions (`captum==0.9.0`, `lime==0.2.0.1`, `shap==0.51.0`) since attribution maps are only reproducible against the library version that produced them

## Dataset

MNIST (60,000 train / 10,000 test, 28×28 grayscale digits), downloaded automatically via `torchvision.datasets.MNIST` on first run — no manual download needed. `data/` and `outputs/` are gitignored; running the notebook end to end regenerates both from scratch (cached embeddings, model checkpoint, attribution arrays, and figures).

## Run

From `Projects/BancaVirtuosa_Solution`:

```bash
jupyter notebook
```

Open `BancaVirtuosa.ipynb`. The notebook defines two configs — `PROTOTYPE_CONFIG` (a small class-balanced subset, for iterating locally) and `FULL_CONFIG` (the full MNIST dataset, used for the run this README describes); switching between them is a one-line change. On Colab, the notebook mounts Google Drive and installs the missing XAI packages automatically.

## Project Structure

```text
BancaVirtuosa_Solution/
├─ README.md
├─ BancaVirtuosa.ipynb
├─ data/                       # MNIST download (gitignored)
└─ outputs/                    # gitignored, regenerated on each full run
   ├─ cache/                   # frozen-backbone embeddings
   ├─ checkpoints/             # model_best.pt
   ├─ figures/                 # report-ready figures
   ├─ attributions/            # cached raw attribution arrays
   ├─ config.json              # the config that produced everything below
   ├─ splits.json              # train/val/test index arrays
   └─ selected_samples.json    # the fixed 40-case XAI case set
```
