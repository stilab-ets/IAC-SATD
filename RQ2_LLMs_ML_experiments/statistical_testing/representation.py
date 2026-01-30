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


# ------------------------------
# Configurations (two cases)
# ------------------------------
CONFIGS = {
    "zero_shot_vs_ml_baselines": {
        "paths": {
            "Precision": "./performance_analysis/grouped/zero_shot_vs_ml_baselines/merged_precision_sk_ranks_zero_shot_vs_ml_baselines.csv",
            "Recall": "./performance_analysis/grouped/zero_shot_vs_ml_baselines/merged_recall_sk_ranks_zero_shot_vs_ml_baselines.csv",
            "F1-Score": "./performance_analysis/grouped/zero_shot_vs_ml_baselines/merged_f1-score_sk_ranks_zero_shot_vs_ml_baselines.csv",
        },
        "model_names": ["chatgpt", "claude", "deepseek", "gemini", "qwen", "gemma", "LightGBM", "RF"],
        "model_mapping": {
            "chatgpt": "CH",
            "claude": "CL",
            "deepseek": "DP",
            "gemini": "GI",
            "qwen": "QW",
            "gemma": "GA",
            "LightGBM": "LG",
            "RF": "RF",
        },
        "caption": "Zero-shot LLMs vs. ML baselines with Scott--Knott ESD ranks.",
        "latex_label": "tab:zero-shot-vs-ml-skd",
    },

    "few_shots_vs_zero_shot": {
        "paths": {
            "Precision": "./performance_analysis/grouped/few_shots_vs_zero_shot/merged_precision_sk_ranks_few_shots_vs_zero_shot.csv",
            "Recall": "./performance_analysis/grouped/few_shots_vs_zero_shot/merged_recall_sk_ranks_few_shots_vs_zero_shot.csv",
            "F1-Score": "./performance_analysis/grouped/few_shots_vs_zero_shot/merged_f1-score_sk_ranks_few_shots_vs_zero_shot.csv",
        },
        "model_names": [
            # few-shot LLMs (RAG)
            "chatgpt_rag_openai_precomputed",
            "claude_rag_openai_precomputed",
            "deepseek_rag_openai_precomputed",
            "gemini_rag_openai_precomputed",
            "qwen_rag_openai_precomputed",
            "gemma_rag_openai_precomputed",
            # few-shot baselines (facebook examples)
            "chatgpt_facebook",
            "gemini_facebook",
            "claude_facebook",
        ],
        "model_mapping": {
            # facebook few-shot
            "chatgpt_facebook": "CH",
            "gemini_facebook": "GI",
            "claude_facebook": "CL",
            # RAG few-shot
            "chatgpt_rag_openai_precomputed": "CHR",
            "claude_rag_openai_precomputed": "CLR",
            "deepseek_rag_openai_precomputed": "DER",
            "qwen_rag_openai_precomputed": "QWR",
            "gemma_rag_openai_precomputed": "GER",
            "gemini_rag_openai_precomputed": "GIR",
        },
        "caption": "Few-shot (RAG / in-context) vs. zero-shot with Scott--Knott ESD ranks.",
        "latex_label": "tab:few-shot-vs-zero-shot-skd",
    },
}


def load_skd_tables(paths: dict) -> dict[str, pd.DataFrame]:
    return {metric: pd.read_csv(fp) for metric, fp in paths.items()}


