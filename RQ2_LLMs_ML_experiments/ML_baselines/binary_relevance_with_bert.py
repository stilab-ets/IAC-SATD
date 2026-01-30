import os
import random
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from transformers import BertTokenizer, BertModel
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from lightgbm import LGBMClassifier
from prediction_saver import save_prediction_row_to_csv
import torch


# Label names
LABELS = [
    "Computing Management Debt",
    "IaC Code Debt",
    "Dependency Management",
    "Security Debt",
    "Networking Debt",
    "Environment-Based Configuration Debt",
    "Monitoring and Logging Debt",
    "Test Debt"
]

# Features
FEATURES = ["SATD Comment", "context", "bloc of first occurrence"]
FEATURE_COMBINATIONS = [tuple(FEATURES)]

# Model choices
MODEL_CHOICES = ['LightGBM', 'RF']

# Seeds to evaluate
SEEDS = [42, 43, 44, 45, 46, 47, 48, 49]

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load BERT model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased').to(device)
bert_model.eval()


def set_seed(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def encode_texts(texts):
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).cpu().numpy()


if __name__ == '__main__':
    for seed_idx, seed in enumerate(SEEDS):
        print(f"\n🌱 Running experiment iteration {seed_idx + 1} with seed = {seed}")
        set_seed(seed)

        # Define parameter grid with current seed
        parameters = {
            'RF': {
                'br__classifier': [RandomForestClassifier(random_state=seed)],
                'br__classifier__n_estimators': [100, 200, 300],
                'br__classifier__criterion': ['gini', 'entropy'],
                'br__classifier__max_depth': [3, 5, 10],
                'br__classifier__min_samples_split': [2, 5, 10],
                'br__classifier__max_features': ['sqrt', 'log2']
            },
            'LightGBM': {
                'br__classifier': [LGBMClassifier(random_state=seed)],
                'br__classifier__num_leaves': [31, 63, 127],
                'br__classifier__max_depth': [2, 3, 5],
                'br__classifier__subsample': [0.8, 1.0],
                'br__classifier__colsample_bytree': [0.8, 1.0]
            }
        }

        for model_choice in MODEL_CHOICES:
            print(f"\n🏁 Starting evaluation for model: {model_choice}")
            param_grid = parameters[model_choice]

            for fold in range(5):
                print(f"\n==== Processing Fold {fold} ====")
                train_data = pd.read_csv(
                    f'../Data_Splitting/stratified_cleaned_folds/stratified_cleaned_folds/stratified_cleaned_train_fold_{fold}.csv')
                test_data = pd.read_csv(
                    f'../Data_Splitting/stratified_cleaned_folds/stratified_cleaned_folds/stratified_cleaned_test_fold_{fold}.csv')

                for combo in FEATURE_COMBINATIONS:
                    combo_list = list(combo)
                    print(f"  >> Feature Combo: {combo_list}")
                    train_text = train_data[combo_list].astype(str).agg(" [SEP] ".join, axis=1)
                    test_text = test_data[combo_list].astype(str).agg(" [SEP] ".join, axis=1)

                    X_train = encode_texts(train_text.tolist())
                    X_test = encode_texts(test_text.tolist())
                    y_train = train_data[LABELS]
                    y_test = test_data[LABELS]

                    pipe = Pipeline([('br', BinaryRelevance())])
                    clf = GridSearchCV(pipe, param_grid, scoring='f1_weighted', n_jobs=-1, cv=3)
                    clf.fit(X_train, y_train)

                    y_pred = clf.predict(X_test).toarray()
                    predictions_csv = f'../LLM_predictions/ML_predictions/predictions_BR_{model_choice}_seed{seed}_bert_revised.csv'

                    for i in range(len(test_data)):
                        save_prediction_row_to_csv(
                            path=predictions_csv,
                            fold=fold,
                            index=i,
                            comment=test_data.iloc[i]['SATD Comment'],
                            context=test_data.iloc[i]['context'],
                            code_block=test_data.iloc[i]['bloc of first occurrence'],
                            label_flags=y_pred[i],
                            labels=LABELS
                        )
