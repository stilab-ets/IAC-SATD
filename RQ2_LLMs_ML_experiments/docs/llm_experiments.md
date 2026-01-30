# LLM Experiments

Large Language Model experiments for multi-label SATD classification using zero-shot and few-shot (RAG) approaches.

---

## Supported Models

| Model | Provider | Type | Configuration |
|-------|----------|------|---------------|
| **ChatGPT** | OpenAI | API | `ChatGPTModel(api_key=..., temperature=...)` |
| **Claude** | Anthropic | API | `ClaudeModel(api_key=..., temperature=...)` |
| **Gemini** | Google | API | `GeminiModel(api_key_manager=...)` |
| **DeepSeek** | DeepSeek | API | `DeepseekModel(api_key=..., temperature=...)` |
| **Gemma** | Google | vLLM | `GemmaModel(temperature=...)` |
| **Qwen** | Alibaba | vLLM | `QwenModel(temperature=...)` |

---

## 1. Zero-Shot Experiments

LLMs classify without examples using only category definitions.

### Running

```bash
cd LLMs_bootstrap/core
python main.py
```

### Configuration

Edit `main.py`:
```python
selected_model_key = "deepseek"  # chatgpt, claude, gemini, gemma, deepseek, qwen
multi_prompt = False
is_alaa_exec = False

for temp in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
    model = get_model(selected_model_key, temperature=temp)
    run_crossval_from_files(...)
```

### Output

`llm_crossval_runner/results/{model}_eval_single_prompt_improved_v11_tmp_{temp}_v2.csv`

---

## 2. Few-Shot Experiments (RAG)

LLMs classify using retrieved similar examples from training data.

### Running

```bash
cd LLMs_bootstrap/core/retriever
python main_RAG.py
```

### Configuration

Edit `main_RAG.py`:
```python
selected_model_key = "claude"
retrieval_mode = "openai_precomputed"  # See retrieval modes below
is_prompt_generation_only = False  # True for ground truth prompts only

for temp in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
    ...
```

### Retrieval Modes

| Mode | Description |
|------|-------------|
| `mpnet_dense` | Dense retrieval using MPNet embeddings |
| `dpr` | Dense Passage Retrieval |
| `rrf_fusion_mpnet` | Reciprocal Rank Fusion (BM25 + MPNet) |
| `rrf_fusion_dpr` | Reciprocal Rank Fusion (BM25 + DPR) |
| `openai_precomputed` | Precomputed OpenAI embeddings |

### Output

`core/results/rag_{mode}_tests/{model}_eval_v11_tmp_{temp}_rag_{mode}.csv`

---

## Prompt Engineering

### Zero-Shot Prompt Structure

```
You are an expert Infrastructure-as-Code (IaC) developer...

INSTANCE:
Technical_debt_single_line_comment: {comment}
Technical_debt_comment_context: {context}
Code_block_associated_if_exists: {code_block}

OUTPUT: CAT1, CAT2, CAT3, CAT4, CAT5, CAT6, CAT7, CAT8

CATEGORY DEFINITIONS:
[Detailed definitions with inclusion/exclusion rules...]

ANSWER:
```

### Few-Shot Prompt Structure

Same as zero-shot, plus:
```
In the following, I will introduce some examples related to that instance...
==============================
{retrieved_examples}
==============================

ANSWER:
```

**Key Features:**
- Clear role definition
- Strict category definitions with rules
- Multi-label instructions
- Code block analysis guidance
- Chain-of-thought structure

---

## vLLM Server (for Gemma/Qwen)

### Start Server

```bash
vllm serve google/gemma-3-27b-it \
  --port 8015 \
  --host 0.0.0.0 \
  --tensor-parallel-size 4
```

### SLURM (HPC)

```bash
sbatch run_vllm_satd_all_models.slurm
```

**Configuration:**
- GPUs: 4 (tensor parallelism)
- Memory: 64GB
- CPUs: 32 cores
- Time: 7 hours

---

## Cross-Validation

- **5-fold stratified** cross-validation
- **Resumable:** Tracks completed (fold, row) pairs
- **Retry logic:** Max 5 retries with exponential backoff
- **Failed requests:** Logged to `failed_requests.csv`

---

## Temperature Sweep

All experiments run with temperatures: `[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]`

- `0.0` = Deterministic
- Higher values = More randomness

---

## API Key Setup

Edit these files:
- `LLMs_bootstrap/core/models/api_key_management.py`
- `LLMs_bootstrap/core/main.py`
- `LLMs_bootstrap/core/retriever/main_RAG.py`

Replace `XXXXXXXXXX` with actual API keys.

---

## Output Format

See [Data Format](data_format.md) for detailed CSV specifications.
