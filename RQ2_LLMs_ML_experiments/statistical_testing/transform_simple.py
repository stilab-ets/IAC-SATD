# import pandas as pd
# import os
#
# # === Configuration ===
# # input_csv = '../../performance_analysis/rag_llms_vs_zero_shot_llms_main_metrics.csv'
# # output_dir = './output_by_label/rag_vs_zero_shot_comparison'
# # input_csv = '../performance_analysis/zero_shot_vs_ml_baselines.csv'
# # output_dir = './output_by_label/new_baseline_comparisons'
# # input_csv = '../performance_analysis/zero_vs_shot_comparison.csv'
#
#
# def transform_to_tim_representation(vectorized_type):
#
#     input_csv = f'../performance_analysis/vectors/{vectorized_type}_vs_zero_shots.csv'
#     output_dir = f'./output_by_label/vector_{vectorized_type}_vs_zero_shots'
#     metrics = ['precision', 'recall', 'f1-score']
#
#     # Create output root directory
#     os.makedirs(output_dir, exist_ok=True)
#
#
#     # Load dataset
#     df = pd.read_csv(input_csv)
#
#     # Get all unique labels
#     labels = df['label'].unique()
#
#     # Iterate over labels and metrics
#     for label in labels:
#         print(f"\n🔎 Processing label: {label}")
#         label_sanitized = label.replace(' ', '_')
#         label_dir = os.path.join(output_dir, label_sanitized)
#         os.makedirs(label_dir, exist_ok=True)
#
#         for metric in metrics:
#             print(f"  ➤ Metric: {metric}")
#
#             # Filter for current label
#             df_label = df[df['label'] == label]
#
#             # Pivot: one row per model, values as list
#             pivot_df = df_label.pivot_table(index='model', values=metric, aggfunc=list)
#
#             # Expand list into columns
#             wide_df = pivot_df[metric].apply(pd.Series)
#
#             # Generate space-separated format (no header)
#             lines = []
#             for model, row in wide_df.iterrows():
#                 values = [str(v) for v in row if pd.notnull(v)]
#                 lines.append(model + " " + " ".join(values))
#
#             # Save space-separated file (no header)
#             space_txt_path = os.path.join(label_dir, f"{metric}_separated.txt")
#             with open(space_txt_path, 'w') as f:
#                 f.write("\n".join(lines))
#
#     print("\n✅ All metrics processed and files generated (without headers).")
#
#
# if __name__ == '__main__':
#
#     vectorized_types = [
#                         # "rag_dpr",
#                         # "rag_mpnet_dense",
#                         "rag_openai_precomputed",
#                         # "rag_rrf_bm25_mpnet",
#                         # "rag_rrf_fusion_openai_precomputed"
#                         # "rag_rrf_bm25_dpr",
#     ]
#
#     for vec in vectorized_types:
#         transform_to_tim_representation(vec)
import os
from pathlib import Path
import pandas as pd

METRICS = ["precision", "recall", "f1-score"]


def sanitize_label(label: str) -> str:
    return str(label).strip().replace(" ", "_").replace("/", "_")


def transform_to_tim_representation(input_csv: str, output_dir: str) -> None:
    input_csv = Path(input_csv)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_csv)
    if "label" not in df.columns or "model" not in df.columns:
        raise ValueError("CSV must contain at least 'label' and 'model' columns.")

    labels = df["label"].dropna().unique()

    for label in labels:
        print(f"\n🔎 Processing label: {label}")
        label_dir = output_dir / sanitize_label(label)
        label_dir.mkdir(parents=True, exist_ok=True)

        df_label = df[df["label"] == label]

        for metric in METRICS:
            if metric not in df_label.columns:
                print(f"⚠️ Metric column missing in CSV: {metric}")
                continue

            pivot_df = df_label.pivot_table(index="model", values=metric, aggfunc=list)
            wide_df = pivot_df[metric].apply(pd.Series)

            lines = []
            for model, row in wide_df.iterrows():
                values = [str(v) for v in row if pd.notnull(v)]
                if values:
                    lines.append(model + " " + " ".join(values))

            metric_path = label_dir / f"{metric}_separated.txt"
            metric_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"  ✅ Saved: {metric_path}")

    print("\n✅ Done: TIM separated files generated per label.")


if __name__ == "__main__":

    # -----------------------------
    # Case A: Zero-shot vs ML baselines (no vector)
    # -----------------------------
    # transform_to_tim_representation(
    #     input_csv="./performance_analysis/zero_shot_vs_ml_baselines.csv",
    #     output_dir="./performance_analysis/data_transformer/output_by_label/zero_shot_vs_ml_baselines",
    # )

    # -----------------------------
    # Case B: Few-shots vs Zero-shot
    # Choose ONE of the following patterns:
    # -----------------------------

    # (B1) Single file (no vector)
    transform_to_tim_representation(
        input_csv="./performance_analysis/few_shots_vs_zero_shot.csv",
        output_dir="./performance_analysis/data_transformer/output_by_label/few_shots_vs_zero_shot",
    )
