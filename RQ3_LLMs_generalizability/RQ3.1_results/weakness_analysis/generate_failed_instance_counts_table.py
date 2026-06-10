from __future__ import annotations

from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
ZERO_COUNTS_PATH = SCRIPT_DIR / "zero_shot_all_models_failed_instance_heatmaps" / "failure_counts.csv"
FEW_COUNTS_PATH = SCRIPT_DIR / "few_shots_all_models_failed_instance_heatmaps" / "failure_counts.csv"
OUT_CSV_PATH = SCRIPT_DIR / "failed_instance_counts_summary.csv"
OUT_TEX_PATH = SCRIPT_DIR / "failed_instance_counts_summary.tex"

MODEL_ORDER = ["ChatGPT", "Claude", "DeepSeek", "Gemini", "Gemma", "Qwen"]


def load_counts(path: Path, column_name: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[["display_model", "failed_instances"]].rename(
        columns={"display_model": "Model", "failed_instances": column_name}
    )


def build_summary() -> pd.DataFrame:
    zero = load_counts(ZERO_COUNTS_PATH, "Zero-shot failed instances")
    few = load_counts(FEW_COUNTS_PATH, "Few-shot failed instances")

    summary = zero.merge(few, on="Model", how="inner")
    summary["Change (few - zero)"] = (
        summary["Few-shot failed instances"] - summary["Zero-shot failed instances"]
    )
    summary["Succeeded instances in zero-shot"] = 680 - summary["Zero-shot failed instances"]
    summary["Succeeded instances in few-shot"] = 680 - summary["Few-shot failed instances"]

    summary["Model"] = pd.Categorical(summary["Model"], categories=MODEL_ORDER, ordered=True)
    summary = summary.sort_values("Model").reset_index(drop=True)
    summary["Model"] = summary["Model"].astype(str)
    return summary


def write_latex(summary: pd.DataFrame, out_path: Path) -> None:
    latex_df = summary.copy()
    latex_df["Change (few - zero)"] = latex_df["Change (few - zero)"].map(lambda x: f"{x:+d}")
    latex = latex_df.to_latex(index=False, escape=False)
    out_path.write_text(latex, encoding="utf-8")


def main() -> None:
    summary = build_summary()
    summary.to_csv(OUT_CSV_PATH, index=False)
    write_latex(summary, OUT_TEX_PATH)

    print(summary.to_string(index=False))
    print()
    print(f"Wrote: {OUT_CSV_PATH}")
    print(f"Wrote: {OUT_TEX_PATH}")


if __name__ == "__main__":
    main()
