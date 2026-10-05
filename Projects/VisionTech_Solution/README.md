# VisionTech Solution

VisionTech is a notebook-based computer vision project that builds a road-safety alert system: a CNN that watches road-camera footage and flags when an **animal** (as opposed to a vehicle) is in frame, so an electronic road sign can warn drivers.

## Project Goal

- Classify road-scene images into two macro-categories: **animal** vs. **vehicle**.
- Optimize for the deployment's actual cost structure: missing an animal (no alert, driver blindsided) is far worse than a false alarm on a vehicle (brief, harmless alert).
- Go beyond aggregate accuracy — understand *where* and *why* the model fails, and pick an operational decision threshold accordingly.

## Dataset

- **CIFAR-10**, loaded via `tensorflow.keras.datasets.cifar10.load_data()` — downloads automatically on first run, no manual data setup needed.
- 10 original classes remapped into 2 macro-classes for this task:
  - **Vehicle**: automobile, truck (2 classes × 5,000 train images = 10,000)
  - **Animal**: bird, cat, deer, dog, frog, horse (6 classes × 5,000 train images = 30,000)
- `airplane` and `ship` are dropped — neither macro-class fits.
- The remap creates a **1:3 vehicle-to-animal class imbalance**, addressed with class weighting during training (vehicle weight = 3.0).

## Approach

**Architecture.** A CNN with three convolutional blocks of increasing depth (32 → 64 → 128 filters). Each block: two `Conv2D` layers (ReLU, `same` padding) → `BatchNormalization` → `MaxPool2D` → `Dropout(0.25)`. The head is a 512-unit `Dense` layer followed by a single sigmoid neuron (binary output, `binary_crossentropy` loss).

**Data augmentation.** `ImageDataGenerator` applies horizontal flips and ±10% width/height shifts at training time only, to reduce overfitting without distorting the validation signal.

**Class imbalance.** Since animals outnumber vehicles 3:1 in the remapped set, the vehicle class is weighted 3.0× in the loss so a vehicle misclassification counts as much as three animal ones.

**Training strategy.**
- Batch size 128 (smaller batches like 32 were tried and produced noisier gradients).
- Learning rate: **Cosine Decay** from `1e-3`, chosen over `ReduceLROnPlateau` because the latter's abrupt LR halving produced visibly segmented learning curves.
- `ModelCheckpoint` saves weights on every `val_accuracy` improvement; `EarlyStopping` (patience=3, `restore_best_weights=True`) stops training on `val_loss` plateau and restores the best epoch — this also protects against Cosine Decay destabilizing updates late in training as the LR approaches 0.

**Evaluation, beyond accuracy.** The notebook deliberately digs past the top-line number:
- Per-class precision/recall/F1 and a confusion matrix, to expose the asymmetry between animal and vehicle errors.
- Reconstructing original CIFAR-10 fine-grained labels for every error, to find which subclasses (e.g. cats, horses) actually drive the animal miss rate.
- A grid of the most confidently wrong predictions, plus a confidence-distribution histogram, to sanity-check model calibration.
- A **threshold sweep** (0.05–0.95) to find the "safety-optimal" decision threshold — the highest threshold that still keeps animal recall ≥ 0.99 — since the default 0.5 threshold is not the right choice for this cost-asymmetric deployment.

## Results

- **95.5% test accuracy**; animal F1 0.97, vehicle F1 0.92.
- Of 357 total errors (4.46%): **336 false negatives** (animals missed) vs. **21 false positives** (vehicles flagged as animals) — a 16:1 FN:FP ratio, the defining operational issue since a missed animal produces no alert at all.
- Class weighting worked as intended on the vehicle side: vehicle recall 0.99, vehicle errors negligible (truck 14, automobile 7).
- Cat (99), horse (76), and bird (60) account for 66% of all animal misses — at 32×32 resolution these subclasses' silhouettes visually overlap with vehicle shapes (e.g. a curled-up cat vs. a car hood).
- Inference: ~0.375 ms/image (~2,600 FPS) on the evaluation run — well within real-time requirements for road-camera deployment.
- Threshold calibration (lowering from 0.5 to the safety-optimal value) raises animal recall above 0.99 while keeping accuracy above 93%, at the cost of more false alarms — an explicit trade-off favored given the asymmetric error cost.

See the notebook's final section for the full discussion, including proposed improvements (targeted augmentation for cats/horses/birds, higher input resolution, transfer learning, and domain adaptation for real road-camera conditions vs. CIFAR-10's clean, centered images).

## Tech Stack

- TensorFlow / Keras (`Sequential`, `Conv2D`, `BatchNormalization`, `Dropout`, `ImageDataGenerator`, `ModelCheckpoint`, `EarlyStopping`, Cosine Decay LR schedule)
- NumPy, Pandas
- scikit-learn (`classification_report`, confusion matrix, metrics)
- Matplotlib

## Running It

```bash
jupyter notebook VisionTech.ipynb
```

CIFAR-10 downloads automatically via Keras on first run — no manual dataset setup required. The trained weights (`cnn.weights.h5`) and pickled model (`cnn.pkl`) are gitignored (`*.h5`, `*.pkl`); re-run the notebook end-to-end to regenerate them.
