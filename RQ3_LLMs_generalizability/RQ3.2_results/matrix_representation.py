import pandas as pd

if __name__ == '__main__':

    # Path to your CSV file
    csv_file = "../ISA_application/evaluation_details_hamming_zero_shot/projection_matrix.csv"  # TODO ← replace with CSV path of zero-shot
    # csv_file = "../ISA_application/evaluation_details_hamming_few_shots/projection_matrix.csv"

    # Read CSV
    df = pd.read_csv(csv_file)

    # Extract feature names (excluding the first column 'Row')
    features = list(df.columns[1:])

    # Escape underscores for LaTeX
    features = [f.replace("_", "\\_") for f in features]

    # Extract numeric values and transpose (features as rows, z's as columns)
    matrix = df.iloc[:, 1:].values.T

    # Round values
    round_decimals = 4
    matrix = matrix.round(round_decimals)

    # Print LaTeX code
    print("\\begin{footnotesize}")
    print("\\begin{equation}")
    print("\\centering")
    print("\\vec{\\mathbf{z}} = ")
    print("\\begin{bmatrix}")
    print("z_1 \\\\")
    print("z_2")
    print("\\end{bmatrix} =")
    print("\\begin{bmatrix}")

    # Find max positive per column
    max_pos_per_col = []
    for col in range(matrix.shape[1]):
        col_vals = matrix[:, col]
        pos_vals = col_vals[col_vals > 0]
        if len(pos_vals) > 0:
            max_pos_per_col.append(pos_vals.max())
        else:
            max_pos_per_col.append(None)

    # Print matrix rows (features)
    for row_idx, row in enumerate(matrix):
        row_parts = []
        for col_idx, val in enumerate(row):
            val_str = f"{val:.{round_decimals}f}"
            if max_pos_per_col[col_idx] is not None and val == max_pos_per_col[col_idx]:
                val_str = f"\\textbf{{{val_str}}}"
            row_parts.append(val_str)
        print("  " + " & ".join(row_parts) + " \\\\")
    print("\\end{bmatrix}^T")

    # Print feature names
    print("\\begin{bmatrix}")
    for f in features:
        print(f"\\text{{{f}}} \\\\")
    print("\\end{bmatrix}")

    print("\\label{eq:defect_matrix}")
    print("\\end{equation}")
    print("\\end{footnotesize}")
