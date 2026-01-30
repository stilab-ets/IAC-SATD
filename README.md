# Replication Study: Understanding Self-Admitted Technical Debt in Infrastructure-as-Code


This repository contains the complete replication package for our study on Self-Admitted Technical Debt (SATD) in Infrastructure-as-Code (IaC) projects, with a focus on Terraform configurations.

## Repository Structure

```
replication_SATD_IaC/
├── RQ1_Taxonomy_Construction/     # Taxonomy development and annotation
│   └── data_annotation/           # See detailed README in this folder
├── RQ2_LLMs_ML_experiments/       # Machine learning experiments
├── RQ3_LLMs_generalizability/     # Generalizability analysis
├── SATD_collection_in_TF_projects/ # Data collection scripts
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Research Questions

### RQ1: Taxonomy Construction

**Goal**: Develop a hierarchical taxonomy of technical debt in IaC

**Location**: `RQ1_Taxonomy_Construction/`

**Components**:
- **SATD Collector**: Automated extraction from Terraform repositories (1,394 instances)
- **Data Annotation**: Manual annotation and validation (725 instances)

**Key Results**:
- 8 higher-level debt categories
- 25 fine-grained theme sub-categories
- Inter-annotator Cohen's Kappa: 0.68 (Substantial agreement)

📖 **[RQ1 Overview →](RQ1_Taxonomy_Construction/README.md)**
- 📖 [SATD Collector Documentation](RQ1_Taxonomy_Construction/SATD_collector/README.md)
- 📖 [Data Annotation Documentation](RQ1_Taxonomy_Construction/data_annotation/README.md)

### RQ2: ML/LLM Experiments

**Goal**: Evaluate machine learning and large language models for SATD classification

**Location**: `RQ2_LLMs_ML_experiments/`

**Key Approaches**:
- Zero-shot and Few-shot LLM classification
- Traditional ML baselines (Binary Relevance + BERT)
- Statistical testing with ESD tests
- Multi-label classification across 8 debt categories

**Evaluation Metric**: Hamming Loss (lower is better)

📖 **[Detailed Documentation →](RQ2_LLMs_ML_experiments/README.md)**

### RQ3: Generalizability

**Goal**: Assess model performance across different IaC projects using Instance Space Analysis

**Location**: `RQ3_LLMs_generalizability/`

**Key Analyses**:
- Instance Space Analysis (ISA) for algorithm testing
- LLM performance comparison (zero-shot vs few-shot)
- Footprint metrics and feature distribution
- Cross-project validation

📖 **[Detailed Documentation →](RQ3_LLMs_generalizability/README.md)**

### SATD Collection

**Goal**: Collect and preprocess SATD comments from Terraform projects

**Location**: `SATD_collection_in_TF_projects/`

**Output**: 1,394 SATD instances from GitHub Terraform projects

📖 **[Documentation →](SATD_collection_in_TF_projects/README.md)**

## Getting Started

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd replication_SATD_IaC

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

Each research question folder contains its own scripts and documentation. Start with:

1. **RQ1**: See `RQ1_Taxonomy_Construction/data_annotation/README.md` for annotation analysis
2. **RQ2**: Navigate to `RQ2_LLMs_ML_experiments/` for ML experiments
3. **RQ3**: Navigate to `RQ3_LLMs_generalizability/` for generalizability tests

## Dataset

### SATD Collection
- **Source**: Terraform projects from GitHub
- **Total instances**: 1,394 SATD comments
- **Annotated subset**: 725 instances
- **Ground truth**: 680 instances with detailed labels

### Data Location
- Raw data: `SATD_collection_in_TF_projects/`
- Annotated data: `RQ1_Taxonomy_Construction/data_annotation/`

## Key Technologies

- **IaC Platform**: Terraform
- **Languages**: Python, HCL (Terraform)
- **ML Frameworks**: scikit-learn
- **LLMs**: Various (see RQ2 documentation)
- **Analysis**: pandas, numpy, matplotlib

---

## Folder Documentation

Each major folder contains its own detailed README with specific instructions and documentation:

- 📖 **[RQ1: Data Annotation](RQ1_Taxonomy_Construction/data_annotation/README.md)** - Complete annotation workflow, analysis scripts, and taxonomy validation
- 📖 **[RQ2: ML/LLM Experiments](RQ2_LLMs_ML_experiments/README.md)** - Zero-shot/few-shot LLM experiments, ML baselines, and statistical testing
- 📖 **[RQ3: Generalizability Analysis](RQ3_LLMs_generalizability/README.md)** - Instance Space Analysis and cross-project validation
- 📖 **[SATD Collection](SATD_collection_in_TF_projects/README.md)** - Data collection methodology and preprocessing