def generate_latex_table_from_skd(
    sk_ranks: dict[str, pd.DataFrame],
    labels: list[str],
    model_names: list[str],
    model_mapping: dict[str, str],
    metric_columns: list[str],
    caption: str,
    latex_label: str,
) -> None:
    print("\\begin{table*}[ht]")
    print("\\fontsize{4.75}{10}\\selectfont")
    print("\\tabcolsep=0.1cm")
    print("\\centering")
    print(f"\\caption{{{caption}}}")

    n_models = len(model_names)
    print("\\begin{tabular}{@{}l!{\\vrule width 1pt}" +
          f"*{{{n_models}}}{{c}}!{{\\vrule width 1pt}}" +
          f"*{{{n_models}}}{{c}}!{{\\vrule width 1pt}}" +
          f"*{{{n_models}}}{{c}}@{{}}}}")
    print("\\toprule")

    # Header row 1
    print("\\rowcolor{black}")
    print("\\textcolor{white}{\\textbf{Cat.}} &"
          f"\\multicolumn{{{n_models}}}{{c!{{\\vrule width 1pt}}}}{{\\cellcolor{{black}}\\textcolor{{white}}{{\\textbf{{Precision}}}}}} &"
          f"\\multicolumn{{{n_models}}}{{c!{{\\vrule width 1pt}}}}{{\\cellcolor{{black}}\\textcolor{{white}}{{\\textbf{{Recall}}}}}} &"
          f"\\multicolumn{{{n_models}}}{{c}}{{\\cellcolor{{black}}\\textcolor{{white}}{{\\textbf{{F1-score}}}}}} \\\\"
          )

    # Header row 2
    print("\\rowcolor{black}")
    model_headers = [f"\\textcolor{{white}}{{\\textbf{{{model_mapping.get(m, m)}}}}}" for m in model_names]
    print("\\textcolor{white}{} & " + " & ".join(model_headers * len(metric_columns)) + " \\\\")
    print("\\midrule")

    core_labels = labels[:8]
    post_core_labels = labels[8:]  # Weighted etc.

    for i, label in enumerate(labels):
        row_label = ROW_LABEL_MAP.get(label, label)
        row = [row_label]

        for metric in metric_columns:
            df = sk_ranks[metric]
            for model in model_names:
                row_data = df[(df["label"] == label) & (df["model"] == model)]
                if row_data.empty:
                    row.append("--")
                    continue

                val = float(row_data["median"].values[0])
                if label in post_core_labels:
                    row.append(f"{val:.3f}")
                else:
                    rank = float(row_data["rank"].values[0])
                    cell = f"{val:.3f} ({rank:g})"
                    row.append(f"\\textbf{{{cell}}}" if rank == 1 else cell)

        print("\\rowcolor[HTML]{DADADA} " + " & ".join(row) + " \\\\" if i % 2 == 0 else " & ".join(row) + " \\\\")

        if row_label == "C8":
            print("\\midrule")

            # Median rank row (computed over C1..C8)
            med_rank_row = ["Median Rank"]
            med_rank_values = {metric: [] for metric in metric_columns}

            for metric in metric_columns:
                df = sk_ranks[metric]
                df_core = df[df["label"].isin(core_labels)]
                for model in model_names:
                    model_ranks = df_core[df_core["model"] == model]["rank"]
                    med = float(model_ranks.median()) if not model_ranks.empty else None
                    med_rank_values[metric].append(med)

            # Bold best (minimum) median rank per metric
            for metric in metric_columns:
                values = [v for v in med_rank_values[metric] if v is not None]
                min_val = min(values) if values else None
                for v in med_rank_values[metric]:
                    if v is None:
                        med_rank_row.append("--")
                    elif v == min_val:
                        med_rank_row.append(f"\\textbf{{{v:.2f}}}")
                    else:
                        med_rank_row.append(f"{v:.2f}")

            print("\\rowcolor[HTML]{EFEFEF} " + " & ".join(med_rank_row) + " \\\\")
            print("\\midrule")

    print("\\bottomrule")
    print("\\end{tabular}")
    print(f"\\label{{{latex_label}}}")
    print("\\end{table*}")


if __name__ == "__main__":
    # Choose one:
    # CONFIG_NAME = "zero_shot_vs_ml_baselines"
    CONFIG_NAME = "few_shots_vs_zero_shot"

    cfg = CONFIGS[CONFIG_NAME]
    sk_ranks = load_skd_tables(cfg["paths"])

    generate_latex_table_from_skd(
        sk_ranks=sk_ranks,
        labels=LABELS,
        model_names=cfg["model_names"],
        model_mapping=cfg["model_mapping"],
        metric_columns=METRIC_COLUMNS,
        caption=cfg["caption"],
        latex_label=cfg["latex_label"],
    )
