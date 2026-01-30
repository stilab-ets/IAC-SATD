import os
import pandas as pd

FILES = [
    "stratified_cleaned_test_fold_0.csv",
    "stratified_cleaned_test_fold_1.csv",
    "stratified_cleaned_test_fold_2.csv",
    "stratified_cleaned_test_fold_3.csv",
    "stratified_cleaned_test_fold_4.csv",
]

LABELS = [
    "IaC Code Debt",
    "Computing Management Debt",
    "Security Debt",
    "Networking Debt",
    "Dependency Management",
    "Environment-Based Configuration Debt",
    "Monitoring and Logging Debt",
    "Test Debt",
]

ALIASES = [
    "IaC Code Management ($C1$)",
    "Infrastructure Management ($C2$)",
    "Security ($C3$)",
    "Networking ($C4$)",
    "Dependency Management ($C5$)",
    "Environment-Based Config ($C6$)",
    "Monitoring/Logging ($C7$)",
    "Testing ($C8$)",
]

if __name__ == '__main__':

    # ---- Count positives per fold
    fold_counts = {}
    fold_sizes = []  # keep track of dataset size per fold
    for i, fp in enumerate(FILES, start=1):
        df = pd.read_csv( "./stratified_cleaned_folds/" + fp)
        fold_sizes.append(len(df))
        for col in LABELS:
            if df[col].dtype == bool:
                df[col] = df[col].astype(int)
        counts = df[LABELS].sum(numeric_only=True).astype(int)
        fold_counts[f"Fold {i}"] = counts

    counts_df = pd.DataFrame(fold_counts).loc[LABELS]
    counts_df["Total"] = counts_df.sum(axis=1)

    # ---- Print full LaTeX table
    print(r"\begin{table}[h!]")
    print(r"\centering")
    print(r"\caption{Distribution of labels across 5 folds using Iterative Stratification}")
    print(r"\label{tab:label-distribution}")
    print(r"\begin{tabular}{l|ccccc|c}")
    print(r"\hline")
    print(r"\hline")
    print(r"\rowcolor{black}")
    print(
        r"\textcolor{white}{\textbf{Labels}} & \textcolor{white}{$Fold 1$} & \textcolor{white}{$Fold 2$} & \textcolor{white}{$Fold 3$} & \textcolor{white}{$Fold 4$} & \textcolor{white}{$Fold 5$} & \textcolor{white}{$Total$} \\")
    print(r"\hline")
    print(r"\hline")


    def row_prefix(idx: int) -> str:
        return r"\rowcolor[HTML]{DADADA} " if idx % 2 == 1 else ""


    # Label rows
    for idx, (label, alias) in enumerate(zip(LABELS, ALIASES)):
        f1, f2, f3, f4, f5, tot = counts_df.loc[
            label, ["Fold 1", "Fold 2", "Fold 3", "Fold 4", "Fold 5", "Total"]].tolist()
        print(f"{row_prefix(idx)}{alias} & {int(f1)} & {int(f2)} & {int(f3)} & {int(f4)} & {int(f5)} & {int(tot)} \\\\")

    # Last row: fold sizes
    print(r"\hline")
    print(r"\textbf{Fold Size} & " +
          " & ".join(str(s) for s in fold_sizes) +
          f" & {sum(fold_sizes)} \\\\")

    print(r"\hline")
    print(r"\end{tabular}")
    print(r"\end{table}")
