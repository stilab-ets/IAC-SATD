import re
from typing import Optional, Tuple

from openai import OpenAI

from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.base_model import BaseLLM
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.prompts.prompt_zero_shot import PROMPT_COT_improved
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.prompts.prompt_few_shots import PROMPT_COT_RAG_improved


class DeepseekModel(BaseLLM):

    def __init__(self, api_key: str, model_name="deepseek-chat", temperature=0.0):
        self.model_name = model_name
        self.category_labels = ['CAT1', 'CAT2', 'CAT3', 'CAT4', 'CAT5', 'CAT6', 'CAT7', 'CAT8']
        self.temperature = temperature

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def generate(self, comment: str, context: str, code_block: str) -> str:
        prompt = PROMPT_COT_improved.format(comment=comment, context=context, code_block=code_block)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system",
                 "content": "You are a senior Infrastructure-as-Code (IaC) engineer with deep expertise in Terraform. Follow the requirements provided in the user prompt. Do not explain or reason."},
                {"role": "user", "content": prompt},
            ], temperature=self.temperature
            # , top_k=10, top_p=0.95
        )
        return response.choices[0].message.content.strip()

    def rag_implementation_for_single_prompts(
            self,
            train_data,
            comment: str,
            context: str,
            code_block: str,
            labels,
            retrieval_engine=None,
            query_vec=None,  # <—<—<— NEW: precomputed query vector (optional)
            generate_prompt_only=False  # ✅ NEW FLAG

    ) -> Tuple[Optional[int], Optional[str], str]:

        # 1) Retrieve
        query_triplet = (str(comment), str(context), str(code_block))

        hits = retrieval_engine.retrieve(
            query_triplet,
            train_df=train_data,
            label_cols=labels,
            top_k_final=2, k_bm25=200, k_dense=60, rrf_k=60,
            query_vec=query_vec,  # <— pass it through (None for non-precomputed modes)
        )

        # 2) Format into your prompt
        retrieved_examples = self._format_retrieved_examples(hits)
        prompt = PROMPT_COT_RAG_improved.format(
            comment=comment, context=context, code_block=code_block,
            retrieved_examples=retrieved_examples
        )

        # ✅ NEW: If we only want to get the prompt, stop here
        if generate_prompt_only:
            return None, None, prompt

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system",
                     "content": "You are a senior Infrastructure-as-Code (IaC) engineer with deep expertise in Terraform. Follow the requirements provided in the user prompt. Do not explain or reason."},
                    {"role": "user", "content": prompt}]
                , temperature=self.temperature
                # , top_k=10, top_p=0.95
            )
            label, raw_text = self._parse_llm_response(response.choices[0].message.content)
            return label, raw_text, prompt
        except Exception as e:
            print(f"❌ RAG single prompt failed: {e}")
            return 0, "ERROR", "ERROR"

    def _format_retrieved_examples(
            self,
            similar_comments: list[tuple[int, float, str, list[int]]],
    ) -> str:
        formatted = []

        for i, (doc_idx, score, comment_sim, label_vec) in enumerate(similar_comments):
            parts = comment_sim.split(" [SEP] ")
            example_comment = parts[0]
            example_context = parts[1] if len(parts) > 1 else ""
            example_code_block = " [SEP] ".join(parts[2:]) if len(parts) > 2 else ""

            selected_cats = [
                self.category_labels[j] for j, val in enumerate(label_vec) if val == 1
            ]
            CATS = ", ".join(selected_cats)

            formatted.append(
                f"Example {i + 1}:\n"
                f"Technical_debt_single_line_comment: {example_comment}\n"
                f"Technical_debt_comment_context: {example_context}\n"
                f"Code_block_associated_if_exists: {example_code_block}\n"
                f"CATS: {CATS}"
            )

        return "\n\n".join(formatted).strip()

    def _parse_llm_response(self, response_text: str) -> tuple[int, str]:
        answer = response_text.strip()
        match = re.search(r"ANSWER:\s*([01])", answer, re.IGNORECASE)
        label = int(match.group(1)) if match else 0
        return label, answer
