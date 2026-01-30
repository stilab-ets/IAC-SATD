# Data Format

Input and output CSV file specifications for RQ2 experiments.

---

## Input Data

### Location
`Data_Splitting/stratified_cleaned_folds/`

### Files
- `cleaned_dataset_revised_filtered.csv` - Full dataset
- `stratified_cleaned_train_fold_{0-4}.csv` - Training folds
- `stratified_cleaned_test_fold_{0-4}.csv` - Test folds

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `SATD Comment` | string | Single-line technical debt comment |
| `context` | string | Adjacent explanatory comments |
| `bloc of first occurrence` | string | Associated code block |
| `Computing Management Debt` | int (0/1) | Binary label for CAT1 |
| `IaC Code Debt` | int (0/1) | Binary label for CAT2 |
| `Dependency Management` | int (0/1) | Binary label for CAT3 |
| `Security Debt` | int (0/1) | Binary label for CAT4 |
| `Networking Debt` | int (0/1) | Binary label for CAT5 |
| `Environment-Based Configuration Debt` | int (0/1) | Binary label for CAT6 |
| `Monitoring and Logging Debt` | int (0/1) | Binary label for CAT7 |
| `Test Debt` | int (0/1) | Binary label for CAT8 |
| `Fold` | int (0-4) | Cross-validation fold number |
| `Index` | int | Row index within fold |

---

## Output Data (LLM Predictions)

### Location
- Zero-shot: `llm_crossval_runner/results/`
- Few-shot: `core/results/rag_{mode}_tests/`

### Filename Pattern
- Zero-shot: `{model}_eval_single_prompt_improved_v11_tmp_{temp}_v2.csv`
- Few-shot: `{model}_eval_v11_tmp_{temp}_rag_{mode}.csv`

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `fold` | int | Cross-validation fold |
| `row` | int | Row index |
| `SATD Comment` | string | Original comment |
| `context` | string | Original context |
| `bloc of first occurrence` | string | Original code block |
| `Response` | string | Raw LLM response |
| `Computing Management Debt` | int (0/1) | Predicted label |
| `IaC Code Debt` | int (0/1) | Predicted label |
| `Dependency Management` | int (0/1) | Predicted label |
| `Security Debt` | int (0/1) | Predicted label |
| `Networking Debt` | int (0/1) | Predicted label |
| `Environment-Based Configuration Debt` | int (0/1) | Predicted label |
| `Monitoring and Logging Debt` | int (0/1) | Predicted label |
| `Test Debt` | int (0/1) | Predicted label |
| `Predicted Categories` | string | List of predicted category names |

---

## Output Data (ML Predictions)

### Location
`LLM_predictions/ML_predictions/`

### Filename Pattern
`predictions_BR_{model}_seed{seed}_bert_revised.csv`

### Columns
Same as LLM predictions (without `Response` column)

---

## Statistical Testing Input

### Location
`statistical_testing/performance_analysis/`

### Files
- `zero_shot_vs_ml_baselines.csv`
- `few_shots_vs_zero_shot.csv`

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `fold` | int | Cross-validation fold |
| `label` | string | SATD category name |
| `model` | string | Model identifier |
| `run` | float | Run number (for multiple seeds) |
| `source` | string | "llm" or "ml" |
| `precision` | float | Precision score |
| `recall` | float | Recall score |
| `f1-score` | float | F1 score |

**Aggregated rows:**
- `label="Macro"` - Macro-averaged metrics
- `label="Micro"` - Micro-averaged metrics
- `label="Weighted"` - Weighted-averaged metrics

---

## Example: Input Row

```csv
SATD Comment,context,bloc of first occurrence,Computing Management Debt,IaC Code Debt,...,Fold,Index
"# TODO: fix container config","Need to update memory limits","resource \"aws_ecs_task_definition\" {...}",1,1,0,0,0,0,0,0,0,42
```

---

## Example: LLM Output Row

```csv
fold,row,SATD Comment,context,bloc of first occurrence,Response,Computing Management Debt,IaC Code Debt,...,Predicted Categories
0,42,"# TODO: fix container config","Need to update memory limits","resource \"aws_ecs_task_definition\" {...}","ANSWER: CAT1, CAT2",1,1,0,0,0,0,0,0,"['Computing Management Debt', 'IaC Code Debt']"
```

---

## Notes

- **Multi-label:** Each instance can have multiple categories (sum of labels ≥ 0)
- **Binary encoding:** 1 = category applies, 0 = does not apply
- **Missing values:** Should be avoided; use empty strings for text fields
- **Encoding:** UTF-8
- **Delimiter:** Comma (`,`)
