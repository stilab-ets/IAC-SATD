from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import hamming_loss

# Expect these globals to be defined in the caller's module/environment
# (kept to preserve drop-in compatibility with your current code).


LABELS = [
    "Infrastructure Management Debt", "IaC Code Debt", "Dependency Management",
    "Security Debt", "Networking Debt", "Environment-Based Configuration Debt",
    "Monitoring and Logging Debt", "Test Debt"
]

ALLOWED_MODELS = {"chatgpt", "claude", "deepseek", "gemini", "gemma", "qwen"}


# ==========================
# Logging
# ==========================

def _setup_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(message)s",
        level=logging.INFO,
    )


# ==========================
# Loading helpers
# ==========================

def _load_ground_truth(gt_path: Path, labels: Sequence[str]) -> pd.DataFrame:
    logging.info("Loading ground truth from %s", gt_path)
    df = pd.read_csv(gt_path)
    required = {"Fold", "Index", "Prompt", *labels}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Ground truth missing required columns: {missing}")
    return df


def _load_spacy_td_or_none():
    """Return (nlp, td) or (None, None) if unavailable."""
    try:
        import spacy  # type: ignore
        import textdescriptives as td  # type: ignore
    except Exception as e:  # pragma: no cover
        logging.warning("spaCy/textdescriptives unavailable; continuing without text features: %s", e)
        return None, None

    try:
        nlp = spacy.load("en_core_web_lg")
    except Exception:
        logging.info("Falling back to en_core_web_sm spaCy model.")
        nlp = spacy.load("en_core_web_sm")

    try:
        nlp.add_pipe("textdescriptives/all")
    except Exception:
        try:
            nlp.add_pipe("textdescriptives")
        except Exception as e:  # pragma: no cover
            logging.warning("Could not add TextDescriptives; continuing without text features: %s", e)
            return None, None

    import textdescriptives as td  # type: ignore  # re-import for local scope
    return nlp, td


def _extract_text_features(nlp, td, prompts: Sequence[str]) -> pd.DataFrame:
    if nlp is None or td is None:
        logging.info("Skipping text features; creating empty feature frame.")
        return pd.DataFrame(index=range(len(prompts)))

    logging.info("Extracting TextDescriptives on prompts…")
    docs = list(nlp.pipe([str(p) for p in prompts]))
    feat_df = td.extract_df(docs, include_text=False).reset_index(drop=True)
    feat_df = feat_df.rename(columns=lambda c: f"feature_{c}")
    return feat_df


def _load_code_metrics(code_path: Path) -> Optional[pd.DataFrame]:
    if not code_path.exists():
        logging.info("code_metrics_dataset.csv not found; proceeding without code metrics.")
        return None
    try:
        logging.info("Loading code metrics from: %s", code_path)
        df = pd.read_csv(code_path)
        if not {"Fold", "Index"}.issubset(df.columns):
            logging.warning("code metrics missing Fold/Index; skipping merge.")
            return None
        feat_cols = [c for c in df.columns if c.startswith("feature_")]
        keep = ["Fold", "Index", *feat_cols]
        return df[keep].copy()
    except Exception as e:  # pragma: no cover
        logging.warning("Failed to load code metrics (%s); continuing without.", e)
        return None


# ==========================
# Data shaping helpers
# ==========================

def _build_base_df(
    gt_df: pd.DataFrame,
    text_feat_df: pd.DataFrame,
    code_metrics_df: Optional[pd.DataFrame],
    labels: Sequence[str],
) -> pd.DataFrame:
    base_df = pd.concat(
        [gt_df[["Fold", "Index", "Prompt", *labels]].reset_index(drop=True), text_feat_df],
        axis=1,
    )

    if code_metrics_df is not None and not code_metrics_df.empty:
        collisions = set(code_metrics_df.columns).intersection(set(base_df.columns)) - {"Fold", "Index"}
        if collisions:
            code_metrics_df = code_metrics_df.rename(columns={c: f"feature_code__{c}" for c in collisions})
        base_df = base_df.merge(code_metrics_df, on=["Fold", "Index"], how="left")
        logging.info("Merged code metrics (collisions renamed: %d).", len(collisions))

    # Drop problematic features if present
    to_drop = [c for c in ("feature_passed_quality_check", "feature_oov_ratio") if c in base_df.columns]
    if to_drop:
        base_df = base_df.drop(columns=to_drop, errors="ignore")

    # Add Instances (1 ... n) after Fold
    base_df.insert(1, "Instances", range(1, len(base_df) + 1))
    return base_df


def _discover_prediction_files(pred_dir: Path, allowed_models: Sequence[str]) -> List[Path]:
    files: List[Path] = []
    for p in sorted(pred_dir.glob("*.csv")):
        if "_eval_" not in p.name:
            continue
        model_core = p.name.split("_eval_")[0]
        if model_core in allowed_models:
            files.append(p)
    logging.info("Discovered %d prediction file(s) for allowed models.", len(files))
    return files


