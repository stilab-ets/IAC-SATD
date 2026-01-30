import os
import random

import pandas as pd
import numpy as np
from skmultilearn.model_selection import IterativeStratification

SEED = 42

os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)

# === Load dataset ===
df = pd.read_csv("./cleaned_dataset_revised_filtered.csv")


# === Label columns (multi-label) ===
label_cols = [
    "Computing Management Debt", "IaC Code Debt", "Dependency Management",
    "Security Debt", "Networking Debt", "Environment-Based Configuration Debt",
    "Monitoring and Logging Debt", "Test Debt"
]



if __name__ == '__main__':


    # === Feature and label separation ===
    X = df.drop(columns=label_cols)
    y = df[label_cols]

    # === Prepare output directory ===
    output_dir = "./stratified_cleaned_folds"
    os.makedirs(output_dir, exist_ok=True)

    # === Multi-label Stratified Split ===
    stratifier = IterativeStratification(n_splits=5, order=8)

    def print_label_distribution(df_revised, label_cols, fold_name):
        print(f"\n🔍 Label distribution for {fold_name}:")
        total = len(df_revised)
        for col in label_cols:
            count = df[col].sum()
            percent = 100 * count / total
            print(f" - {col}: {count} instances ({percent:.2f}%)")

    for fold, (train_idx, test_idx) in enumerate(stratifier.split(X, y)):
        print(f"\n📂 Fold {fold + 1}")
        print(f"🔹 Train instances: {len(train_idx)}")
        print(f"🔸 Test instances : {len(test_idx)}")

        # Combine X and y
        train_df = pd.concat([X.iloc[train_idx], y.iloc[train_idx]], axis=1)
        test_df = pd.concat([X.iloc[test_idx], y.iloc[test_idx]], axis=1)

        # Analyze label distribution
        print_label_distribution(train_df, label_cols, f"Train Fold {fold}")
        print_label_distribution(test_df, label_cols, f"Test Fold {fold}")

        # Save with unified filenames
        train_path = os.path.join(output_dir, f"stratified_cleaned_train_fold_{fold}.csv")
        test_path = os.path.join(output_dir, f"stratified_cleaned_test_fold_{fold}.csv")

        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)

        print(f"✅ Saved: {train_path}")
        print(f"✅ Saved: {test_path}")
