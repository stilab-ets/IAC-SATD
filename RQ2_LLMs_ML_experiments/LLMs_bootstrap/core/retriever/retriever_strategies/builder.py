import gc
import torch
import pandas as pd
import numpy as np
from typing import Dict, Any
from pathlib import Path

from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.retriever.retriever_strategies.openai_precomputed import (
    build_index_from_precomputed,
)


def build_train_texts(train_df: pd.DataFrame):
    return (
            train_df["SATD Comment"].astype(str).fillna("") + " [SEP] " +
            train_df["context"].astype(str).fillna("") + " [SEP] " +
            train_df["bloc of first occurrence"].astype(str).fillna("")
    ).tolist()


def free_cuda():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()


def free_retrieval_bundle(retrieval: Dict[str, Any]):
    if not retrieval:
        return
    for mkey in ("q_enc", "d_enc", "st_model"):
        m = retrieval.get(mkey)
        if m is not None:
            try:
                m.to("cpu");
                del m
            except Exception:
                pass
    if "dense_index" in retrieval: del retrieval["dense_index"]
    if "faiss_index" in retrieval: del retrieval["faiss_index"]
    retrieval.clear()
    free_cuda()


def _load_npy(path: str | Path) -> np.ndarray:
    arr = np.load(str(path))
    if arr.dtype != np.float32:
        arr = arr.astype("float32")
    return arr


def make_retrieval(
        mode: str,
        train_df: pd.DataFrame,
        *,
        mpnet_model_name: str = "multi-qa-mpnet-base-dot-v1",
        # NEW: precomputed OpenAI embeddings (full paths)
        openai_train_emb_path: str | None = None,
        openai_test_emb_path: str | None = None,
) -> Dict[str, Any]:
    """
    Supported modes:
      - "mpnet_dense"
      - "dpr"
      - "rrf_fusion_mpnet"
      - "rrf_fusion_dpr"
      - "openai_precomputed"               (NEW)
      - "rrf_fusion_openai_precomputed"    (NEW)
    """
    retrieval: Dict[str, Any] = {"mode": mode}
    train_texts = build_train_texts(train_df)

    # ---------- NEW: OpenAI precomputed ----------
    if mode == "openai_precomputed":
        if not openai_train_emb_path or not openai_test_emb_path:
            raise ValueError("[builder] openai_precomputed requires openai_train_emb_path and openai_test_emb_path")
        train_embs = _load_npy(openai_train_emb_path)
        dense_index = build_index_from_precomputed(train_embs)
        test_embs = _load_npy(openai_test_emb_path)  # kept for queries
        retrieval.update({
            "dense_index": dense_index,
            "train_texts": train_texts,
            "openai_test_embs": test_embs,  # Runner/engine will pick per-row vector
        })
        print(f"[builder] OpenAI-precomputed retriever built.\n"
              f"          train_embs={train_embs.shape}, test_embs={test_embs.shape}")
        return retrieval


    raise ValueError(
        "Unknown mode (use 'mpnet_dense','dpr','rrf_fusion_mpnet','rrf_fusion_dpr',"
        "'openai_precomputed','rrf_fusion_openai_precomputed')"
    )
