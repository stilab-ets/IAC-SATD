import re
from typing import List, Tuple, Optional
from openai import OpenAI

from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.base_model import BaseLLM
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.prompts.prompt_zero_shot import PROMPT_COT_improved
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.prompts.prompt_few_shots import PROMPT_COT_RAG_improved


class OpenRouterModel(BaseLLM):
    """
    OpenRouter-backed model using OpenAI-compatible SDK.
    Example model slugs:
      - "deepseek/deepseek-chat-v3-0324"   (default here)
      - "deepseek/deepseek-reasoner"       (if you need the R1-like)
      - "meta-llama/llama-3.1-70b-instruct"
      - "anthropic/claude-3-5-sonnet"
    """

    def __init__(self, api_key: str, model_name: str = "deepseek/deepseek-chat-v3-0324", temperature: float = 0.0):
        self.model_name = model_name
        self.category_labels = ['CAT1', 'CAT2', 'CAT3', 'CAT4', 'CAT5', 'CAT6', 'CAT7', 'CAT8']
        self.temperature = temperature

        # OpenAI-compatible client pointed at OpenRouter
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            # Optional but recommended by OpenRouter for attribution/analytics:
            # default_headers={"HTTP-Referer": "http://your-app-url", "X-Title": "YourAppName"}
        )

    def generate(self, comment: str, context: str, code_block: str) -> str:
        prompt = PROMPT_COT_improved.format(comment=comment, context=context, code_block=code_block)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system",
                 "content": "You are a senior Infrastructure-as-Code (IaC) engineer with deep expertise in Terraform. "
                            "Follow the requirements provided in the user prompt. Do not explain or reason."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
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
        query_vec=None,  # precomputed query vector (optional)
        generate_prompt_only=False  # ✅ NEW FLAG
    ) -> Tuple[Optional[int], Optional[str], str]:

        # 1) Retrieve
        query_triplet = (str(comment), str(context), str(code_block))
        hits = retrieval_engine.retrieve(
            query_triplet,
            train_df=train_data,
            label_cols=labels,
            top_k_final=2, k_bm25=200, k_dense=60, rrf_k=60,
            query_vec=query_vec,
        )

        # 2) Prompt with retrieved examples
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
                     "content": "You are a senior Infrastructure-as-Code (IaC) engineer with deep expertise in Terraform. "
                                "Follow the requirements provided in the user prompt. Do not explain or reason."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
            )
            raw_text = response.choices[0].message.content
            label, parsed_text = self._parse_llm_response(raw_text)
            return label, parsed_text, prompt
        except Exception as e:
            print(f"❌ RAG single prompt failed: {e}")
            return 0, "ERROR", "ERROR"

    # ---------- utilities ----------
    def _format_retrieved_examples(
        self,
        similar_comments: List[Tuple[int, float, str, List[int]]],
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

    def _parse_llm_response(self, response_text: str) -> Tuple[int, str]:
        answer = (response_text or "").strip()
        match = re.search(r"ANSWER:\s*([01])", answer, re.IGNORECASE)
        label = int(match.group(1)) if match else 0
        return label, answer
