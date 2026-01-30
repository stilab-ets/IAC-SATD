# llm_crossval_runner/retriever/retriever_strategies/openai_precomputed.py
import faiss
import numpy as np


def l2_normalize(mat: np.ndarray) -> np.ndarray:
    mat = mat.astype("float32", copy=False)
    norms = np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12
    return mat / norms


def build_index_from_precomputed(embs: np.ndarray):
    """
    embs: [N, D] float32 (will be L2-normalized here just in case)
    Returns FAISS IndexFlatIP (cosine on normalized vectors).
    """
    embs = l2_normalize(embs.astype("float32", copy=False))
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs)
    return index


def search_with_query_vec(
        qvec: np.ndarray, index, train_texts, train_df, label_cols, top_k: int = 2
):
    """
    qvec: shape [D] or [1, D], NOT normalized (we'll normalize).
    """
    if qvec.ndim == 1:
        qvec = qvec[None, :]
    qvec = l2_normalize(qvec.astype("float32", copy=False))
    scores, idxs = index.search(qvec, top_k)

    out = []
    for r, idx in enumerate(idxs[0].tolist()):
        text = train_texts[idx]
        labels = train_df.iloc[idx][label_cols].values
        out.append((idx, float(scores[0][r]), text, labels))
    return out
