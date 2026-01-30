import pandas as pd

### -------- 1. Load and preprocess both CSVs --------


if __name__ == '__main__':

    # Update these paths
    csv_zero_shot = "../../ISA_application/evaluation_details_hamming_zero_shot/footprint_performance.csv"
    csv_few = "../../ISA_application/evaluation_details_hamming_few_shots/footprint_performance.csv"

    ### -------- 1. Load both CSVs --------
    df_zero = pd.read_csv(csv_zero_shot)
    df_few = pd.read_csv(csv_few)

    ### -------- 2. Normalize column names to a common schema --------
    rename_map = {
        "Area_Good_Normalized": "alpha_G",
        "Density_Good_Normalized": "d_G",
        "Purity_Good": "p_G",
        "Area_Best_Normalized": "alpha_B",
        "Density_Best_Normalized": "d_B",
        "Purity_Best": "p_B",
    }

    df_zero = df_zero.rename(columns=rename_map)
    df_few = df_few.rename(columns=rename_map)

    ### -------- 3. Scale to % and round to 1 decimal --------
    for df in (df_zero, df_few):
        # multiply all except the model name "Row"
        num_cols = [c for c in df.columns if c != "Row"]
        df[num_cols] = (df[num_cols] * 100).round(1)


    ### -------- 4. Pretty-print model names (optional cosmetic cleanup) --------
    def pretty_name(x: str) -> str:
        mapping = {
            "chatgpt": "Chatgpt",
            "claude": "Claude",
            "deepseek": "Deepseek",
            "gemini": "Gemini",
            "gemma": "Gemma",
            "qwen": "Qwen",
        }
        return mapping.get(str(x).strip().lower(), x)


    df_zero["PrettyRow"] = df_zero["Row"].apply(pretty_name)
    df_few["PrettyRow"] = df_few["Row"].apply(pretty_name)

    ### -------- 5. Merge the two frames on PrettyRow, add suffixes --------
    merged = pd.merge(
        df_zero.set_index("PrettyRow"),
        df_few.set_index("PrettyRow"),
        left_index=True,
        right_index=True,
        suffixes=("_zero", "_few"),
        how="outer"
    ).reset_index()

    # Keep the row order from df_zero
    order_map = {name: i for i, name in enumerate(df_zero["PrettyRow"])}
    merged["order_idx"] = merged["PrettyRow"].map(order_map)
    merged = merged.sort_values("order_idx").reset_index(drop=True)

    ### -------- 6. Build lists of columns for zero-shot vs rag --------
    zero_cols = [
        "alpha_G_zero", "d_G_zero", "p_G_zero",
        "alpha_B_zero", "d_B_zero", "p_B_zero",
    ]
    rag_cols = [
        "alpha_G_few", "d_G_few", "p_G_few",
        "alpha_B_few", "d_B_few", "p_B_few",
    ]

    # Sanity check: make sure all expected columns exist
    missing_zero = [c for c in zero_cols if c not in merged.columns]
    missing_few = [c for c in rag_cols if c not in merged.columns]
    if missing_zero or missing_few:
        print("WARNING: Missing columns after merge:")
        print(" zero-shot missing:", missing_zero)
        print(" few missing:", missing_few)

    ### -------- 7. Compute max/min per block (zero vs rag separately) --------
    zero_max = merged[zero_cols].max(numeric_only=True)
    zero_min = merged[zero_cols].min(numeric_only=True)
    rag_max = merged[rag_cols].max(numeric_only=True)
    rag_min = merged[rag_cols].min(numeric_only=True)


    ### -------- 8. Formatter for bold / underline --------
    def fmt_val(val, colname, block):
        """
        val: numeric value
        colname: full column name in merged (e.g., 'alpha_G_zero')
        block: 'zero' or 'rag'
        """
        if pd.isna(val):
            return "--"
        s = f"{val}"
        if block == "zero":
            if val == zero_max[colname]:
                s = f"\\textbf{{{s}}}"
            elif val == zero_min[colname]:
                s = f"\\underline{{{s}}}"
        else:  # rag
            if val == rag_max[colname]:
                s = f"\\textbf{{{s}}}"
            elif val == rag_min[colname]:
                s = f"\\underline{{{s}}}"
        return s


    ### -------- 9. Emit LaTeX table --------

    print(r"\begin{table}[]")
    print(r"    \fontsize{10}{12}\selectfont")
    print(r"    \tabcolsep=0.1cm")
    print(r"    \centering")
    print(
        r"    \caption{Comparison of footprint evaluation between Pool and RAG models, describing footprint area ($\alpha$), density ($d$), and purity ($p$). Evaluation metrics are labeled as ``Good'' (G) or ``Best'' (B).}")
    print(r"    \label{table:footprint_merged}")
    print(r"    \begin{threeparttable}")
    print(r"        \begin{tabular}{@{}lcccccc|cccccc@{}}")
    print(r"        \toprule")
    print(r"        \multirow{3}{*}{\textbf{Models}} "
          r"& \multicolumn{6}{c|}{\textbf{Zero-Shot Models}} "
          r"& \multicolumn{6}{c}{\textbf{Few-Shot Models}} \\ ")
    print(r"        \cmidrule(lr){2-7} \cmidrule(lr){8-13}")
    print(r"        & \multicolumn{3}{c}{\textbf{``Good''}} & \multicolumn{3}{c|}{\textbf{``Best''}} "
          r"& \multicolumn{3}{c}{\textbf{``Good''}} & \multicolumn{3}{c}{\textbf{``Best''}} \\ ")
    print(r"        \cmidrule(lr){2-4} \cmidrule(lr){5-7} \cmidrule(lr){8-10} \cmidrule(lr){11-13}")
    print(r"        & $\alpha_{G}(\%)$ & $d_{G}(\%)$ & $p_{G}(\%)$ "
          r"& $\alpha_{B}(\%)$ & $d_{B}(\%)$ & $p_{B}(\%)$ "
          r"& $\alpha_{G}(\%)$ & $d_{G}(\%)$ & $p_{G}(\%)$ "
          r"& $\alpha_{B}(\%)$ & $d_{B}(\%)$ & $p_{B}(\%)$ \\ ")
    print(r"        \midrule")

    for i, row in merged.iterrows():
        # alternating row colour
        if i % 2 == 0:
            print(r"        \rowcolor[HTML]{DADADA} ", end="")
        else:
            print("        ", end="")

        # build row cells
        cells = [row["PrettyRow"]]

        # zero-shot block, "Good" then "Best"
        cells.append(fmt_val(row["alpha_G_zero"], "alpha_G_zero", "zero"))
        cells.append(fmt_val(row["d_G_zero"], "d_G_zero", "zero"))
        cells.append(fmt_val(row["p_G_zero"], "p_G_zero", "zero"))
        cells.append(fmt_val(row["alpha_B_zero"], "alpha_B_zero", "zero"))
        cells.append(fmt_val(row["d_B_zero"], "d_B_zero", "zero"))
        cells.append(fmt_val(row["p_B_zero"], "p_B_zero", "zero"))

        # rag block
        cells.append(fmt_val(row["alpha_G_few"], "alpha_G_few", "few"))
        cells.append(fmt_val(row["d_G_few"], "d_G_few", "few"))
        cells.append(fmt_val(row["p_G_few"], "p_G_few", "few"))
        cells.append(fmt_val(row["alpha_B_few"], "alpha_B_few", "few"))
        cells.append(fmt_val(row["d_B_few"], "d_B_few", "few"))
        cells.append(fmt_val(row["p_B_few"], "p_B_few", "few"))

        # print LaTeX row
        print(" & ".join(cells) + r" \\")

    print(r"        \bottomrule")
    print(r"        \end{tabular}")
    print(r"        \begin{tablenotes}")
    print(r"            \footnotesize")
    print(
        r"            \item \textit{Note: Higher values in each column are in \textbf{bold}, and lowest values are \underline{underlined}. Left block = Pool models; Right block = RAG models.}")
    print(r"        \end{tablenotes}")
    print(r"    \end{threeparttable}")
    print(r"\end{table}")
