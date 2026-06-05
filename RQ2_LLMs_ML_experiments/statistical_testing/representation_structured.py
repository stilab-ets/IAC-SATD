import pandas as pd

METRIC_COLUMNS = ["Precision", "Recall", "F1-Score"]

LABELS = [
    "IaC Code Debt",
    "Infrastructure Management Debt",
    "Security Debt",
    "Networking Debt",
    "Dependency Management",
    "Environment-Based Configuration Debt",
    "Monitoring and Logging Debt",
    "Test Debt",
    "Weighted",
]

ROW_LABEL_MAP = {
    "IaC Code Debt": "C1",
    "Infrastructure Management Debt": "C2",
    "Security Debt": "C3",
    "Networking Debt": "C4",
    "Dependency Management": "C5",
    "Environment-Based Configuration Debt": "C6",
    "Monitoring and Logging Debt": "C7",
    "Test Debt": "C8",
    "Weighted": "Weighted",
}


CONFIGS = {
    "zero_shot_vs_ml_baselines": {
        "paths": {
            "Precision": "./performance_analysis/grouped/zero_shot_vs_ml_baselines/merged_precision_sk_ranks_zero_shot_vs_ml_baselines.csv",
            "Recall": "./performance_analysis/grouped/zero_shot_vs_ml_baselines/merged_recall_sk_ranks_zero_shot_vs_ml_baselines.csv",
            "F1-Score": "./performance_analysis/grouped/zero_shot_vs_ml_baselines/merged_f1-score_sk_ranks_zero_shot_vs_ml_baselines.csv",
        },
        "row_groups": [
            {
                "setting": "Zero-shot",
                "models": ["chatgpt", "claude", "deepseek", "gemini", "qwen", "gemma"],
            },
            {
                "setting": "ML",
                "models": ["LightGBM", "RF"],
            },
        ],
        "model_display": {
            "chatgpt": "ChatGPT",
            "claude": "Claude",
            "deepseek": "DeepSeek",
            "gemini": "Gemini",
            "qwen": "Qwen",
            "gemma": "Gemma",
            "LightGBM": "GBM",
            "RF": "RF",
        },
        "caption": "Performance of Zero-Shot prompting compared to ML-based classifiers with Scott-Knott ESD ranks.",
        "latex_label": "tab:zero-shot-versus-ml-models-skd",
        "note": "Results are reported as $Median(Rank)$, where lower SK-ESD ranks indicate better performance. Algorithms with $Rank=1$ are shown in bold.",
    },
    "few_shots_vs_zero_shot": {
        "paths": {
            "Precision": "./performance_analysis/grouped/few_shots_vs_zero_shot/merged_precision_sk_ranks_few_shots_vs_zero_shot.csv",
            "Recall": "./performance_analysis/grouped/few_shots_vs_zero_shot/merged_recall_sk_ranks_few_shots_vs_zero_shot.csv",
            "F1-Score": "./performance_analysis/grouped/few_shots_vs_zero_shot/merged_f1-score_sk_ranks_few_shots_vs_zero_shot.csv",
        },
        "row_groups": [
            {
                "setting": "Few shot",
                "models": [
                    "chatgpt_rag_openai_precomputed",
                    "claude_rag_openai_precomputed",
                    "deepseek_rag_openai_precomputed",
                    "gemini_rag_openai_precomputed",
                    "qwen_rag_openai_precomputed",
                    "gemma_rag_openai_precomputed",
                ],
            },
            {
                "setting": "Zero shot",
                "models": [
                    "chatgpt_facebook",
                    "gemini_facebook",
                    "claude_facebook",
                ],
            },
        ],
        "model_display": {
            "chatgpt_rag_openai_precomputed": "ChatGPT",
            "claude_rag_openai_precomputed": "Claude",
            "deepseek_rag_openai_precomputed": "DeepSeek",
            "gemini_rag_openai_precomputed": "Gemini",
            "qwen_rag_openai_precomputed": "Qwen",
            "gemma_rag_openai_precomputed": "Gemma",
            "chatgpt_facebook": "ChatGPT",
            "gemini_facebook": "Gemini",
            "claude_facebook": "Claude",
        },
        "caption": "Performance of Few-Shot prompting configurations with Scott-Knott ESD ranks.",
        "latex_label": "tab:few-shot-configurations-skd",
        "note": "Results are reported as $Median(Rank)$, where lower SK-ESD ranks indicate better performance. Algorithms with $Rank=1$ are shown in bold.",
    },
}


def load_skd_tables(paths: dict) -> dict[str, pd.DataFrame]:
    return {metric: pd.read_csv(fp) for metric, fp in paths.items()}


def flatten_models(row_groups: list[dict]) -> list[str]:
    return [model for group in row_groups for model in group["models"]]


def build_lookup_table(df: pd.DataFrame) -> dict[tuple[str, str], dict[str, float]]:
    lookup = {}
    for _, row in df.iterrows():
        lookup[(row["label"], row["model"])] = {
            "rank": float(row["rank"]),
            "median": float(row["median"]),
        }
    return lookup


def get_value(lookup: dict, label: str, model: str) -> dict[str, float] | None:
    return lookup.get((label, model))


def format_category_cell(lookup: dict, label: str, model: str) -> str:
    cell = get_value(lookup, label, model)
    if cell is None:
        return "--"

    value = f"{cell['median']:.3f} ({cell['rank']:g})"
    return f"\\textbf{{{value}}}" if cell["rank"] == 1 else value


