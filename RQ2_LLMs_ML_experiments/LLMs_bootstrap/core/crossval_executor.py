import os
import time
import pandas as pd

from utils import save_row_to_csv, is_retryable_error

PROMPT_DICT_cot_traditional = {}

PROMPT_DICT_cot_improved = {}

# ✅ Define project root path relative to this script
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))


def load_completed_rows(output_path):
    if not os.path.exists(output_path):
        return set()
    df_done = pd.read_csv(output_path)
    return set(zip(df_done['fold'], df_done['row']))

def run_crossval_from_files(model, folds_dir: str, output_path: str, labels: list, num_folds: int = 5, is_alaa_exec: bool = False):
    MAX_RETRIES = 5
    folds_dir = os.path.join(PROJECT_ROOT, folds_dir)
    completed = load_completed_rows(output_path)

    for fold in range(num_folds):
        test_file_path = os.path.join(folds_dir, f"stratified_cleaned_test_fold_{fold}.csv")
        test_data = pd.read_csv(test_file_path)

        print(f"\n🔁 Fold {fold} — Loaded {len(test_data)} examples from {test_file_path}")

        for i, row in test_data.iterrows():

            if (fold, i) in completed:
                print(f"⏭️  Fold {fold} Row {i} already completed. Skipping.")
                continue

            for attempt in range(MAX_RETRIES):
                try:

                    response = model.generate(is_alaa_exec, comment=row["SATD Comment"], context=row["context"],
                                                  code_block=row["bloc of first occurrence"])

                    label_flags = [1 if f"CAT{j + 1}" in response else 0 for j in range(len(labels))]

                    predicted = [labels[j] for j, val in enumerate(label_flags) if val == 1]

                    save_row_to_csv(output_path, fold, i, row, response, label_flags, predicted, labels)
                    print(f"✅ Fold {fold} Row {i} processed successfully.")
                    time.sleep(2)
                    break

                except Exception as e:
                    print(f"⚠️ Fold {fold} Row {i} Attempt {attempt + 1} Error: {e}")

                    if attempt == MAX_RETRIES - 1 or not is_retryable_error(e):
                        print(f"❌ Giving up on Fold {fold} Row {i}.")
                        with open("failed_requests.csv", "a") as f:
                            error_msg = str(e).replace('"', "'")
                            f.write(f"{fold},{i},\"{error_msg}\"\n")
                        break

                    wait_time = min(2 ** attempt + 1, 60)
                    print(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
