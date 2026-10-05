# GourmetAI Solution

GourmetAI is a single-notebook computer vision project that classifies food images into 14 categories using transfer learning. Its core exercise isn't just training one model — it's training three different pre-trained backbones under an identical protocol and comparing them head-to-head, so the choice of architecture is backed by evidence rather than habit.

## Project Goal

- Classify a dish photo into one of 14 food categories.
- Compare three transfer-learning backbones — ResNet-50, EfficientNet-B0, and MobileNet V3 Small — under the same training protocol, data, and hyperparameters.
- Pick the best model using validation accuracy only, then report an honest, single-pass test accuracy on the winner.

## Dataset

- Pre-split on disk into `dataset/train/`, `dataset/val/`, `dataset/test/` (ImageFolder-style, one subfolder per class). This folder is gitignored — you need to supply your own 14-class food image dataset with this structure to run the notebook.
- 14 classes, including Donut, Sushi, Fries, Crispy Chicken, Chicken Curry, Taco, Taquito, Hot Dog, Sandwich, Apple Pie, Cheesecake, Ice Cream, and Omelette.
- Images are resized to 256×256 and normalized with ImageNet statistics before being fed to any backbone.

## How It Was Reached

### Transfer learning setup

For each of the three backbones (ImageNet pre-trained):

1. The backbone's convolutional weights are **frozen** (`requires_grad=False`) to preserve the low-level ImageNet features.
2. The original classification head is **replaced** with a custom head: `BatchNorm1d → ReLU → Dropout(0.3) → Linear(14)`.
3. **Only the new head is trained** — this keeps the trainable parameter count tiny regardless of backbone size, which matters both for training speed and for avoiding overfitting on a comparatively small food dataset.

| Backbone | Total Params | Characteristics |
|---|---|---|
| ResNet-50 | ~25M | Residual connections; strong accuracy/speed trade-off |
| EfficientNet-B0 | ~5.3M | Compound scaling; parameter-efficient |
| MobileNet V3 Small | ~2.5M | Built for edge devices; minimal footprint |

### Data augmentation

Training-only augmentations (via `albumentations`): random 90°/180°/270° rotation, horizontal/vertical flip (p=0.6), transpose, and mild affine shear/scale (p=0.6). Validation and test sets only get resize + normalization, so evaluation numbers reflect true generalization rather than augmented difficulty — this is also why validation loss tracks *below* training loss in the curves (harder augmented training samples, not data leakage).

### Training infrastructure

An `Experiment` dataclass bundles a model factory, optimizer, scheduler, and all hyperparameters into one reproducible object per run. Key hyperparameters, identical across all three experiments:

| Hyperparameter | Value |
|---|---|
| Optimizer | Adam |
| Learning rate | `1e-3` |
| Scheduler | `ReduceLROnPlateau` (factor 0.5, patience 3) |
| Batch size | 32 |
| Max epochs | 100 (early stopping usually triggers first) |
| Early stopping patience | 10 epochs on validation loss |
| Dropout | 0.3 |

An `EarlyStopping` callback tracks validation loss and checkpoints the best-performing weights, so the saved model always corresponds to peak validation performance, not the final epoch. Training is also idempotent: reruns reload a completed checkpoint and its `logs.json` instead of retraining from scratch.

### Model selection and final test

The three experiments are trained under identical conditions, then the checkpoint with the highest validation accuracy is selected. The test set is evaluated **exactly once**, on that single winning checkpoint, to get an unbiased estimate of production performance.

## Results

- **Winner: ResNet-50**, trained 52 epochs before early stopping.
- **Test loss:** 0.0174 · **Test accuracy: 81.74%**
- EfficientNet-B0 converged faster per-epoch but landed ~2 points behind (~80% val accuracy) with roughly a fifth of ResNet-50's parameters — a strong efficiency trade-off.
- MobileNet V3 Small converged fastest of all (early-stopped at epoch 29) but plateaued lowest (~76–77% val accuracy) — consistent with its much smaller representational capacity.
- Best per-class accuracy: Donut (93.0%), Crispy Chicken / Fries / Chicken Curry (88.5%), Sushi (86.5%).
- Main confusion pairs: Taco ↔ Taquito (visually near-identical tortilla wraps), and a warm-toned Omelette / Apple Pie / Chicken Curry cluster.
- No class fell below 68% accuracy, and test loss matched the best validation loss — the model is not overfitting.

See the notebook's "Considerations" section for the full error analysis and suggested next steps (progressive backbone unfreezing, class-balanced sampling, higher input resolution).

## Tech Stack

- PyTorch, torchvision — models, transfer learning, training loop
- albumentations — training-time data augmentation
- scikit-learn (`sklearn.metrics`) — confusion matrix and per-class accuracy
- NumPy, Matplotlib, Seaborn — numerics and plotting
- Jupyter Notebook

## Run

From `Projects/GourmetAI_Solution`, with a `dataset/{train,val,test}/<class>/` folder structure in place:

```bash
pip install torch torchvision albumentations numpy matplotlib seaborn scikit-learn jupyter
jupyter notebook
```

Open `GourmetAI.ipynb` and run top to bottom. A "Smoke Test" section runs every model for 2 epochs on a single batch first, to verify the full pipeline (forward/backward pass, checkpointing, reload) before committing to full training runs.

## Compute

The three full training runs (up to 100 epochs each, with early stopping) were done on **Google Colab** with a GPU runtime, not on a local machine — that's also why the trained checkpoints are committed to this repo (see below) rather than gitignored: re-training all three backbones from scratch takes long enough that shipping the weights is more useful to a reader than making them redo it.

To reproduce or extend this on Colab:
1. Upload `GourmetAI.ipynb` to Colab (or open it directly from this repo via `File → Open notebook → GitHub`).
2. `Runtime → Change runtime type → GPU` (a free T4 is enough for this workload — the trainable parameter count is small since only the head is fine-tuned).
3. Upload/mount your `dataset/{train,val,test}/` folder (e.g. via Google Drive) before running the notebook.

Running it locally on CPU also works (the smoke test is designed for exactly this kind of quick sanity check), but full training will be considerably slower.

## Project Structure

```text
GourmetAI_Solution/
├─ README.md
├─ GourmetAI.ipynb
├─ checkpoints/
│  ├─ resnet50/best.pt
│  ├─ efficientnet_b0/best.pt
│  └─ mobilenet_v3_small/best.pt
└─ dataset/            # gitignored — train/val/test split, not included
```
