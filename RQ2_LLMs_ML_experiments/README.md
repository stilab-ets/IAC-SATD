# RQ2: LLM & Machine Learning Experiments

This directory contains the experimental framework for **Research Question 2 (RQ2)**, which evaluates the performance of Large Language Models (LLMs) and machine learning approaches on multi-label classification of Self-Admitted Technical Debt (SATD) in Infrastructure-as-Code (Terraform).

---

## 📋 Quick Start

**Research Question:** How effectively can LLMs classify IaC SATD instances into multiple debt categories compared to traditional ML baselines?

**Key Experiments:**
- **Zero-shot learning:** LLMs classify without examples
- **Few-shot learning (RAG):** LLMs use retrieved similar examples  
- **ML Baselines:** Binary Relevance with BERT embeddings
- **Statistical comparison:** Rigorous testing with ESD tests

**Evaluation Metric:** Hamming Loss (lower is better)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[ML Baselines](docs/ml_baselines.md)** | Traditional ML approaches (RandomForest, LightGBM + BERT) |
| **[LLM Experiments](docs/llm_experiments.md)** | Zero-shot and few-shot (RAG) LLM experiments |
| **[Statistical Testing](docs/statistical_testing.md)** | ESD tests and performance comparison |
| **[Data Format](docs/data_format.md)** | Input/output CSV specifications |
| **[Troubleshooting](docs/troubleshooting.md)** | Common issues and solutions |

---

## 🎯 SATD Categories

The framework classifies SATD instances into **8 categories** (multi-label):

| Code | Category | Description |
|------|----------|-------------|
| **CAT1** | Computing Components Management Debt | VM, container, serverless, database, storage issues |
| **CAT2** | IaC Code Debt | Code quality, maintainability, bugs |
| **CAT3** | Dependency Management Debt | Terraform/provider version limitations |
| **CAT4** | Security Debt | Weak security configurations |
| **CAT5** | Networking Debt | Routing, VPC, load balancing issues |
| **CAT6** | Environment-Based Configuration Debt | Dev/prod staging, automation pipelines |
| **CAT7** | Monitoring and Logging Debt | Missing/weak monitoring configurations |
| **CAT8** | Test Debt | Lack of testing practices |

---

## 🏗️ Directory Structure

```
RQ2_LLMs_ML_experiments/
├── docs/                                # Documentation
│   ├── ml_baselines.md
│   ├── llm_experiments.md
│   ├── statistical_testing.md
│   ├── data_format.md
│   └── troubleshooting.md
│
├── Data_Splitting/                      # Cross-validation data
│   └── stratified_cleaned_folds/
│
├── ML_baselines/                        # Traditional ML baselines
│   ├── binary_relevance_with_bert.py
│   └── prediction_saver.py
│
├── LLM_predictions/                     # Model outputs
│   ├── llms_predictions_zero_shot/
│   ├── llms_predictions_few_shots/
│   └── ML_predictions/
│
├── LLMs_bootstrap/                      # LLM execution framework
│   ├── core/
│   │   ├── models/                      # LLM wrappers
│   │   ├── retriever/                   # RAG components
│   │   ├── main.py                      # Zero-shot runner
│   │   └── crossval_executor.py         # Cross-validation logic
│   └── prompts/
│       ├── prompt_zero_shot.py
│       └── prompt_few_shots.py
│
└── statistical_testing/                 # Statistical analysis
    ├── ESDTests.py
    ├── apply_tim_testing.py
    └── performance_analysis/
```

---

## ⚡ Quick Run

### ML Baselines
```bash
cd ML_baselines
python binary_relevance_with_bert.py
```

### LLM Zero-Shot
```bash
cd LLMs_bootstrap/core
# Edit main.py to set model and API keys
python main.py
```

### LLM Few-Shot (RAG)
```bash
cd LLMs_bootstrap/core/retriever
# Edit main_RAG.py to set model and retrieval mode
python main_RAG.py
```

### Statistical Testing
```bash
cd statistical_testing
# Edit apply_tim_testing.py to select scenario
python apply_tim_testing.py
```

---

## ⚠️ Important: Import Statements

> [!CAUTION]
> **This project was originally developed in PyCharm, which automatically fixes import paths.** If you're running the code outside PyCharm or from the command line, you may encounter import errors.

**Before Running:**
1. Check import statements in the files you plan to run
2. Fix absolute imports to relative imports if needed
3. Verify PYTHONPATH is set correctly
4. Test with a single fold first

**Files to Check:**
- `LLMs_bootstrap/core/main.py`
- `LLMs_bootstrap/core/retriever/main_RAG.py`
- `ML_baselines/binary_relevance_with_bert.py`

**Alternative:** Use PyCharm and mark `replication_SATD_IaC` as project root.

---

## 📝 Notes

- Temperature sweep: `[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]`
- Multi-label classification: instances can belong to multiple categories
- **Always test with a small subset** before running full cross-validation experiments
- Monitor API costs and rate limits when using commercial LLM APIs
