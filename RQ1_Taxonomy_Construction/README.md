# RQ1: Taxonomy Construction

This directory contains the complete workflow for **Research Question 1 (RQ1)**: Developing and validating a hierarchical taxonomy of Self-Admitted Technical Debt (SATD) in Infrastructure-as-Code (Terraform).

## Overview

RQ1 addresses: **"What types of technical debt exist in Infrastructure-as-Code?"**

The workflow consists of two main phases:
1. **SATD Collection**: Automated extraction from Terraform repositories
2. **Data Annotation**: Manual annotation and taxonomy validation

## Directory Structure

```
RQ1_Taxonomy_Construction/
├── SATD_collector/              # Automated SATD extraction tool
│   ├── CommentsMining/          # Comment extraction and detection
│   ├── Model/                   # Data models
│   ├── SatdTracking/            # Lifecycle tracking
│   ├── DataManagment/           # CSV export
│   ├── diagrams/                # Architecture diagrams
│   ├── main.py                  # Entry point
│   └── README.md                # Detailed documentation
│
└── data_annotation/             # Annotation and taxonomy validation
    ├── ground_truth/            # Ground truth labels
    ├── annotator_agreements/    # Final annotated data
    ├── *.py                     # Analysis scripts
    └── README.md                # Detailed documentation
```

## Workflow

### Phase 1: SATD Collection

**Tool**: `SATD_collector/`

**Process**:
1. Mine Terraform repositories from GitHub
2. Extract comments from `.tf` files
3. Detect SATD using keyword or ML-based methods
4. Track SATD lifecycle across commits
5. Export structured data

**Output**: `collected_SATD_from_all_projects.csv` (1,394 instances)

📖 **[SATD Collector Documentation →](SATD_collector/README.md)**

### Phase 2: Data Annotation

**Tool**: `data_annotation/`

**Process**:
1. Filter and prepare annotation dataset (725 instances)
2. Two independent annotators classify instances
3. Apply hierarchical taxonomy (8 categories → 25 themes)
4. Validate inter-annotator agreement (Cohen's Kappa)
5. Analyze taxonomy consistency

**Output**: Validated taxonomy with substantial agreement (κ = 0.69)

📖 **[Data Annotation Documentation →](data_annotation/README.md)**

## Hierarchical Taxonomy

### Higher-Level Categories (8)
1. Computing Management Debt
2. IaC Code Debt
3. Dependency Management
4. Security Debt
5. Networking Debt
6. Environment-Based Configuration Debt
7. Monitoring and Logging Debt
8. Test Debt

### Fine-Grained Themes (25)
Each category contains 2-5 specific sub-themes representing concrete technical debt patterns.

## Key Results

| Metric | Value              |
|--------|--------------------|
| **SATD Instances Collected** | 1,394              |
| **Annotated Instances** | 725                |
| **Higher-Level Categories** | 8                  |
| **Fine-Grained Themes** | 25                 |
| **Inter-Annotator Kappa** | 0.68 (Substantial) |
| **Average Themes per Instance** | 2.24               |

## Data Flow

```
GitHub Terraform Repos
        ↓
SATD_collector (automated extraction)
        ↓
collected_SATD_from_all_projects.csv (1,394 instances)
        ↓
data_annotation (filtering + annotation)
        ↓
filtered_dataset_for_annotation.csv (725 instances)
        ↓
Two Independent Annotators
        ↓
Check false positive instances (680 valide SATD instances)
        ↓
Validated Taxonomy (8 categories, 25 themes)
        ↓
RQ2 (ML/LLM Classification)
```

## Quick Start

### 1. Collect SATD from Repositories

```bash
cd SATD_collector
python main.py --repo_url https://github.com/user/terraform-repo --detect_type 1
```

### 2. Analyze Annotations

```bash
cd data_annotation

# Calculate inter-annotator agreement
python calculate_median_kappa.py

# Count theme distribution
python count_ground_truth_themes.py

# Analyze category vs theme agreement
python analyze_category_theme_agreement.py
```

## Architecture Diagrams

The `SATD_collector/diagrams/` folder contains:
- **Activity Diagrams**: Detection and tracking workflows
- **Class Diagrams**: System architecture
- **Sequence Diagrams**: Component interactions

## Requirements

See individual README files for specific requirements:
- **SATD_collector**: PyDriller, pandas, scikit-learn
- **data_annotation**: pandas, numpy, scikit-learn, matplotlib

## Integration with Other RQs

- **RQ2**: Uses the annotated dataset for ML/LLM training and evaluation
- **RQ3**: Applies taxonomy for generalizability analysis

## Documentation

Each subfolder contains detailed documentation:

- 📖 **[SATD Collector](SATD_collector/README.md)** - Automated extraction tool, detection methods, lifecycle tracking
- 📖 **[Data Annotation](data_annotation/README.md)** - Annotation workflow, analysis scripts, validation results

## Contact

For questions about the taxonomy or annotation process, please contact [your contact information].
