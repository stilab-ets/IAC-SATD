from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.transforms import ScaledTranslation

SCRIPT_DIR = Path(__file__).resolve().parent

SETTING_CONFIG = {
    "zero_shot": {
        "zip_path": SCRIPT_DIR / "../../../RQ2_LLMs_ML_experiments/LLM_predictions/llms_predictions_zero_shot.zip",
        "ground_truth_path": SCRIPT_DIR / "../../ISA_application/ground_truth_zero.csv",
        "algorithm_bin_path": SCRIPT_DIR / "../../ISA_application/evaluation_details_hamming_zero_shot/algorithm_bin.csv",
        "out_dir": SCRIPT_DIR / "zero_shot_all_models_failed_instance_heatmaps",
    },
    "few_shots": {
        "zip_path": SCRIPT_DIR / "../../../RQ2_LLMs_ML_experiments/LLM_predictions/llms_predictions_few_shots.zip",
        "ground_truth_path": SCRIPT_DIR / "../../ISA_application/ground_truth_few.csv",
        "algorithm_bin_path": SCRIPT_DIR / "../../ISA_application/evaluation_details_hamming_few_shots/algorithm_bin.csv",
        "out_dir": SCRIPT_DIR / "few_shots_all_models_failed_instance_heatmaps",
    },
}

MODELS = ["chatgpt", "claude", "deepseek", "gemini", "gemma", "qwen"]
MODEL_LABELS = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "deepseek": "DeepSeek",
    "gemini": "Gemini",
    "gemma": "Gemma",
    "qwen": "Qwen",
}
LABEL_COLS = [
    "Infrastructure Management Debt",
    "IaC Code Debt",
    "Dependency Management",
    "Security Debt",
    "Networking Debt",
    "Environment-Based Configuration Debt",
    "Monitoring and Logging Debt",
    "Test Debt",
]
LABEL_SHORT = {
    "Infrastructure Management Debt": "Infra Mgmt",
    "IaC Code Debt": "IaC Code",
    "Dependency Management": "Dependency",
    "Security Debt": "Security",
    "Networking Debt": "Networking",
    "Environment-Based Configuration Debt": "Env Config",
    "Monitoring and Logging Debt": "Monitoring",
    "Test Debt": "Test",
}
LABEL_CODES = {
    "Infrastructure Management Debt": "C1",
    "IaC Code Debt": "C2",
    "Dependency Management": "C3",
    "Security Debt": "C4",
    "Networking Debt": "C5",
    "Environment-Based Configuration Debt": "C6",
    "Monitoring and Logging Debt": "C7",
    "Test Debt": "C8",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--setting",
        choices=sorted(SETTING_CONFIG),
        default="zero_shot",
        help="Prompting setting to analyze.",
    )
    return parser.parse_args()


def load_ground_truth(setting: str) -> pd.DataFrame:
    return pd.read_csv(SETTING_CONFIG[setting]["ground_truth_path"])


def load_algorithm_bin(setting: str) -> pd.DataFrame:
    return pd.read_csv(SETTING_CONFIG[setting]["algorithm_bin_path"])


def discover_run_members(setting: str, model: str) -> list[str]:
    with zipfile.ZipFile(SETTING_CONFIG[setting]["zip_path"]) as zf:
        members = [
            name
            for name in zf.namelist()
            if name.endswith(".csv") and Path(name).name.startswith(f"{model}_eval_")
        ]
    return sorted(members)


def load_run(setting: str, member: str) -> pd.DataFrame:
    with zipfile.ZipFile(SETTING_CONFIG[setting]["zip_path"]) as zf:
        with zf.open(member) as raw:
            return pd.read_csv(raw)


def build_failed_instances(gt: pd.DataFrame, algo: pd.DataFrame, model: str) -> pd.DataFrame:
    failed_mask = algo[model] == 0
    failed = gt.loc[failed_mask, ["Fold", "Index", *LABEL_COLS]].copy()
    failed["failed_instance_id"] = range(1, len(failed) + 1)
    return failed


