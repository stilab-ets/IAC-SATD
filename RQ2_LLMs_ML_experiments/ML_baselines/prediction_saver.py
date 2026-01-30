import os
import pandas as pd


def save_prediction_row_to_csv(path, fold, index, comment, context, code_block, label_flags, labels):
    if not os.path.exists(path):
        pd.DataFrame(columns=['Fold', 'Index', 'Comment', 'Context', 'Code Block'] + labels).to_csv(path, index=False)

    row_data = {
        'Fold': fold,
        'Index': index,
        'Comment': comment,
        'Context': context,
        'Code Block': code_block,
        **{labels[i]: label_flags[i] for i in range(len(labels))}
    }

    df = pd.DataFrame([row_data])
    df.to_csv(path, mode='a', header=False, index=False)
