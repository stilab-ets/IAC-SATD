import pandas as pd
import os

import os

# Path to the root of the project
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def save_row_to_csv(path, fold, index, row, response_text, prompt_text, label_flags, predicted_labels, labels):
    if not os.path.exists(path):
        pd.DataFrame(columns=['Fold', 'Index', 'Comment', 'Context', 'Code Block', 'Prompt', 'Response'] +
                             labels + ['Predicted Labels']).to_csv(path, index=False)

    df = pd.DataFrame({
        'Fold': [fold],
        'Index': [index],
        'Comment': [row['SATD Comment']],
        'Context': [row['context']],
        'Code Block': [row['bloc of first occurrence']],
        # 'Prompt': ["--hidden--"],  # Optional
        'Prompt': [prompt_text],
        'Response': [response_text],
        **{labels[i]: [label_flags[i]] for i in range(len(labels))},
        'Predicted Labels': [predicted_labels]
    })

    df.to_csv(path, mode='a', header=False, index=False)


def save_row_prompt(path, fold, index, row, labels, prompt):
    if not os.path.exists(path):
        pd.DataFrame(columns=['Fold', 'Index', 'Comment', 'Context', 'Code Block', 'Prompt'] + labels) \
            .to_csv(path, index=False)

    # Extract the ground-truth labels
    ground_truth_labels = [1 if row.get(label, 0) == 1 else 0 for label in labels]

    df = pd.DataFrame({
        'Fold': [fold],
        'Index': [index],
        'Comment': [row['SATD Comment']],
        'Context': [row.get('context', '')],
        'Code Block': [row.get('bloc of first occurrence', '')],
        'Prompt': [prompt],
        **{label: [gt] for label, gt in zip(labels, ground_truth_labels)}
    })

    df.to_csv(path, mode='a', header=False, index=False)


def is_retryable_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(keyword in msg for keyword in [
        "503", "service unavailable", "429", "too many requests",
        "timeout", "connection", "temporarily unavailable", "rate limit"
    ])
