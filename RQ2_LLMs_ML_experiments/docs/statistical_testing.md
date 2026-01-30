# Statistical Testing

Rigorous statistical comparison of LLM and ML baseline performance using Effect Size Difference (ESD) tests.

---

## Overview

**Purpose:** Determine if performance differences between models are statistically significant

**Method:** Effect Size Difference (ESD) tests with Scott-Knott (SK) rankings

**Metrics:** Precision, Recall, F1-score (per category and aggregated)

---

## Running Tests

```bash
cd statistical_testing
python apply_tim_testing.py
```

### Configuration

Edit `apply_tim_testing.py`:
```python
# Scenario 1: Zero-shot LLMs vs ML baselines
run_scenario(scenario_zero_shot_vs_ml_baselines())

# Scenario 2: Few-shot vs Zero-shot LLMs
run_scenario(scenario_few_shots_vs_zero_shot())
```

---

## Test Scenarios

### 1. Zero-Shot vs ML Baselines

**Input:** `performance_analysis/zero_shot_vs_ml_baselines.csv`

**Output:** `performance_analysis/grouped/zero_shot_vs_ml_baselines/`
- `merged_precision_sk_ranks_zero_shot_vs_ml_baselines.csv`
- `merged_recall_sk_ranks_zero_shot_vs_ml_baselines.csv`
- `merged_f1-score_sk_ranks_zero_shot_vs_ml_baselines.csv`

**Compares:**
- ChatGPT, Claude, Gemini, Gemma, DeepSeek, Qwen (zero-shot)
- RandomForest + BERT
- LightGBM + BERT

### 2. Few-Shot vs Zero-Shot

**Input:** `performance_analysis/few_shots_vs_zero_shot.csv`

**Output:** `performance_analysis/grouped/few_shots_vs_zero_shot/`

**Compares:**
- Same LLMs with RAG (few-shot) vs without (zero-shot)

---

## Statistical Methods

### Effect Size Difference (ESD)

Implemented in `ESDTests.py`:
- Computes effect sizes between model pairs
- Generates Scott-Knott (SK) rankings
- Groups models into statistically distinct clusters

### Scott-Knott Rankings

- **Rank 1:** Best performing cluster
- **Rank 2, 3, ...:** Progressively lower performance
- Models in same rank: No significant difference

---

## Output Files

### Per-Label Results

`performance_analysis/data_transformer/output_by_label/{scenario}/{label}/{metric}_sk_rank.csv`

**Columns:**
- `model`: Model name
- `rank`: Scott-Knott rank
- `mean`: Mean performance across folds
- `median`: Median performance
- `iqr`: Interquartile range

### Merged Results

`performance_analysis/grouped/{scenario}/merged_{metric}_sk_ranks_{scenario}.csv`

**Contains:** All labels aggregated with SK ranks per label

---

## Metrics Analyzed

### Per-Category Metrics
- **Precision:** Fraction of correct positive predictions
- **Recall:** Fraction of actual positives correctly identified
- **F1-score:** Harmonic mean of precision and recall

### Aggregated Metrics
- **Macro:** Unweighted mean across categories
- **Micro:** Global average across all instances
- **Weighted:** Weighted by category support

---

## Workflow

1. **Data Preparation:** Transform predictions into metric files
   - `transform_simple.py` or `representation.py`

2. **Run ESD Tests:** Generate SK rankings
   - `apply_tim_testing.py`

3. **Analyze Results:** Review merged CSV files
   - Compare SK ranks across models
   - Identify statistically significant differences

---

## Interpretation

**Example Output:**
```csv
label,model,rank,mean,median,iqr
IaC Code Debt,chatgpt,1,0.89,0.89,0.02
IaC Code Debt,claude,2,0.87,0.87,0.03
IaC Code Debt,RF_BERT,2,0.86,0.86,0.04
```

**Interpretation:**
- ChatGPT significantly outperforms others (rank 1)
- Claude and RF_BERT perform similarly (both rank 2)
- No significant difference between Claude and RF_BERT

---

## Key Files

| File | Purpose |
|------|---------|
| `ESDTests.py` | ESD test implementation |
| `apply_tim_testing.py` | Test orchestration |
| `transform_simple.py` | Simple data transformation |
| `representation.py` | Advanced data transformation |
| `performance_analysis/` | Input data and results |
