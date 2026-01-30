import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


NAME_MAP = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "deepseek": "DeepSeek",
    "gemini": "Gemini",
    "gemma": "Gemma",
    "qwen": "Qwen",
}


def load_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def rename_models(df: pd.DataFrame, name_map: dict) -> pd.DataFrame:
    # Rename only columns that exist
    rename_dict = {k: v for k, v in name_map.items() if k in df.columns}
    return df.rename(columns=rename_dict)


def get_model_columns(df: pd.DataFrame, id_cols=("row",)) -> list[str]:
    id_cols_lower = {c.lower() for c in id_cols}
    return [c for c in df.columns if c.lower() not in id_cols_lower]


def compute_intersection_matrix(df: pd.DataFrame, model_cols: list[str]) -> np.ndarray:
    """
    intersection[i, j] = #instances correctly predicted by BOTH model i and model j
    diagonal will later be overwritten with total correct per model.
    """
    n = len(model_cols)
    intersection = np.zeros((n, n), dtype=int)

    # Precompute boolean correct vectors once
    correct = {m: (df[m] == 1).to_numpy() for m in model_cols}

    for i, m1 in enumerate(model_cols):
        for j, m2 in enumerate(model_cols):
            intersection[i, j] = int(np.sum(correct[m1] & correct[m2]))

    return intersection


def compute_correct_and_unique(df: pd.DataFrame, model_cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """
    correct_per_model[i] = total correct of model i
    unique_diag[i] = #instances ONLY model i got correct (all others wrong)
    """
    n = len(model_cols)
    correct = {m: (df[m] == 1).to_numpy() for m in model_cols}

    correct_per_model = np.array([int(np.sum(correct[m])) for m in model_cols], dtype=int)
    unique_diag = np.zeros(n, dtype=int)

    if n == 1:
        # Only one model: all its correct are unique
        unique_diag[0] = correct_per_model[0]
        return correct_per_model, unique_diag

    for i, m in enumerate(model_cols):
        others = [correct[om] for j, om in enumerate(model_cols) if j != i]
        others_correct = np.logical_or.reduce(others)
        unique_diag[i] = int(np.sum(correct[m] & ~others_correct))

    return correct_per_model, unique_diag


def mask_lower_triangle(mat: np.ndarray) -> tuple[np.ma.MaskedArray, np.ndarray]:
    mask = np.tril(np.ones_like(mat, dtype=bool), k=-1)
    return np.ma.array(mat, mask=mask), mask


def build_colormap(colors: list[str]) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list("custom_cmap", colors)


def plot_heatmap(
    mat_masked: np.ma.MaskedArray,
    mask: np.ndarray,
    model_cols: list[str],
    correct_per_model: np.ndarray,
    unique_diag: np.ndarray,
    cmap: LinearSegmentedColormap,
    colorbar_label: str = "Correct Classification Count",
    out_pdf: str = "heatmap.pdf",
) -> None:
    n = len(model_cols)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(mat_masked, cmap=cmap)

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(model_cols, rotation=20, ha="right", fontsize=12, fontweight="bold")
    ax.set_yticklabels(model_cols, fontsize=12, fontweight="bold")

    # Annotate values
    for i in range(n):
        for j in range(n):
            if mask[i, j]:
                continue  # lower triangle hidden

            if i == j:
                text = f"{correct_per_model[i]}\n(U:{unique_diag[i]})"
            else:
                text = f"{int(mat_masked.data[i, j])}"

            ax.text(j, i, text, ha="center", va="center", fontsize=18, fontweight="bold", color="black")

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.ax.tick_params(labelsize=15, width=1)
    cbar.ax.set_ylabel(colorbar_label, fontsize=22, fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_pdf, format="pdf", bbox_inches="tight")
    # plt.show()
    plt.close(fig)

def main():
    # Change path as needed
    # fp = "../../ISA_application/evaluation_details_hamming_few_shots/algorithm_bin.csv"
    fp = "../../ISA_application/evaluation_details_hamming_zero_shot/algorithm_bin.csv"

    df = load_data(fp)
    df = rename_models(df, NAME_MAP)

    model_cols = get_model_columns(df, id_cols=("row",))
    if not model_cols:
        raise ValueError("No model columns found. Check your CSV header.")

    intersection = compute_intersection_matrix(df, model_cols)
    correct_per_model, unique_diag = compute_correct_and_unique(df, model_cols)

    # Replace diagonal with total correct per model (as in your original logic)
    for i in range(len(model_cols)):
        intersection[i, i] = correct_per_model[i]

    masked_intersection, mask = mask_lower_triangle(intersection)

    # Your orange palette
    colors = ["#fff5cc", "#ffdd99", "#ffbf66", "#ff9933", "#ff6600"]
    cmap = build_colormap(colors)

    # Output name based on which file you used
    out_pdf = "heatmap_few_shots.pdf" if "few_shots" in fp else "heatmap_zero_shot.pdf"

    plot_heatmap(
        mat_masked=masked_intersection,
        mask=mask,
        model_cols=model_cols,
        correct_per_model=correct_per_model,
        unique_diag=unique_diag,
        cmap=cmap,
        out_pdf=out_pdf,
    )


if __name__ == "__main__":
    main()
