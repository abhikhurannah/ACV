# Reproducible pet segmentation experiment

**Abhay Kumar · 23115002 · Advanced Computer Vision**

This project tests whether additive encoder-to-decoder skip fusion improves a small segmentation model under a fixed training budget. Both variants have 24,674 trainable parameters. All reported results are measured locally; no pseudo-labels are used.

## Measured result

| Model | Background IoU | Pet IoU | Mean IoU | Parameters |
|---|---:|---:|---:|---:|
| Baseline | 78.25% | 62.85% | 70.55% | 24,674 |
| Additive skip | 80.04% | 63.48% | 71.76% | 24,674 |

The single-seed change is **+1.21 percentage points mIoU** on the frozen 740-image official-test subset. This is a descriptive comparison, not a significance claim.

## Plan and report

See [PLAN_OF_ACTION.md](PLAN_OF_ACTION.md) for the execution plan. The submission report is `report/23115002.docx` with a PDF copy. It contains the architecture, data contract, figures, actual experiment screenshots, interpretation and limitations.

## Reproduce the experiment

Tested with Python 3.10.16, PyTorch 2.14.1, NumPy 2.2.6 on an Apple M2 CPU, 4 PyTorch threads. `requirements-lock.txt` records every installed package. On another platform, numerical equality and latency are not guaranteed; use the saved checkpoints for direct evaluation.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
python src/download.py
python src/prepare.py
python src/audit_annotations.py
python src/check_contract.py
python -u src/train.py --variant baseline > artifacts/baseline_train.log 2>&1
python -u src/train.py --variant skip > artifacts/skip_train.log 2>&1
python src/evaluate.py
python src/figures.py
python src/build_evidence.py
```

The data download is about 810 MB. The source mirror is pinned to revision `089695c834a7deb60505b7cc506672db1c31a6aa`. Archive SHA256 values are in `artifacts/archive_hashes.json`. The downloader verifies these when the manifest is present. Training is CPU-only; each variant receives 1,860 Adam updates in 20 epochs. The last batch has 8 images. The best checkpoint is chosen by validation global mIoU; test data are loaded only in evaluation. Do not change the budget after inspecting test results.

## Data contract

Oxford-IIIT Pet official `trainval.txt` and `test.txt` define the source pools. Within each of the 37 breeds, a seeded shuffle selects 40 training and 10 validation images from trainval, then 20 test images from official test. Counts: 1,480 / 370 / 740. Remaining official examples are unused. This is a declared subset experiment, not a full benchmark score. `artifacts/splits.json` is the authoritative manifest. `src/prepare.py` joins mirror RGB images to official trimaps by image ID and saves per-file hashes.

Original mask 1 (pet) maps to target 1; original mask 2 (background) maps to target 0; original mask 3 (uncertain boundary) maps to ignored target 255. Cross entropy and evaluation exclude 255. RGB is converted to three channels, resized directly to 96×96 with bilinear interpolation, then divided by 255. Masks use nearest-neighbour resizing. No ImageNet normalization, pretraining or aspect-preserving crop is used. Only the training split receives a jointly applied horizontal flip with probability 0.5. Breed IDs define balancing, not segmentation output classes.

## Controlled architecture

The encoder has two convolution blocks at widths 8 and 16, and a width-32 bottleneck after two max pools. Bilinear upsampling and 1×1 projections restore decoder widths 16 and 8. Every block has two 3×3 convolutions with padding 1, biases and ReLU. A 1×1 head produces two logits. There is no batch normalization or dropout.

The baseline passes projected decoder tensors directly into the decoder blocks. The skip variant adds the corresponding encoder tensor before each decoder block. All parameter shapes are identical, allowing the same initialization seed to yield identical initial weights. Separate generators fix sample order and paired augmentation draws. Only skip routing changes.

## Evaluation and latency

`src/evaluate.py` loads each selected checkpoint, predicts every test image without augmentation and sums a 2×2 confusion matrix over all valid pixels. Rows are truth and columns prediction, ordered background then pet. IoU(c) = TP(c) / (TP(c) + FP(c) + FN(c)); mIoU is the arithmetic mean of both class IoUs. The global score is not the mean of individual-image IoUs. For image-level diagnosis only, a class with zero union has undefined IoU and is omitted from that image mean; both classes have positive union globally. `artifacts/per_image.csv` is provided only for case selection and inspection.

Latency uses float32 CPU inference with four threads, batch 1, an already resident 1×3×96×96 tensor, 30 warmups and 200 timed forwards. `time.perf_counter_ns` measures each iteration. No decoding, resizing, copies, argmax or metric calculation is timed. Median, mean, p95 and all raw samples are saved. Wall-clock training time is measured separately. Background activity and thermal state were not controlled.

## Evidence and files

- `artifacts/results.json`: test IoUs, confusion matrices, checkpoints and raw latency samples.
- `artifacts/*_history.json` and `*_train.log`: every epoch and validation score.
- `artifacts/*.pt`: selected state dictionaries and checkpoint metadata (included in the repository and submission archive).
- `artifacts/data_manifest.json`: exact IDs, split labels, and image/mask SHA256 values.
- `artifacts/environment.json`, `hardware.json`, and `requirements-lock.txt`: execution conditions.
- `artifacts/figures/`: measured curves, metrics, architecture and test examples.
- `artifacts/screenshots/`: genuine browser captures of generated evidence pages.
- `src/check_contract.py`: split, mask, parameter-shape and hand-calculated metric checks.

`src/build_evidence.py` builds a static HTML evidence dashboard directly from saved logs and results. Screenshots show this dashboard and are labelled as browser evidence views, not terminal captures. `src/capture_evidence.cjs` uses Playwright with Google Chrome to reproduce screenshots; install Playwright separately if needed. Screenshot creation and report authoring are separate from model reproduction.

## Annotation audit

The selected original masks for `Egyptian_Mau_165` and `miniature_pinscher_14` (training), and `keeshond_7` and `Persian_259` (test), contain only background. They were retained in the frozen dataset. `artifacts/annotation_audit.json` records the exact raw pixel counts; the protocol does not silently filter examples after seeing results. This annotation limitation affects what the measured scores establish.

## Scope and limitations

One seed and a small subset at 96×96 cannot establish statistical significance, state of the art accuracy, robustness across datasets or devices, or full-resolution boundary quality. Ignoring the uncertain human boundary makes the measured task easier near edges. The model is not an exact reproduction of the original U-Net, and this additive skip test does not evaluate concatenation, dilation, global pooling, or a boundary branch. Equal parameters and updates do not imply exactly equal compute. No model selection or tuning uses the test split.

## Attribution

Dataset: Parkhi, Vedaldi, Zisserman and Jawahar, *Cats and Dogs*, CVPR 2012. Official data and license: https://www.robots.ox.ac.uk/~vgg/data/pets/ . The official page specifies CC BY-SA 4.0; source image copyright remains with the original owners. Example images and masks in this submission are attributed to that dataset; see `DATA_ATTRIBUTION.md`.

Architecture background: Ronneberger, Fischer and Brox, *U-Net: Convolutional Networks for Biomedical Image Segmentation*, 2015, https://arxiv.org/abs/1505.04597 . The implementation here is a deliberately smaller additive-fusion experiment.

Mirror: https://huggingface.co/datasets/timm/oxford-iiit-pet . Reproducibility background: https://docs.pytorch.org/docs/2.14/notes/randomness.html .
