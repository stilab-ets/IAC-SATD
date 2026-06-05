import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


METRICS = ["precision", "recall", "f1-score"]
DEFAULT_LABELS = ["Weighted"]
PALETTE = {
    "precision": ("#1f5aa6", "Weighted Precision"),
    "recall": ("#b04a00", "Weighted Recall"),
    "f1-score": ("#1d7f5f", "Weighted F1-score"),
}

SCENARIOS = {
    "zero_shots": {
        "input_csv": "performance_analysis/zero_shot_vs_ml_baselines.csv",
        # Temperature is meaningful only for the LLM rows in this file.
        "models": ["chatgpt", "claude", "deepseek", "gemini", "gemma", "qwen"],
    },
    "few_shots": {
        "input_csv": "performance_analysis/few_shots_vs_zero_shot.csv",
        "models": [
            "chatgpt_rag_openai_precomputed",
            "claude_rag_openai_precomputed",
            "deepseek_rag_openai_precomputed",
            "gemini_rag_openai_precomputed",
            "gemma_rag_openai_precomputed",
            "qwen_rag_openai_precomputed",
        ],
    },
}

MODEL_DISPLAY = {
    "chatgpt": "ChatGPT Zero-Shot",
    "claude": "Claude Zero-Shot",
    "deepseek": "DeepSeek Zero-Shot",
    "gemini": "Gemini Zero-Shot",
    "gemma": "Gemma Zero-Shot",
    "qwen": "Qwen Zero-Shot",
    "chatgpt_rag_openai_precomputed": "ChatGPT Few-Shot",
    "claude_rag_openai_precomputed": "Claude Few-Shot",
    "deepseek_rag_openai_precomputed": "DeepSeek Few-Shot",
    "gemini_rag_openai_precomputed": "Gemini Few-Shot",
    "gemma_rag_openai_precomputed": "Gemma Few-Shot",
    "qwen_rag_openai_precomputed": "Qwen Few-Shot",
}


def sanitize_name(value: str) -> str:
    return value.strip().replace(" ", "_").replace("/", "_").replace("-", "_")


def display_name(model_name: str) -> str:
    return MODEL_DISPLAY.get(model_name, model_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate median-based temperature sensitivity analysis for LLM results. "
            "The script treats `run` as temperature and uses fold-level rows as repeated measurements."
        )
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=sorted(SCENARIOS.keys()),
        default=["zero_shots", "few_shots"],
        help="Which scenario folders to generate.",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        default=DEFAULT_LABELS,
        help="Labels to analyze, for example Weighted Macro Micro or a specific category label.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Optional subset of models. If omitted, uses the scenario defaults.",
    )
    return parser.parse_args()


def build_temperature_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for run, group in df.groupby("run", sort=True):
        row = {"temperature": run}
        for metric in METRICS:
            series = group.sort_values("fold")[metric]
            row[f"{metric}_median"] = series.median()
            row[f"{metric}_q1"] = series.quantile(0.25)
            row[f"{metric}_q3"] = series.quantile(0.75)
            row[f"{metric}_min"] = series.min()
            row[f"{metric}_max"] = series.max()
        rows.append(row)
    return pd.DataFrame(rows).sort_values("temperature").reset_index(drop=True)


def build_fold_values_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for run, group in df.groupby("run", sort=True):
        row = {"temperature": run}
        ordered = group.sort_values("fold")
        for metric in METRICS:
            values = ordered[metric].tolist()
            for fold_value, value in enumerate(values):
                row[f"{metric}_fold_{fold_value}"] = value
            row[f"{metric}_median"] = pd.Series(values).median()
        rows.append(row)
    return pd.DataFrame(rows).sort_values("temperature").reset_index(drop=True)


