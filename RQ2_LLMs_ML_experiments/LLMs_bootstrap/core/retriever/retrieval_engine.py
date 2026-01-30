# llm_crossval_runner/retriever/retrieval_engine.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import gc, torch

from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.retriever.retriever_strategies.openai_precomputed import (
    search_with_query_vec, l2_normalize,
)

ResultT = List[Tuple[int, float, str, list[int]]]

class RetrievalEngine:
    __slots__ = ("mode", "c")

    def __init__(self, mode: str, **components: Any):
        self.mode = (mode or "none").lower()
        self.c: Dict[str, Any] = components

    def retrieve(self, query_triplet, train_df, label_cols, *,
                 top_k_final=2, k_bm25=200, k_dense=60, rrf_k=60,
                 # NEW: optional precomputed query vector
                 query_vec=None) -> ResultT:
        if self.mode == "none":
            return []

        if self.mode == "openai_precomputed":
            idx, texts, test_embs = self.c.get("dense_index"), self.c.get("train_texts") or [], self.c.get("openai_test_embs")
            if not (idx and texts and test_embs is not None and query_vec is not None): return []
            return search_with_query_vec(query_vec, idx, texts, train_df, label_cols, top_k=top_k_final)

        return []

    def free(self) -> None:
        for mkey in ("q_enc", "d_enc", "st_model"):
            m = self.c.get(mkey)
            if m is not None:
                try:
                    m.to("cpu"); del m
                except Exception:
                    pass
        if "dense_index" in self.c: del self.c["dense_index"]
        if "faiss_index" in self.c: del self.c["faiss_index"]
        self.c.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    @classmethod
    def from_bundle(cls, retrieval: Dict[str, Any] | None) -> "RetrievalEngine":
        retrieval = retrieval or {}
        mode = (retrieval.get("mode") or "none").lower()
        comps = {k: v for k, v in retrieval.items() if k != "mode"}
        return cls(mode, **comps)
