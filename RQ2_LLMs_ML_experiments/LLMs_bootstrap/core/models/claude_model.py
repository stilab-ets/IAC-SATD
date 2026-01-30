import re
from typing import Tuple, Optional

import anthropic

from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.base_model import BaseLLM
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.prompts.prompt_zero_shot import PROMPT_COT_improved
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.prompts.prompt_few_shots import PROMPT_COT_RAG_improved


class ClaudeModel(BaseLLM):

    #
    def __init__(self, api_key: str, model_name="claude-3-5-haiku-20241022", temperature=0.0):
        self.model_name = model_name
        self.category_labels = ['CAT1', 'CAT2', 'CAT3', 'CAT4', 'CAT5', 'CAT6', 'CAT7', 'CAT8']
        self.client = anthropic.Anthropic(api_key=api_key)
        self.temperature = temperature

    def generate(self, comment: str, context: str, code_block: str) -> str:
        prompt = PROMPT_COT_improved.format(comment=comment, context=context, code_block=code_block)

        response = self.client.messages.create(
            model=self.model_name,
            system="You are a senior Infrastructure-as-Code (IaC) engineer with deep expertise in Terraform. Follow the requirements provided in the user prompt. DO NOT EXPLAIN OR REASON.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=self.temperature,
            thinking={"type": "disabled"},
            # , top_k=10, top_p=0.95
        )
        return response.content[0].text.strip()

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
            response = self.client.messages.create(
                model=self.model_name,
                system="You are a senior Infrastructure-as-Code (IaC) engineer with deep expertise in Terraform. Follow the requirements provided in the user prompt. DO NOT EXPLAIN OR REASON.",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=self.temperature,
                thinking={"type": "disabled"},
                stop_sequences=["Reasoning", "Explanation", "Rationale" ,"Because"]
                # , top_k=10, top_p=0.95
            )
            label, raw_text = self._parse_llm_response(response.content[0].text.strip())
            return label, raw_text, prompt

        except Exception as e:
            print(f"❌ RAG single prompt failed: {e}")
            return 0, "ERROR", "ERROR"

    def _format_retrieved_examples(self, similar_comments: list[tuple[int, float, str, list[int]]]) -> str:
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

# import re
# import json
# import anthropic
#
# from llm_crossval_runner.models.base_model import BaseLLM
# from prompt_engineering.improved_prompts.improved_cot.prompt_cot_single_improved import PROMPT_COT_improved
# from prompt_engineering.improved_prompts.improved_cot_rag.prompt_cot_rag_single_improved import PROMPT_COT_RAG_improved
#
#
# class ClaudeModel(BaseLLM):
#
#     def __init__(self, api_key: str, model_name="claude-3-5-haiku-20241022", temperature=0.0):
#         self.model_name = model_name
#         self.category_labels = ['CAT1', 'CAT2', 'CAT3', 'CAT4', 'CAT5', 'CAT6', 'CAT7', 'CAT8']
#         self.client = anthropic.Anthropic(api_key=api_key)
#         self.temperature = temperature
#
#         # JSON schema to force a single bit result
#         self._response_format = {
#             "type": "json_schema",
#             "json_schema": {
#                 "name": "binary_answer",
#                 "schema": {
#                     "type": "object",
#                     "properties": {
#                         "answer": {"type": "integer", "enum": [0, 1]}
#                     },
#                     "required": ["answer"],
#                     "additionalProperties": False
#                 },
#                 "strict": True
#             },
#         }
#
#         # System: output format contract only
#         self._system_msg = (
#             "You are a senior Infrastructure-as-Code (IaC) engineer with deep expertise in Terraform.\n"
#             "Return ONLY JSON that matches this schema: {\"answer\": 0|1}.\n"
#             "Do not explain, do not add keys, do not include text outside JSON."
#         )
#
#     def _call_claude_json(self, prompt: str) -> int:
#         resp = self.client.messages.create(
#             model=self.model_name,
#             system=self._system_msg,
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=8,
#             temperature=self.temperature,
#             response_format=self._response_format,
#             thinking={"type": "disabled"},
#             # Optional extra guardrails (uncomment if needed):
#             # top_k=1, top_p=0.0,
#             # stop_sequences=["\n\n", "Reasoning:", "EXPLANATION:"],
#         )
#         # Anthropic returns a JSON string; parse it
#         raw = resp.content[0].text
#         data = json.loads(raw)
#         return int(data["answer"])
#
#     def generate(self, comment: str, context: str, code_block: str) -> str:
#         prompt = PROMPT_COT_improved.format(comment=comment, context=context, code_block=code_block)
#         label = self._call_claude_json(prompt)
#         # Keep your current consumer happy (expects 'ANSWER: [01]')
#         return f"ANSWER: {label}"
#
#     def rag_implementation_for_single_prompts(
#             self,
#             train_data,
#             comment: str,
#             context: str,
#             code_block: str,
#             labels,
#             retrieval_engine=None,
#             query_vec=None,
#     ) -> tuple[int, str]:
#
#         # 1) Retrieve
#         query_triplet = (str(comment), str(context), str(code_block))
#         hits = retrieval_engine.retrieve(
#             query_triplet,
#             train_df=train_data,
#             label_cols=labels,
#             top_k_final=2, k_bm25=200, k_dense=60, rrf_k=60,
#             query_vec=query_vec,
#         )
#
#         # 2) Format prompt with retrieved examples
#         retrieved_examples = self._format_retrieved_examples(hits)
#         prompt = PROMPT_COT_RAG_improved.format(
#             comment=comment, context=context, code_block=code_block,
#             retrieved_examples=retrieved_examples
#         )
#
#         try:
#             label = self._call_claude_json(prompt)
#             answer_text = f"ANSWER: {label}"
#             return label, answer_text
#         except Exception as e:
#             print(f"❌ RAG single prompt failed: {e}")
#             return 0, "ERROR"
#
#     def _format_retrieved_examples(self, similar_comments: list[tuple[int, float, str, list[int]]]) -> str:
#         formatted = []
#         for i, (doc_idx, score, comment_sim, label_vec) in enumerate(similar_comments):
#             parts = comment_sim.split(" [SEP] ")
#             example_comment = parts[0]
#             example_context = parts[1] if len(parts) > 1 else ""
#             example_code_block = " [SEP] ".join(parts[2:]) if len(parts) > 2 else ""
#             selected_cats = [self.category_labels[j] for j, val in enumerate(label_vec) if val == 1]
#             CATS = ", ".join(selected_cats)
#             formatted.append(
#                 f"Example {i + 1}:\n"
#                 f"Technical_debt_single_line_comment: {example_comment}\n"
#                 f"Technical_debt_comment_context: {example_context}\n"
#                 f"Code_block_associated_if_exists: {example_code_block}\n"
#                 f"CATS: {CATS}"
#             )
#         return "\n\n".join(formatted).strip()
#
#     def _parse_llm_response(self, response_text: str) -> tuple[int, str]:
#         # Kept for compatibility; not used in the JSON path
#         answer = response_text.strip()
#         match = re.search(r"ANSWER:\s*([01])", answer, re.IGNORECASE)
#         label = int(match.group(1)) if match else 0
#         return label, answer