def compute_model_summary(setting: str, gt: pd.DataFrame, algo: pd.DataFrame, model: str) -> tuple[pd.DataFrame, int]:
    failed = build_failed_instances(gt, algo, model)
    failed_count = len(failed)
    members = discover_run_members(setting, model)
    if len(members) != 7:
        raise ValueError(f"Expected 7 runs for {model} in {setting}, found {len(members)}")

    all_runs_rows = []
    for member in members:
        run_df = load_run(setting, member)
        pred_failed = failed[["failed_instance_id", "Fold", "Index"]].merge(
            run_df[["Fold", "Index", *LABEL_COLS]],
            on=["Fold", "Index"],
            how="left",
        )
        merged = failed.merge(
            pred_failed,
            on=["failed_instance_id", "Fold", "Index"],
            how="inner",
            suffixes=("_true", "_pred"),
        )
        if len(merged) != failed_count:
            raise ValueError(f"Run {member} does not align with failed instances for {model}.")

        for label in LABEL_COLS:
            all_runs_rows.append(
                pd.DataFrame(
                    {
                        "category": label,
                        "true": merged[f"{label}_true"].astype(int),
                        "pred": merged[f"{label}_pred"].astype(int),
                    }
                )
            )

    result_rows = []
    for label in LABEL_COLS:
        label_frames = [df for df in all_runs_rows if df["category"].iloc[0] == label]
        label_all = pd.concat(label_frames, ignore_index=True)
        positive = label_all["true"] == 1
        negative = label_all["true"] == 0
        false_negative_count = int(((label_all["true"] == 1) & (label_all["pred"] == 0)).sum())
        false_positive_count = int(((label_all["true"] == 0) & (label_all["pred"] == 1)).sum())
        positive_total = int(positive.sum())
        negative_total = int(negative.sum())

        result_rows.append(
            {
                "model": model,
                "failed_instances": failed_count,
                "category": label,
                "fnr_within_failed_instances": false_negative_count / positive_total if positive_total else 0.0,
                "fpr_within_failed_instances": false_positive_count / negative_total if negative_total else 0.0,
                "false_negative_count": false_negative_count,
                "false_positive_count": false_positive_count,
                "positive_total_across_failed_runs": positive_total,
                "negative_total_across_failed_runs": negative_total,
            }
        )

    return pd.DataFrame(result_rows), failed_count


def build_heatmap_matrix(summary: pd.DataFrame, value_col: str) -> pd.DataFrame:
    matrix = summary.pivot(index="model", columns="category", values=value_col).loc[MODELS, LABEL_COLS]
    matrix.index = [MODEL_LABELS[m] for m in matrix.index]
    matrix.columns = [f"{LABEL_SHORT[c]}\n({LABEL_CODES[c]})" for c in matrix.columns]
    return matrix


def plot_heatmap(matrix: pd.DataFrame, out_path: Path, cmap: str) -> None:
    values = matrix.to_numpy()
    fig, ax = plt.subplots(figsize=(12, 4.8))
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=1)

    ax.set_xticks(np.arange(matrix.shape[1]))
    ax.set_yticks(np.arange(matrix.shape[0]))
    ax.set_xticklabels(matrix.columns, rotation=30, ha="right", rotation_mode="anchor")
    ax.set_yticklabels(matrix.index)
    for tick in ax.get_xticklabels():
        tick.set_fontweight("bold")
        tick.set_color("black")
        tick.set_transform(tick.get_transform() + ScaledTranslation(10 / 72.0, 0, fig.dpi_scale_trans))
    for tick in ax.get_yticklabels():
        tick.set_fontweight("bold")
        tick.set_color("black")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = values[i, j]
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="black", fontsize=9, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("Rate")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    setting = args.setting
    gt = load_ground_truth(setting)
    algo = load_algorithm_bin(setting)

    summaries = []
    failure_counts = []
    for model in MODELS:
        model_summary, failed_count = compute_model_summary(setting, gt, algo, model)
        summaries.append(model_summary)
        failure_counts.append(
            {
                "model": model,
                "display_model": MODEL_LABELS[model],
                "failed_instances": failed_count,
                "failed_rate": failed_count / len(gt),
            }
        )

    summary = pd.concat(summaries, ignore_index=True)
    failure_counts_df = pd.DataFrame(failure_counts).sort_values(
        ["failed_instances", "model"], ascending=[False, True]
    ).reset_index(drop=True)

    fn_matrix = build_heatmap_matrix(summary, "fnr_within_failed_instances")
    fp_matrix = build_heatmap_matrix(summary, "fpr_within_failed_instances")

    out_dir = SETTING_CONFIG[setting]["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_dir / "category_fn_fp_summary.csv", index=False)
    failure_counts_df.to_csv(out_dir / "failure_counts.csv", index=False)
    fn_matrix.to_csv(out_dir / "fn_rate_matrix.csv")
    fp_matrix.to_csv(out_dir / "fp_rate_matrix.csv")

    plot_heatmap(
        fn_matrix,
        out_path=out_dir / "fn_heatmap.pdf",
        cmap="OrRd",
    )
    plot_heatmap(
        fp_matrix,
        out_path=out_dir / "fp_heatmap.pdf",
        cmap="Blues",
    )

    print(f"Setting: {setting}")
    print("Failure counts by model")
    print(failure_counts_df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print()
    print("FN rate matrix")
    print(fn_matrix.to_string(float_format=lambda x: f"{x:.2f}"))
    print()
    print("FP rate matrix")
    print(fp_matrix.to_string(float_format=lambda x: f"{x:.2f}"))
    print()
    print(f"Wrote: {out_dir / 'category_fn_fp_summary.csv'}")
    print(f"Wrote: {out_dir / 'failure_counts.csv'}")
    print(f"Wrote: {out_dir / 'fn_rate_matrix.csv'}")
    print(f"Wrote: {out_dir / 'fp_rate_matrix.csv'}")
    print(f"Wrote: {out_dir / 'fn_heatmap.pdf'}")
    print(f"Wrote: {out_dir / 'fp_heatmap.pdf'}")


if __name__ == "__main__":
    main()
