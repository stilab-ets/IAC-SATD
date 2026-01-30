# Instance Space Analysis (ISA) for IaC SATD Experiments

This repository provides the scripts and metadata required to perform **Instance Space Analysis (ISA)** on Infrastructure-as-Code (IaC) SATD experiments, comparing **LLM performance under zero-shot and few-shot settings**.

The workflow builds on the official ISA implementation by Muñoz et al. and adapts it to the IaC domain.

---

## 1. Prerequisites

### Software Requirements
- **MATLAB** (R2021a or later recommended)
- **Python 3.9+**
- Required Python packages (see your project environment):
  - `pandas`
  - `numpy`

### External Dependency
You must install the official ISA implementation:

👉👉 **Instance Space Analysis repository**  
https://github.com/andremun/InstanceSpace

Follow the installation and setup instructions provided in that repository before proceeding.

---

## 2. Folder Structure

```text
.
├── ISA_application/
│   │
│   ├── evaluation_details_hamming_zero_shot/
│   │  └── metadata.csv
│   │
│   ├── evaluation_details_hamming_few_shots/
│   │  └── metadata.csv
│   │
│   ├── metadata_construction.py
│   │
│   └── trial/
│       └── metadata.csv
├── RQ3.1_results/
│   ├── count_correct_prediction/
│   │   ├── cc_prediction.py
│   │   ├── heatmap_few_shots.pdf
│   │   └── heatmap_zero_shot.pdf
│   │
│   └── footprint_metrics/
│       └── ft_metrics.py
│
├── RQ3.2_results/
│   ├── feature_distribution_in_2D_space_few_shot/
│   │   ├── distribution_feature_*.png
│   │
│   └── feature_distribution_in_2D_space_zero_shot/
│       ├── distribution_feature_*.png
│
├── matrix_representation.py
├── isa_for_iac_satd.m
└── README.md
```

## 3. Running Instance Space Analysis (MATLAB)

### Steps
1. Copy `isa_for_iac_satd.m` into the root of the InstanceSpace repository.
2. Edit the script and set:
```matlab
rootdir = 'ABSOLUTE_PATH_TO_YOUR_METADATA_FOLDER';
```
3. Run in MATLAB:
```matlab
isa_for_iac_satd
```

## Reproducibility Notes
- Figures are generated deterministically.
- Zero-shot and few-shot analyses are fully separated into their specific repositories.
- 
## Reference
- K. Smith-Miles and M.A. Muñoz. Instance Space Analysis for Algorithm Testing: Methodology and Software Tools. ACM Comput. Surv. 55(12:255),1-31 DOI:10.1145/3572895, 2023.
- https://github.com/andremun/InstanceSpace: Functions that run an automated Instance Space analysis.

## 3. RQ3.1 — LLM Correct Prediction Overlap & Footprints

### Correct Prediction Intersection (Heatmaps)

**Folder:**  
`RQ3.1_results/count_correct_prediction/`

**Run:**
```bash
python cc_prediction.py
```

**Description:**
- Computes pairwise intersections of correctly classified instances between LLMs.
- Diagonal values correspond to total correct predictions per model.
- Unique correct predictions (only one model correct) are reported on the diagonal.
- Outputs upper-triangular heatmaps for clarity.

**Outputs:**
- `heatmap_few_shots.pdf`
- `heatmap_zero_shot.pdf`

### Footprint Metrics

**Folder:**  
`RQ3.1_results/footprint_metrics/`

**Run:**
```bash
python ft_metrics.py
```

**Description:**
- Computes footprint-related metrics used in ISA (e.g., coverage, density).
- Enables comparison of LLM behavior across prompting settings.

---

## RQ3.2 — Feature Distribution in the ISA 2D Space

### Few-Shot Setting
**Folder:** `RQ3.2_results/feature_distribution_in_2D_space_few_shot/` contains PNG figures illustrating how instance-level features are distributed across the ISA 2D space.

### Zero-Shot Setting
**Folder:** `RQ3.2_results/feature_distribution_in_2D_space_zero_shot/` contains the same feature distributions for the zero-shot configuration, enabling direct comparison.

### Matrix Representation (ISA Input Preparation)

**Run:**
```bash
python matrix_representation.py
```

**Purpose:**
- Constructs matrix representations required by the ISA pipeline.
- Aligns instance-level features with model performance labels.