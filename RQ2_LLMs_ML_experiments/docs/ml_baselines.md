# ML Baselines

Traditional machine learning baselines using **Binary Relevance** with **BERT embeddings** for multi-label SATD classification.

---

## Overview

**Approach:**
- **Text Encoding:** BERT-base-uncased (110M parameters)
- **Multi-label Strategy:** Binary Relevance (8 independent binary classifiers)
- **Classifiers:** RandomForest and LightGBM with GridSearch hyperparameter tuning

**Purpose:** Serve as comparison benchmarks for LLM performance

---

## Architecture

```
Input: SATD Comment + Context + Code Block
    ↓
Concatenate with [SEP] tokens
    ↓
BERT Tokenization (max 512 tokens)
    ↓
BERT Encoding (bert-base-uncased)
    ↓
Mean Pooling → 768-dim embeddings
    ↓
Binary Relevance Wrapper
    ↓
8 Independent Binary Classifiers
    ↓
Multi-label Predictions (8 binary outputs)
```

---

## Supported Models

| Model | Description | Key Hyperparameters |
|-------|-------------|---------------------|
| **RandomForest (RF)** | Ensemble of decision trees | n_estimators, max_depth, criterion |
| **LightGBM** | Gradient boosting | num_leaves, max_depth, subsample |

---

## Running

```bash
cd ML_baselines
python binary_relevance_with_bert.py
```

**Configuration:**
```python
MODEL_CHOICES = ['LightGBM', 'RF']
SEEDS = [42, 43, 44, 45, 46, 47, 48, 49]  # 8 runs for robustness
FEATURES = ["SATD Comment", "context", "bloc of first occurrence"]
```

---

## Hyperparameter Grids

### RandomForest
```python
{
    'n_estimators': [100, 200, 300],
    'criterion': ['gini', 'entropy'],
    'max_depth': [3, 5, 10],
    'min_samples_split': [2, 5, 10],
    'max_features': ['sqrt', 'log2']
}
```

### LightGBM
```python
{
    'num_leaves': [31, 63, 127],
    'max_depth': [2, 3, 5],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}
```

**Grid Search:**
- Scoring: `f1_weighted`
- CV: 3-fold on training data
- Parallelization: All CPU cores (`n_jobs=-1`)

---

## Output

**Location:** `../LLM_predictions/ML_predictions/`

**Filename:** `predictions_BR_{model}_seed{seed}_bert_revised.csv`

**Format:** Same as LLM predictions (fold, index, comment, context, code_block, 8 binary labels)

---

## BERT Details

- **Model:** `bert-base-uncased`
- **Tokenization:** Max 512 tokens, padding, truncation
- **Pooling:** Mean of last hidden states
- **Device:** Auto-detects CUDA/CPU
- **Deterministic:** All seeds fixed (Python, NumPy, PyTorch, CUDA)

---

## Reproducibility

- **8 different seeds** for robust evaluation
- **Same cross-validation folds** as LLM experiments
- **Deterministic settings** for all random components
- **Consistent feature extraction** across all runs

---

## Performance Comparison

ML baselines compared against LLMs in:
- **Statistical Testing:** `statistical_testing/apply_tim_testing.py`
- **Scenario:** `zero_shot_vs_ml_baselines`
- **Metrics:** Precision, Recall, F1-score per category
- **Test:** Effect Size Difference (ESD) with Scott-Knott rankings
