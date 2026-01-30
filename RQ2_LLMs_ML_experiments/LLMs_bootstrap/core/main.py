import os

from models.chagpt_model import ChatGPTModel
from models.claude_model import ClaudeModel
from models.gemma_model import GemmaModel
from models.qween import QwenModel
from models.deepseek_model import DeepseekModel
from models.gemini_model import GeminiModel
from crossval_executor import run_crossval_from_files

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

def get_model(model_key, temperature):
    if model_key == "gemini":
        return GeminiModel(api_key="XXXXXXXXXX", temperature=temperature)
    elif model_key == "deepseek":
        return DeepseekModel(api_key="XXXXXXXXXX", temperature=temperature)
    elif model_key == "claude":
        return ClaudeModel(api_key="XXXXXXXXXX", temperature=temperature)
    elif model_key == "chatgpt":
        return ChatGPTModel(api_key="XXXXXXXXXX", temperature=temperature)
    elif model_key == "qwen":
        return QwenModel(temperature=temperature)
    elif model_key == "gemma":
        return GemmaModel(temperature=temperature)
    else:
        raise ValueError(f"Model {model_key} not found.")


if __name__ == '__main__':
    selected_model_key = "deepseek"  # 🔁 Change as needed  🔁
    multi_prompt = False             # 🔁 Switch True/False 🔁
    is_alaa_exec = False

    # ✅ Define path relative to the project root
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    folds_dir = os.path.join(PROJECT_ROOT, "RQ2_LLMs_ML_experiments", "Data_Splitting", "stratified_cleaned_folds")

    for temp in [ 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        print(f"🔁 Running with temperature = {temp}")
        model = get_model(selected_model_key, temperature=temp)

        output_path = os.path.join(
            PROJECT_ROOT,
            "llm_crossval_runner",
            "results",
            f"{selected_model_key}_eval_single_prompt_improved_v11_tmp_{temp}_v2.csv"
        )

        run_crossval_from_files(
            model=model,
            folds_dir=folds_dir,
            output_path=output_path,
            labels=LABELS,
            num_folds=5,
            multi_prompt=multi_prompt,
            is_alaa_exec=is_alaa_exec
        )
