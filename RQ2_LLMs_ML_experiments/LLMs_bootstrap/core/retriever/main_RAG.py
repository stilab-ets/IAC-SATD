# main_RAG.py
import os

import pandas as pd

from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.api_key_management import APIKeyManager
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.chagpt_model import ChatGPTModel
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.claude_model import ClaudeModel
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.gemini_model import GeminiModel
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.gemma_model import GemmaModel
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.open_router_model import OpenRouterModel
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.qween import QwenModel
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.retriever.new_rag_runner import run_rag_from_files_new_runners

LABELS = [
    "Computing Management Debt",
    "IaC Code Debt",
    "Dependency Management",
    "Security Debt",
    "Networking Debt",
    "Environment-Based Configuration Debt",
    "Monitoring and Logging Debt",
    "Test Debt"
]

GEMINI_KEYS = [
    os.environ.get("GEMINI_KEY_1", "YOUR_KEY_1"),
    os.environ.get("GEMINI_KEY_2", "YOUR_KEY_2"),
    os.environ.get("GEMINI_KEY_3", "YOUR_KEY_3"),
]

gemini_key_manager = APIKeyManager(api_keys=GEMINI_KEYS, rate_limit=10, time_window=90)


def build_output_path(project_root: str, model_key: str, temperature: float, retrieval_mode: str) -> str:
    """
    Save results in a subfolder based on retrieval mode.
    Example:
      results/rag_dpr_tests/gemma_eval_v11_tmp_0.3_rag_dpr.csv
    """
    mode_map = {
        "mpnet_dense": "rag_mpnet_dense",
        "dpr": "rag_dpr",
        "rrf_fusion_mpnet": "rag_rrf_bm25_mpnet",
        "rrf_fusion_dpr": "rag_rrf_bm25_dpr",
    }
    mode_label = mode_map.get((retrieval_mode or "none").lower(), f"rag_{retrieval_mode}")

    folder_name = f"{mode_label}_tests"
    tmp_str = f"{temperature:.2f}".rstrip("0").rstrip(".") or "0"

    filename = f"{model_key}_eval_v11_tmp_{tmp_str}_{mode_label}.csv"

    results_dir = os.path.join(project_root, "core", "results", folder_name)
    os.makedirs(results_dir, exist_ok=True)
    return os.path.join(results_dir, filename)


def get_model(model_key, temperature):
    if model_key == "gemini":
        return GeminiModel(gemini_key_manager)

    elif model_key == "deepseek":
        return OpenRouterModel(api_key=os.environ.get("OPENROUTER_API_KEY", "YOUR_KEY"), model_name="deepseek/deepseek-chat-v3-0324", temperature=temperature)
    elif model_key == "claude":
        return ClaudeModel(api_key=os.environ.get("CLAUDE_API_KEY", "YOUR_KEY"), temperature=temperature)
    elif model_key == "chatgpt":
        return ChatGPTModel(api_key=os.environ.get("OPENAI_API_KEY", "YOUR_KEY"), temperature=temperature)
    elif model_key == "qwen":
        return QwenModel(temperature=temperature)
    elif model_key == "gemma":
        return GemmaModel(temperature=temperature)
    else:
        raise ValueError(f"Model {model_key} not found.")


def retry_failed_instances(model, folds_dir, output_path, labels, retrieval_mode):
    if not os.path.exists(output_path):
        print(f"[RETRY] No file found: {output_path}")
        return

    df = pd.read_csv(output_path)

    # Identify failed rows
    failed = []
    for _, row in df.iterrows():
        response = str(row.get("Response", "")).strip()
        if response in ("", "ERROR", "NaN", "nan", "None"):
            failed.append((row["Fold"], row["Index"]))  # assumes Fold + Index exist

    if not failed:
        print("[RETRY] No failed rows to retry.")
        return

    print(f"[RETRY] Retrying {len(failed)} rows...")
    # print("failed:", failed, set(failed))

    # Temp file for retried rows
    tmp_file = output_path.replace(".csv", "__retry.csv")

    run_rag_from_files_new_runners(
        model=model,
        folds_dir=folds_dir,
        output_path=tmp_file,
        labels=labels,
        num_folds=5,
        default_retrieval_mode=retrieval_mode,
        only_indices=set(failed),  # retry only failed
        overwrite=True
    )

    refreshed = pd.read_csv(tmp_file)

    # --- Update df safely using MultiIndex on (Fold, Index)
    df = df.set_index(["Fold", "Index"])
    df = df[~df.index.duplicated(keep="last")]

    refreshed = refreshed.set_index(["Fold", "Index"])
    refreshed = refreshed[~refreshed.index.duplicated(keep="last")]

    # Overwrite only matching cells
    df.update(refreshed)

    # Restore normal index
    df.reset_index(inplace=True)

    df.to_csv(output_path, index=False)
    print(f"[RETRY] Updated {len(refreshed)} rows in {output_path}")


def build_ground_truth_output_path(project_root: str) -> str:
    """
    Build a standardized path for saving a single ground-truth prompt or inference result.

    Example output:
      llm_crossval_runner/results/ground_truth/ground_truth_rags.csv
    """
    # Ensure the ground_truth folder exists
    groundtruth_dir = os.path.join(
        project_root, "llm_crossval_runner", "results", "ground_truth"
    )
    os.makedirs(groundtruth_dir, exist_ok=True)

    # Construct a descriptive file name
    filename = f"ground_truth_rags.csv"

    # Full path
    return os.path.join(groundtruth_dir, filename)


if __name__ == '__main__':
    selected_model_key = "claude"  # 🔁 Change as needed 🔁
    retrieval_mode = "openai_precomputed"  # 🔁 Change retrieval mode here 🔁
    is_prompt_generation_only = True

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    folds_dir = os.path.join(PROJECT_ROOT, "RQ2_LLMs_ML_experiments", "Data_Splitting", "stratified_cleaned_folds")

    for temp in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        print(f"🔁 Running {selected_model_key} with temp={temp}, retrieval={retrieval_mode}")
        model = get_model(selected_model_key, temperature=temp)

        if is_prompt_generation_only:
            output_path = build_ground_truth_output_path(PROJECT_ROOT)
        else:
            output_path = build_output_path(PROJECT_ROOT, selected_model_key, temp, retrieval_mode)

        run_rag_from_files_new_runners(
            model=model,
            folds_dir=folds_dir,
            output_path=output_path,
            labels=LABELS,
            num_folds=5,
            default_retrieval_mode=retrieval_mode,
            is_prompt_generation_only=is_prompt_generation_only
        )

        # 🔁 NEW: in-depth retry step
        # retry_failed_instances(model, folds_dir, output_path, LABELS, retrieval_mode)