def format_weighted_cell(lookup: dict, model: str) -> str:
    cell = get_value(lookup, "Weighted", model)
    if cell is None:
        return "--"
    return f"{cell['median']:.3f}"


def compute_median_ranks(lookup: dict, core_labels: list[str], models: list[str]) -> dict[str, float | None]:
    median_ranks = {}
    for model in models:
        ranks = []
        for label in core_labels:
            cell = get_value(lookup, label, model)
            if cell is not None:
                ranks.append(cell["rank"])
        median_ranks[model] = float(pd.Series(ranks).median()) if ranks else None
    return median_ranks


def format_median_rank_cell(median_rank: float | None, best_rank: float | None) -> str:
    if median_rank is None:
        return "--"
    text = f"{median_rank:.2f}"
    return f"\\textbf{{{text}}}" if best_rank is not None and median_rank == best_rank else text


def generate_structured_latex_table(
    sk_ranks: dict[str, pd.DataFrame],
    labels: list[str],
    row_groups: list[dict],
    model_display: dict[str, str],
    metric_columns: list[str],
    caption: str,
    latex_label: str,
    note: str,
) -> None:
    core_labels = labels[:8]
    all_models = flatten_models(row_groups)
    total_models_per_metric = len(all_models)

    print("\\begin{table*}[t]")
    print("\\centering")
    print(f"\\caption{{{caption}}}")
    print(f"\\label{{{latex_label}}}")
    print("")
    print("\\begingroup")
    print("\\scriptsize")
    print("\\setlength{\\tabcolsep}{3pt}")
    print("\\renewcommand{\\arraystretch}{0.92}")
    print("")
    print("\\adjustbox{max width=\\textwidth}{")
    print("\\begin{tabular}{@{}lllcccccccccc@{}}")
    print("")
    print("\\toprule")
    print("\\rowcolor{black}")
    print("\\textcolor{white}{\\textbf{Metric}} &")
    print("\\textcolor{white}{\\textbf{Setting}} &")
    print("\\textcolor{white}{\\textbf{Model}} &")
    print("\\multicolumn{8}{c}{\\cellcolor{black}\\textcolor{white}{\\textbf{Categories}}} &")
    print("\\textcolor{white}{\\textbf{Median Rank}} &")
    print("\\textcolor{white}{\\textbf{Weighted}} \\\\")
    print("")
    print("\\rowcolor{black}")
    print("\\textcolor{white}{} &")
    print("\\textcolor{white}{} &")
    print("\\textcolor{white}{} &")
    print(" & ".join([f"\\textcolor{{white}}{{\\textbf{{{ROW_LABEL_MAP[label]}}}}}" for label in core_labels]) + " &")
    print("\\textcolor{white}{} &")
    print("\\textcolor{white}{} \\\\")
    print("\\midrule")
    print("")

    for metric_idx, metric in enumerate(metric_columns):
        metric_df = sk_ranks[metric]
        lookup = build_lookup_table(metric_df)
        median_ranks = compute_median_ranks(lookup, core_labels, all_models)
        valid_ranks = [rank for rank in median_ranks.values() if rank is not None]
        best_median_rank = min(valid_ranks) if valid_ranks else None

        metric_started = False

        for group_idx, group in enumerate(row_groups):
            group_models = group["models"]
            group_setting = group["setting"]

            for model_idx, model in enumerate(group_models):
                row = []

                if not metric_started:
                    row.append(f"\\multirow{{{total_models_per_metric}}}{{*}}{{{metric}}}")
                    metric_started = True
                else:
                    row.append("")

                if model_idx == 0:
                    row.append(f"\\multirow{{{len(group_models)}}}{{*}}{{{group_setting}}}")
                else:
                    row.append("")

                row.append(model_display.get(model, model))

                for label in core_labels:
                    row.append(format_category_cell(lookup, label, model))

                row.append(format_median_rank_cell(median_ranks[model], best_median_rank))
                row.append(format_weighted_cell(lookup, model))

                print(" & ".join(row) + " \\\\")

            if group_idx < len(row_groups) - 1:
                print("")
                print("\\arrayrulecolor{black}")
                print("\\cmidrule(lr){2-13}")
                print("")

        if metric_idx < len(metric_columns) - 1:
            print("")
            print("\\midrule")
            print("")

    print("\\bottomrule")
    print("\\end{tabular}")
    print("}")
    print("")
    print("\\vspace{0.05cm}")
    print("\\begin{minipage}{0.98\\textwidth}")
    print("\\scriptsize")
    print(f"\\textit{{Note.}} {note}")
    print("\\end{minipage}")
    print("")
    print("\\endgroup")
    print("\\end{table*}")


if __name__ == "__main__":
    CONFIG_NAME = "zero_shot_vs_ml_baselines"
    # CONFIG_NAME = "few_shots_vs_zero_shot"

    cfg = CONFIGS[CONFIG_NAME]
    sk_ranks = load_skd_tables(cfg["paths"])

    generate_structured_latex_table(
        sk_ranks=sk_ranks,
        labels=LABELS,
        row_groups=cfg["row_groups"],
        model_display=cfg["model_display"],
        metric_columns=METRIC_COLUMNS,
        caption=cfg["caption"],
        latex_label=cfg["latex_label"],
        note=cfg["note"],
    )
