import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from ESDTests import generate_sk_rank

METRICS = ["precision", "recall", "f1-score"]


# -----------------------------
# Scenario configuration
# -----------------------------
@dataclass(frozen=True)
class Scenario:
    """
    name: Used to build output folder names and merged filenames.
    input_csv: Path to the dataset that provides the labels to iterate over.
    per_label_root: Root folder that contains per-label metric files.
                   We expect: <per_label_root>/<label>/<metric>_separated.txt
    merged_root: Where merged outputs should be saved.
    """
    name: str
    input_csv: Path
    per_label_root: Path
    merged_root: Path


def sanitize_label(label: str) -> str:
    return label.strip().replace(" ", "_").replace("/", "_")


def read_labels(input_csv: Path) -> np.ndarray:
    df = pd.read_csv(input_csv)
    if "label" not in df.columns:
        raise ValueError(f"'label' column not found in {input_csv}")
    return df["label"].dropna().unique()


def enrich_with_summary_stats(metric_file: Path, df_sk: pd.DataFrame) -> pd.DataFrame:
    df_raw = pd.read_csv(metric_file, sep=r"\s+", header=None)
    if df_raw.shape[1] < 2:
        raise ValueError(f"Metric file has no score columns: {metric_file}")

    df_raw.columns = ["model"] + [f"s{i}" for i in range(1, df_raw.shape[1])]
    score_cols = [c for c in df_raw.columns if c != "model"]

    df_raw["mean"] = df_raw[score_cols].mean(axis=1)
    df_raw["median"] = df_raw[score_cols].median(axis=1)
    df_raw["iqr"] = df_raw[score_cols].apply(
        lambda row: np.percentile(row, 75) - np.percentile(row, 25),
        axis=1
    )

    return df_sk.merge(df_raw[["model", "mean", "median", "iqr"]], on="model", how="left")


def run_scenario(scn: Scenario) -> None:
    if not scn.input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {scn.input_csv}")

    scn.merged_root.mkdir(parents=True, exist_ok=True)

    labels = read_labels(scn.input_csv)
    merged_results: dict[str, list[pd.DataFrame]] = {m: [] for m in METRICS}

    for label in labels:
        print(f"\n🔎 Processing label: {label}")
        label_dir = scn.per_label_root / sanitize_label(label)

        for metric in METRICS:
            metric_file = label_dir / f"{metric}_separated.txt"
            if not metric_file.exists():
                print(f"⚠️ Missing file: {metric_file}")
                continue

            print(f"  ➤ Analyzing: {metric_file}")
            try:
                # your existing function
                df_sk = generate_sk_rank(str(metric_file), metric)

                df_enriched = enrich_with_summary_stats(metric_file, df_sk)
                df_enriched.insert(0, "label", label)

                # Save per-label enriched output
                out_csv = label_dir / f"{metric}_sk_rank.csv"
                df_enriched.to_csv(out_csv, index=False)
                print(f"  ✅ Saved: {out_csv}")

                merged_results[metric].append(df_enriched)

            except Exception as e:
                print(f"  ❌ Error processing {metric_file}: {e}")

    # Merge per metric
    for metric, dfs in merged_results.items():
        if not dfs:
            print(f"\n⚠️ No data available to merge for metric: {metric}")
            continue

        merged_df = pd.concat(dfs, ignore_index=True)
        merged_path = scn.merged_root / f"merged_{metric}_sk_ranks_{scn.name}.csv"
        merged_df.to_csv(merged_path, index=False)
        print(f"\n📦 Merged result saved to: {merged_path}")


# -----------------------------
# Scenario builders
# -----------------------------
def scenario_zero_shot_vs_ml_baselines() -> Scenario:
    """
    Case 1: Zero-shot vs ML baselines (no vector).
    Adjust folder names to match your repo.
    """
    name = "zero_shot_vs_ml_baselines"

    input_csv = Path("./performance_analysis/zero_shot_vs_ml_baselines.csv")
    per_label_root = Path("./performance_analysis/data_transformer/output_by_label/zero_shot_vs_ml_baselines")
    merged_root = Path("./performance_analysis/grouped/zero_shot_vs_ml_baselines")

    return Scenario(name=name, input_csv=input_csv, per_label_root=per_label_root, merged_root=merged_root)


def scenario_few_shots_vs_zero_shot() -> Scenario:
    # vector: str
    """
    Case 2: Few-shots vs Zero-shot (vector-specific).
    """
    name = f"few_shots_vs_zero_shot"
    # {vector}_

    input_csv = Path(f"./performance_analysis/few_shots_vs_zero_shot.csv")
    # {vector}_
    per_label_root = Path(f"./performance_analysis/data_transformer/output_by_label/few_shots_vs_zero_shot")
    # {vector}_
    merged_root = Path(f"./performance_analysis/grouped/few_shots_vs_zero_shot")
    # {vector}_

    return Scenario(name=name, input_csv=input_csv, per_label_root=per_label_root, merged_root=merged_root)


# -----------------------------
# Entrypoint
# -----------------------------
if __name__ == "__main__":
    random.seed(1)

    # # ---- Run Case 1 (Zero shot)
    # run_scenario(scenario_zero_shot_vs_ml_baselines())

    # ---- Run Case 2 (Few shot)
    run_scenario(scenario_few_shots_vs_zero_shot())

