# RQ2: LLM and Machine Learning Experiments

This directory contains the implementation and analysis artifacts for **Research Question 2 (RQ2)**: evaluating how well LLMs and ML baselines classify Infrastructure-as-Code (Terraform) SATD instances into multiple debt categories.

## Scope

RQ2 contains four main parts:

1. `Data_Splitting/`
   Cross-validation folds used by the experiments.
2. `LLMs_bootstrap/`
   Zero-shot and few-shot/RAG LLM execution code.
3. `ML_baselines/`
   Traditional ML baselines built on top of BERT-based representations.
4. `statistical_testing/`
   Post-processing, statistical comparison, table generation, and temperature sensitivity analysis.

## RQ2 Workflow

The practical pipeline is:

```text
folded SATD dataset
-> zero-shot LLM predictions
-> few-shot/RAG LLM predictions
-> ML baseline predictions
-> aggregated performance CSVs
-> statistical comparison and table generation
-> temperature sensitivity analysis
```

At a high level:

- `LLMs_bootstrap/` generates LLM predictions.
- `ML_baselines/` generates ML baseline predictions.
- `statistical_testing/performance_analysis/*.csv` stores aggregated metric results.
- `statistical_testing/` converts those results into Scott-Knott ESD comparisons, LaTeX tables, and sensitivity-analysis outputs.

## Debt Categories

The multi-label classification task covers 8 SATD categories:

| Code | Category |
| --- | --- |
| `C1` | Computing Components Management Debt |
| `C2` | IaC Code Debt |
| `C3` | Dependency Management Debt |
| `C4` | Security Debt |
| `C5` | Networking Debt |
| `C6` | Environment-Based Configuration Debt |
| `C7` | Monitoring and Logging Debt |
| `C8` | Test Debt |

The aggregated result files also contain:

- `Macro`
- `Micro`
- `Weighted`

These are fold-level aggregate measures, not additional debt categories.

## Directory Map

```text
RQ2_LLMs_ML_experiments/
|-- Data_Splitting/
|-- docs/
|   |-- data_format.md
|   |-- llm_experiments.md
|   |-- ml_baselines.md
|   |-- statistical_testing.md
|   `-- troubleshooting.md
|-- LLM_predictions/
|   |-- llms_predictions_zero_shot/
|   |-- llms_predictions_few_shots/
|   `-- ML_predictions/
|-- LLMs_bootstrap/
|   |-- core/
|   |   |-- main.py
|   |   |-- crossval_executor.py
|   |   |-- models/
|   |   `-- retriever/
|   `-- prompts/
|-- ML_baselines/
|   |-- binary_relevance_with_bert.py
|   `-- prediction_saver.py
|-- statistical_testing/
|   |-- apply_tim_testing.py
|   |-- transform_simple.py
|   |-- representation.py
|   |-- representation_structured.py
|   |-- temperature_sensitivity_analysis.py
|   |-- temperature_sensitivity_markdown.py
|   `-- performance_analysis/
|       |-- zero_shot_vs_ml_baselines.csv
|       |-- few_shots_vs_zero_shot.csv
|       |-- grouped/
|       `-- temperature_sensitivity/
|-- qwen3_nonthinking.jinja
|-- run_vllm_satd_all_models.slurm
`-- run_vllm_satd_qwen.slurm
```

## Main Experiment Entry Points

### Zero-shot LLM experiments

Main runner:

- [LLMs_bootstrap/core/main.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/LLMs_bootstrap/core/main.py)

Typical usage:

```bash
cd LLMs_bootstrap/core
python main.py
```

### Few-shot / RAG LLM experiments

Main runner:

- [LLMs_bootstrap/core/retriever/main_RAG.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/LLMs_bootstrap/core/retriever/main_RAG.py)

Typical usage:

```bash
cd LLMs_bootstrap/core/retriever
python main_RAG.py
```

### ML baselines

Main runner:

- [ML_baselines/binary_relevance_with_bert.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/ML_baselines/binary_relevance_with_bert.py)

Typical usage:

```bash
cd ML_baselines
python binary_relevance_with_bert.py
```

## Performance Analysis Inputs

Two aggregated CSV files are central to the downstream analysis:

