# run_rag_from_files.py
import os
import time

import pandas as pd

from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.main import LABELS
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.utils import save_row_to_csv, save_row_prompt
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.retriever.retriever_strategies.builder import make_retrieval, free_retrieval_bundle
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.retriever.retrieval_engine import RetrievalEngine

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _openai_paths(project_root: str, fold: int, tag: str = "openai__text-embedding-3-small"):
    emb_dir = os.path.join(project_root, "embed", "embeddings_cache")
    train_path = os.path.join(emb_dir, f"stratified_cleaned_train_fold_{fold}_revised__{tag}__embeddings.npy")
    test_path = os.path.join(emb_dir, f"stratified_cleaned_test_fold_{fold}_revised__{tag}__embeddings.npy")
    return train_path, test_path


def _maybe_openai_kwargs(retrieval_mode: str, fold: int):
    if retrieval_mode in ("openai_precomputed", "rrf_fusion_openai_precomputed"):
        train_p, test_p = _openai_paths(PROJECT_ROOT, fold)
        return {"openai_train_emb_path": train_p, "openai_test_emb_path": test_p}
    return {}


def _maybe_query_vec(engine: RetrievalEngine, i: int, retrieval_mode: str):
    if retrieval_mode in ("openai_precomputed", "rrf_fusion_openai_precomputed"):
        test_embs = engine.c.get("openai_test_embs")
        return None if test_embs is None else test_embs[i]
    return None


def run_rag_from_files_new_runners(
        model,
        folds_dir: str,
        output_path: str,
        labels: list,
        num_folds: int = 5,
        default_retrieval_mode: str = "dpr",
        only_indices=None,  # NEW: retry only these indices (per fold)
        is_prompt_generation_only=False  # NEW: if True, fresh file instead of append
):
    # MAX_RETRIES = 5
    folds_dir = os.path.join(PROJECT_ROOT, folds_dir)
    retrieval_mode = getattr(model, "retrieval_mode", default_retrieval_mode)

    for fold in range(num_folds):

        # Skip folds not in the failed set
        if only_indices and not any(f == fold for f, _ in only_indices):
            continue

        train_fp = os.path.join(folds_dir, f"stratified_cleaned_train_fold_{fold}.csv")
        test_fp = os.path.join(folds_dir, f"stratified_cleaned_test_fold_{fold}.csv")
        train_df = pd.read_csv(train_fp)
        test_df = pd.read_csv(test_fp)

        print('starting making retrieval')

        # ✅ 1) Build the component bundle (inject OpenAI .npy paths only if needed)
        retrieval = make_retrieval(
            retrieval_mode,
            train_df,
            **_maybe_openai_kwargs(retrieval_mode, fold)  # <—<—<— important for openai_* modes
        )

        # 2) Wrap it with the engine
        engine = RetrievalEngine.from_bundle(retrieval)

        for i, row in test_df.iterrows():
            if only_indices and (fold, i) not in only_indices:
                continue
            # ✅ NEW: provide query_vec for precomputed-OpenAI modes
            query_vec = _maybe_query_vec(engine, i, retrieval_mode)

            result, response, prompt = model.rag_implementation_for_single_prompts(
                train_data=train_df,
                comment=row["SATD Comment"],
                context=row["context"],
                code_block=row["bloc of first occurrence"],
                labels=LABELS,
                retrieval_engine=engine,  # <—<— pass the engine
                query_vec=query_vec,  # <—<— None for non-openai modes
                generate_prompt_only=is_prompt_generation_only
            )

            if is_prompt_generation_only:
                save_row_prompt(output_path, fold, i, row, labels, prompt)
                print(f"✅ Fold {fold} Row {i} processed successfully.")

            else:
                label_flags = [1 if f"CAT{j + 1}" in response else 0 for j in range(len(labels))]
                predicted = [labels[j] for j, v in enumerate(label_flags) if v == 1]

                save_row_to_csv(output_path, fold, i, row, response, label_flags, predicted, labels)
                print(f"✅ Fold {fold} Row {i} processed successfully.")
                time.sleep(3)

        # 3) Free GPU/FAISS
        engine.free()
        free_retrieval_bundle(retrieval)
