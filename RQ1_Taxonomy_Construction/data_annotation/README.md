# RQ1 Taxonomy Construction - Data Annotation

This directory contains the complete workflow for annotating and analyzing Self-Admitted Technical Debt (SATD) in Infrastructure-as-Code (IaC) projects, specifically for constructing and validating a hierarchical taxonomy of IaC technical debt.

## Overview

The annotation process involves:
1. **Data Collection**: SATD comments extracted from IaC repositories
2. **Annotation**: Two independent annotators classify instances using a hierarchical taxonomy
3. **Validation**: Inter-annotator agreement analysis using Cohen's Kappa

## Directory Structure

```
data_annotation/
├── ground_truth/              # Ground truth dataset with original labels
├── annotator_agreements/      # Annotator files with complete taxonomy
├── *.py                       # Analysis and processing scripts
└── *.csv                      # Dataset files
```

## Key Datasets

### Input Files
- `collected_SATD_from_all_projects.csv` - Raw SATD data (1,394 instances)
- `filtered_dataset_for_annotation.csv` - Filtered dataset for annotation (725 instances)
- `reduced_dataset_from_duplication.csv` - Deduplicated dataset (822 instances)

### Annotator Files
- `annotator_agreements/annotator_1.csv` - Annotator 1 with complete taxonomy (725 instances)
- `annotator_agreements/annotator_2.csv` - Annotator 2 with complete taxonomy (725 instances)

### ConstructedGround Truth
- `ground_truth/ground_truth.csv` - Ground truth with low-level labels (680 instances)

## Hierarchical Taxonomy

### Higher-Level Categories (8 categories)
1. Computing Management Debt
2. IaC Code Debt
3. Dependency Management
4. Security Debt
5. Networking Debt
6. Environment-Based Configuration Debt
7. Monitoring and Logging Debt
8. Test Debt

### Fine-Grained Themes (25 sub-categories)
Each category contains 2-5 specific theme sub-categories. See `count_ground_truth_themes.py` for complete distribution.

## Analysis Scripts

### Inter-Annotator Agreement
- `calculate_median_kappa.py`
  - Mean Kappa: 0.6795 (Substantial agreement)
  - Median Kappa: 0.6960

### Theme Analysis
- `count_ground_truth_themes.py` 
  - 25 unique themes across 680 instances
  - Average 2.24 themes per instance
  - Normalized by instance count


## Key Results

### Inter-Annotator Reliability

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Mean Cohen's Kappa** | 0.6795 | Substantial agreement |
| **Median Cohen's Kappa** | 0.6960 | Substantial agreement |

### Theme Distribution (Top 5)

| Theme | Count | % of Instances |
|-------|-------|----------------|
| Insufficient Attribute Specification | 178 | 26.2% |
| Improper Implementation Patterns | 173 | 25.4% |
| Misconfigured Identity & Access Management | 150 | 22.1% |
| Deferred Orchestration Features | 110 | 16.2% |
| Feature to be implemented in the future | 103 | 15.1% |

### Agreement by Category

| Category | Kappa | Interpretation |
|----------|-------|----------------|
| Computing Management Debt | 0.7381 | Substantial |
| IaC code debt | 0.7187 | Substantial |
| Security debt | 0.6990 | Substantial |
| Dependency management | 0.6520 | Substantial |

## Usage

### Running Analysis Scripts

```bash
# Activate virtual environment
# (automatically activated if using venv)

# Calculate inter-annotator agreement
python calculate_median_kappa.py

# Count theme distribution
python count_ground_truth_themes.py


```

## Methodology

### 1. Data Collection
- SATD comments extracted from IaC repositories
- Filtered and deduplicated instances
- Annotation dataset: 725 instances

### 2. Annotation Process
- Two independent annotators classified instances
- Hierarchical taxonomy: 8 categories → 25 themes
- Categories marked as binary (0/1)
- Themes listed in Theme 1-12 columns

### 3. Validation
- Cohen's Kappa for inter-annotator agreement
- Category-level and theme-level analysis

## Requirements

See `requirements.txt` for complete dependencies. Key packages:
- pandas (data manipulation)
- numpy (numerical operations)
- scikit-learn (Cohen's Kappa calculation)