def _compute_losses_for_file(
    base_df: pd.DataFrame,
    labels: Sequence[str],
    csv_path: Path,
) -> Optional[Tuple[str, pd.DataFrame, float, float]]:
    """Compute per-instance and global Hamming loss for a single prediction CSV.

    Returns (model_core, run_df, mean_per_instance, global_loss) or None if skipped.
    """
    name = csv_path.name
    model_core = name.split("_eval_")[0]

    pred_df = pd.read_csv(csv_path)
    required = {"Fold", "Index", *labels}
    missing = [c for c in required if c not in pred_df.columns]
    if missing:
        logging.warning("%s missing columns %s. Skipping.", name, missing)
        return None

    merged = base_df[["Fold", "Index", *labels]].merge(
        pred_df[["Fold", "Index", *labels]], on=["Fold", "Index"], how="inner", suffixes=("", "__pred")
    )
    if merged.empty:
        logging.warning("No overlapping rows after merge for %s. Skipping.", name)
        return None

    y_true = merged[list(labels)].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int).to_numpy()
    y_pred = (
        merged[[f"{lab}__pred" for lab in labels]].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int).to_numpy()
    )

    per_instance = np.array([hamming_loss(y_true[i], y_pred[i]) for i in range(y_true.shape[0])])
    run_df = pd.DataFrame({"Fold": merged["Fold"].values, "Index": merged["Index"].values, "loss": per_instance})

    mean_pi = float(per_instance.mean())
    global_loss = float(hamming_loss(y_true, y_pred))
    return model_core, run_df, mean_pi, global_loss


def _aggregate_and_merge_losses(
    base_df: pd.DataFrame,
    losses_by_model: Mapping[str, List[pd.DataFrame]],
    run_counts: Mapping[str, int],
) -> pd.DataFrame:
    out_df = base_df.copy()
    for model_core, df_list in losses_by_model.items():
        concat_runs = pd.concat(df_list, ignore_index=True)
        avg_loss = (
            concat_runs.groupby(["Fold", "Index"], as_index=False)["loss"].mean().rename(columns={"loss": f"algo_{model_core}"})
        )
        out_df = out_df.merge(avg_loss, on=["Fold", "Index"], how="left")
        logging.info("✅ %s: averaged over %d run(s)", model_core, run_counts.get(model_core, 0))
    return out_df


def _reorder_columns(df: pd.DataFrame, labels: Sequence[str]) -> pd.DataFrame:
    meta_cols = ["Fold", "Instances", "Index", "Prompt"]
    feature_cols = [c for c in df.columns if c.startswith("feature_")]
    gt_cols = list(labels)
    algo_cols = [c for c in df.columns if c.startswith("algo_")]

    final = [c for c in (meta_cols + feature_cols + gt_cols + algo_cols) if c in df.columns]
    return df[final]


def _write_output(df: pd.DataFrame, out_dir: Path) -> Path:
    out_path = out_dir / "metadata.csv"
    df.to_csv(out_path, index=False)
    logging.info("📄 Wrote: %s", out_path)
    return out_path


# ==========================
# Orchestrator (public API)
# ==========================

def evaluate_hamming_by_model(
    ground_truth_path: str,
    prediction_folder: str,
    output_folder: str,
    code_metrics_path: str = "code_metrics_dataset.csv",
) -> pd.DataFrame:
    """Split, testable refactor of the evaluator with the same behavior and signature.

    Returns the final DataFrame and writes <output_folder>/metadata.csv.
    """
    _setup_logging()

    out_dir = Path(output_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    gt_df = _load_ground_truth(Path(ground_truth_path), LABELS)
    nlp, td = _load_spacy_td_or_none()
    text_feat_df = _extract_text_features(nlp, td, gt_df["Prompt"].astype(str))
    code_df = _load_code_metrics(Path(code_metrics_path))

    base_df = _build_base_df(gt_df, text_feat_df, code_df, LABELS)

    pred_dir = Path(prediction_folder)
    if not pred_dir.exists():
        raise FileNotFoundError(f"Prediction folder not found: {pred_dir}")

    losses_by_model: Dict[str, List[pd.DataFrame]] = defaultdict(list)
    run_counts: Dict[str, int] = defaultdict(int)

    for pred_csv in _discover_prediction_files(pred_dir, ALLOWED_MODELS):
        result = _compute_losses_for_file(base_df, LABELS, pred_csv)
        if result is None:
            continue
        model_core, run_df, mean_pi, global_loss = result
        logging.info("🧮 %s | %s: mean per-instance=%.4f | global=%.4f", model_core, pred_csv.name, mean_pi, global_loss)
        losses_by_model[model_core].append(run_df)
        run_counts[model_core] += 1

    final_df = _aggregate_and_merge_losses(base_df, losses_by_model, run_counts)
    final_df = _reorder_columns(final_df, LABELS)

    _write_output(final_df, out_dir)
    return final_df


if __name__ == "__main__":

    evaluate_hamming_by_model(
        # TODO: Change to "./ground_truth_zero.csv" in the case of Zero Shot Experiments
        ground_truth_path = "./ground_truth_few.csv",

        # TODO: Change to "../../RQ2_LLMs_ML_experiments/llms_predictions_zero_shot" in the case of zero shot experiments
        prediction_folder = "../../RQ2_LLMs_ML_experiments/LLM_predictions/llms_predictions_few_shots",

        # TODO: Change to "./evaluation_details_hamming_zero_shot"
        output_folder = "./evaluation_details_hamming_few_shots",

        code_metrics_path = "./code_metrics_dataset.csv"
    )