def build_sensitivity_report(summary_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        metric_col = f"{metric}_median"
        best_idx = summary_df[metric_col].idxmax()
        worst_idx = summary_df[metric_col].idxmin()

        best_temp = float(summary_df.loc[best_idx, "temperature"])
        best_value = float(summary_df.loc[best_idx, metric_col])
        worst_temp = float(summary_df.loc[worst_idx, "temperature"])
        worst_value = float(summary_df.loc[worst_idx, metric_col])

        rows.append(
            {
                "metric": metric,
                "best_temperature": best_temp,
                "best_median": best_value,
                "worst_temperature": worst_temp,
                "worst_median": worst_value,
                "median_gap": best_value - worst_value,
                "median_of_temperature_medians": float(summary_df[metric_col].median()),
            }
        )
    return pd.DataFrame(rows)


def write_text_report(
    report_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    scenario_name: str,
    model_name: str,
    label_name: str,
    output_path: Path,
) -> None:
    lines = [
        f"Temperature sensitivity report",
        f"Scenario: {scenario_name}",
        f"Model: {display_name(model_name)}",
        f"Label: {label_name}",
        "",
        "Temperature medians by metric:",
        summary_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"),
        "",
        "Sensitivity summary:",
        report_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"),
        "",
        "Interpretation helper:",
        "- `best_temperature` is the temperature with the highest median score.",
        "- `worst_temperature` is the temperature with the lowest median score.",
        "- `median_gap` is the practical spread across temperatures.",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def plot_temperature_lines(summary_df: pd.DataFrame, model_name: str, label_name: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5.5))

    for metric in METRICS:
        color, default_label = PALETTE[metric]
        axis_label = default_label.replace("Weighted", label_name) if label_name in {"Weighted", "Macro", "Micro"} else f"{label_name} {metric.title()}"
        median_col = f"{metric}_median"

        ax.plot(
            summary_df["temperature"],
            summary_df[median_col],
            marker="o" if metric == "precision" else ("s" if metric == "recall" else "^"),
            linewidth=2.2 if metric != "f1-score" else 2.4,
            color=color,
            label=axis_label,
        )

    all_values = []
    for metric in METRICS:
        all_values.extend(summary_df[f"{metric}_median"].tolist())

    y_min = max(0.0, min(all_values) - 0.01)
    y_max = min(1.0, max(all_values) + 0.01)

    ax.set_title(f"{display_name(model_name)} Temperature Sensitivity on {label_name} Metrics")
    ax.set_xlabel("Temperature")
    ax.set_ylabel("Score")
    ax.set_xticks(summary_df["temperature"])
    ax.set_ylim(y_min, y_max)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def analyze_model_label(df: pd.DataFrame, scenario_name: str, model_name: str, label_name: str, output_root: Path) -> None:
    subset = df[(df["model"] == model_name) & (df["label"] == label_name)].copy()
    if subset.empty:
        return

    model_dir = output_root / sanitize_name(model_name) / sanitize_name(label_name)
    model_dir.mkdir(parents=True, exist_ok=True)

    summary_df = build_temperature_summary(subset)
    folds_df = build_fold_values_table(subset)
    report_df = build_sensitivity_report(summary_df)

    summary_csv = model_dir / "temperature_summary_median_iqr.csv"
    folds_csv = model_dir / "fold_values_and_medians.csv"
    report_csv = model_dir / "sensitivity_report.csv"
    report_txt = model_dir / "sensitivity_report.txt"
    plot_png = model_dir / "temperature_lines_median.png"

    summary_df.to_csv(summary_csv, index=False)
    folds_df.to_csv(folds_csv, index=False)
    report_df.to_csv(report_csv, index=False)
    write_text_report(report_df, summary_df, scenario_name, model_name, label_name, report_txt)
    plot_temperature_lines(summary_df, model_name, label_name, plot_png)

    print(f"[saved] {plot_png}")


def run_scenario(scenario_name: str, labels: list[str], models_override: list[str] | None) -> None:
    config = SCENARIOS[scenario_name]
    base_dir = Path(__file__).resolve().parent
    input_csv = base_dir / config["input_csv"]
    output_root = base_dir / "performance_analysis" / "temperature_sensitivity" / scenario_name
    output_root.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_csv)
    models = models_override if models_override else config["models"]

    for model_name in models:
        for label_name in labels:
            analyze_model_label(df, scenario_name, model_name, label_name, output_root)


def main() -> None:
    args = parse_args()
    for scenario_name in args.scenarios:
        run_scenario(scenario_name, args.labels, args.models)


if __name__ == "__main__":
    main()
