# GreenTech Solution

GreenTech is a single-notebook computer vision project that classifies field images of plants as **daisy** or **dandelion**, using transfer learning on a pre-trained ResNet50. It compares two fine-tuning strategies head-to-head and picks a winner using a disciplined, leakage-free evaluation process.

## Project Goal

- Build a binary image classifier that distinguishes daisy from dandelion plants in field photography, for agritech use cases like precision herbicide spraying and automated crop monitoring.
- Compare two transfer-learning strategies on the same backbone: a **frozen ResNet50** (train only a custom head) vs. **partial fine-tuning** (also unfreeze the last residual block, `layer4`, with a differential learning rate).
- Select the better strategy using validation macro-F1 (robust to class imbalance) and report an honest, single-pass test-set score.

## Dataset

- Expected layout (not included in the repo — `Projects/GreenTech_Solution/dataset/` is gitignored):
  ```text
  dataset/
  ├─ train/{daisy,dandelion}/
  ├─ valid/{daisy,dandelion}/
  └─ test/{daisy,dandelion}/
  ```
- Loaded via `torchvision.datasets.ImageFolder`, so any dataset following this two-class folder structure works — the notebook targets a public daisy/dandelion flower dataset.
- Binary target, single-logit output (`BCEWithLogitsLoss`), decision boundary at 0 (≈ sigmoid threshold 0.5).

## Approach

**Preprocessing & augmentation.** Validation/test images are resized to 256×256 and normalized with ImageNet statistics, matching what the pre-trained backbone expects. Training images additionally go through an `albumentations` pipeline designed around real field-photography variability rather than generic defaults:

| Transform | Parameters | Models |
|---|---|---|
| `RandomResizedCrop` | scale `(0.89, 1.0)`, 256×256 | Camera-to-plant distance variation |
| `Rotate` | limit 7° | Imperfectly levelled camera/drone capture |
| `RandomBrightnessContrast` | brightness limit 0.08 | Cloud cover / time-of-day lighting |
| `RandomGamma` | gamma `(94, 106)` | Sensor response differences across cameras |
| `CoarseDropout` | 4 holes, 23×23 px | Partial occlusion by soil, other plants, debris |

A `Transforms` wrapper adapts the `albumentations` pipeline to `torchvision`'s callable-transform API, so `ImageFolder` can be reused unchanged.

**Architecture.** A pre-trained ResNet50 (`timm.create_model`) has its classifier replaced with a custom head: `BatchNorm1d → ReLU → Dropout → Linear(1)`. Backbone choice and which layers to unfreeze are both function arguments (`make_resnet_timm`), so swapping to ResNet18/34/101 or another `timm` backbone needs no code changes.

**Two experiments, same infrastructure.** Both runs share a reusable training stack: an `Experiment` dataclass holding model, optimizer, scheduler, loss, and running metrics; `EarlyStopping` (tracks validation loss, restores the best checkpoint); and `train_epoch`/`test_epoch`/`train` loops. Checkpointing makes the notebook idempotent — finished experiments are loaded from disk (`best.pt`, `logs.json`) instead of retrained on re-run. A smoke test (2 epochs on one mini-batch) validates the whole pipeline — shapes, loss dtype, checkpointing, early stopping, reload-from-disk — before committing to full training.

1. **Experiment 1 — frozen backbone (baseline).** Only the head is trained. Adam (`lr=1e-3`), `ReduceLROnPlateau` (factor 0.5, patience 3), early stopping (patience 10), max 100 epochs.
2. **Experiment 2 — partial fine-tuning.** `layer4` is unfrozen alongside the head, trained with differential learning rates: head at `1e-3`, `layer4` at `1e-5` (100× smaller, to adapt high-level features to daisy/dandelion without forgetting ImageNet representations).

**Model selection.** The winner is chosen by validation macro-F1 (not raw accuracy, to stay robust to class imbalance). The test set is evaluated exactly once, only after that decision is final, to avoid leaking test information into model choice.

## Results

- Partial fine-tuning (unfreezing `layer4`) beat the frozen baseline by **+0.55 pp accuracy and +3 pp macro-F1**, converging in ~35–38 epochs.
- Final test-set performance (best model): **97.8% accuracy, 97.8% macro-F1**.
- Interpretation: early ResNet layers transfer well as generic texture/edge detectors, but `layer4` encodes higher-level, more ImageNet-specific part/shape features — letting it adapt (at a much lower LR than the head) captures daisy/dandelion-specific visual structure (petal arrangement, stem texture, seed-head geometry) without catastrophic forgetting.

## Tech Stack

- PyTorch, `torchvision` (`ImageFolder`, `DataLoader`)
- `timm` (pre-trained ResNet50 backbone)
- `albumentations` (augmentation pipeline)
- `scikit-learn` (`confusion_matrix`, `f1_score`, `classification_report`)
- NumPy, Matplotlib, Seaborn

## Run

From `Projects/GreenTech_Solution/`, with the dataset placed under `dataset/` as described above:

```bash
jupyter notebook
```

Open `GreenTech.ipynb` and run top to bottom. Batch size is 32; both experiments checkpoint to `checkpoints/<experiment_name>/` (gitignored) and will skip retraining if a completed run is already on disk.

## Compute

Both experiments (up to 100 epochs each, with early stopping) were trained on **Google Colab** with a GPU runtime rather than locally. Only the head (and, in Experiment 2, `layer4`) is trainable, so a free-tier Colab GPU (T4) is enough — you don't need a paid tier or a personal GPU machine to reproduce this.

To run it on Colab: upload `GreenTech.ipynb` (or open it via `File → Open notebook → GitHub`), set `Runtime → Change runtime type → GPU`, then upload/mount your `dataset/` folder before running. It also runs on CPU (the smoke-test cell exists precisely to validate the pipeline cheaply before a full run), just much slower.

## Known Limitations

- **Domain shift**: training images may not cover the full range of field conditions (season, lighting, soil, camera model) a deployed model would see.
- **Binary scope**: any plant that isn't a daisy or dandelion is force-classified as one of the two — there's no out-of-distribution rejection.
- **Small, clean dataset**: high accuracy here doesn't guarantee equivalent robustness on noisier, real-world field imagery.