- [zero_shot_vs_ml_baselines.csv](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/performance_analysis/zero_shot_vs_ml_baselines.csv)
- [few_shots_vs_zero_shot.csv](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/performance_analysis/few_shots_vs_zero_shot.csv)

Each row represents one result for a specific:

- `fold`
- `label`
- `model`
- `run`
- metric triple: `precision`, `recall`, `f1-score`

For the LLM analyses in this repository, `run` is used as the temperature setting of the model.

## Statistical Testing and Table Generation

The main statistical-comparison utilities are:

- [transform_simple.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/transform_simple.py)
- [apply_tim_testing.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/apply_tim_testing.py)
- [representation.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/representation.py)
- [representation_structured.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/representation_structured.py)

Suggested sequence:

1. Run `transform_simple.py` to prepare grouped metric files.
2. Run `apply_tim_testing.py` to compute Scott-Knott ESD groupings and summary statistics.
3. Run one of the representation scripts to generate LaTeX tables.

## Temperature Sensitivity Analysis

Temperature sensitivity is handled by:

- [temperature_sensitivity_analysis.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/temperature_sensitivity_analysis.py)
- [temperature_sensitivity_markdown.py](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/temperature_sensitivity_markdown.py)

### What the analysis script does

`temperature_sensitivity_analysis.py`:

- reads the aggregated performance CSVs in `statistical_testing/performance_analysis/`
- filters the selected models and labels
- groups rows by temperature (`run`) and fold
- computes temperature-wise medians for `precision`, `recall`, and `f1-score`
- saves per-model CSV summaries, text reports, and line plots

It does **not** change the original experiment outputs. It only creates derived analysis files.

### Current default scope

The script currently focuses on:

- `Weighted` only
- zero-shot LLMs:
  - `ChatGPT Zero-Shot` (`chatgpt`)
  - `Claude Zero-Shot` (`claude`)
  - `DeepSeek Zero-Shot` (`deepseek`)
  - `Gemini Zero-Shot` (`gemini`)
  - `Gemma Zero-Shot` (`gemma`)
  - `Qwen Zero-Shot` (`qwen`)
- few-shot RAG LLMs:
  - `ChatGPT Few-Shot` (`chatgpt_rag_openai_precomputed`)
  - `Claude Few-Shot` (`claude_rag_openai_precomputed`)
  - `DeepSeek Few-Shot` (`deepseek_rag_openai_precomputed`)
  - `Gemini Few-Shot` (`gemini_rag_openai_precomputed`)
  - `Gemma Few-Shot` (`gemma_rag_openai_precomputed`)
  - `Qwen Few-Shot` (`qwen_rag_openai_precomputed`)

### Generated outputs

The derived outputs are written under:

- `statistical_testing/performance_analysis/temperature_sensitivity/zero_shots/`
- `statistical_testing/performance_analysis/temperature_sensitivity/few_shots/`

For each model, the script generates:

- `temperature_summary_median_iqr.csv`
- `fold_values_and_medians.csv`
- `sensitivity_report.csv`
- `sensitivity_report.txt`
- `temperature_lines_median.png`

The Markdown summary is then assembled by `temperature_sensitivity_markdown.py` into:

- [weighted_temperature_sensitivity_report.md](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/statistical_testing/performance_analysis/temperature_sensitivity/weighted_temperature_sensitivity_report.md)

### Typical usage

```bash
cd statistical_testing
python temperature_sensitivity_analysis.py
python temperature_sensitivity_markdown.py
```

## Documentation

Additional documentation is available in:

- [docs/ml_baselines.md](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/docs/ml_baselines.md)
- [docs/llm_experiments.md](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/docs/llm_experiments.md)
- [docs/statistical_testing.md](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/docs/statistical_testing.md)
- [docs/data_format.md](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/docs/data_format.md)
- [docs/troubleshooting.md](/C:/Users/Admin/PycharmProjects/replication_SATD_IaC/RQ2_LLMs_ML_experiments/docs/troubleshooting.md)

## Execution Notes

- This codebase was originally developed with PyCharm project-root assumptions.
- If you run scripts from the command line, import paths may need adjustment.
- Test with a small subset before launching a full cross-validation or full API-backed run.
- Monitor API rate limits and cost for commercial LLM providers.
- Some files in `statistical_testing/` are report-generation utilities, not experiment runners.
