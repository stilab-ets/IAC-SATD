# Troubleshooting

Common issues and solutions for RQ2 experiments.

---

## Import Errors

### Problem
```python
ModuleNotFoundError: No module named 'RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models'
```

### Solution

**Option 1: Fix imports manually**
```python
# Change from:
from RQ2_LLMs_ML_experiments.LLMs_bootstrap.core.models.chagpt_model import ChatGPTModel

# To:
from models.chagpt_model import ChatGPTModel
```

**Option 2: Use PyCharm**
1. Open project in PyCharm
2. Mark `replication_SATD_IaC` as project root
3. Run scripts from IDE

**Option 3: Set PYTHONPATH**
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/replication_SATD_IaC"
```

---

## API Rate Limits

### Problem
```
Rate limit exceeded for API requests
```

### Solution

**Increase sleep time:**
Edit `LLMs_bootstrap/core/crossval_executor.py`:
```python
time.sleep(5)  # Increase from 2 to 5 seconds
```

**Use multiple API keys (Gemini):**
Edit `LLMs_bootstrap/core/retriever/main_RAG.py`:
```python
GEMINI_KEYS = [
    "key1",
    "key2",
    "key3",
]
gemini_key_manager = APIKeyManager(api_keys=GEMINI_KEYS, rate_limit=10, time_window=90)
```

---

## vLLM Server Issues

### Problem: Server won't start

**Check GPU availability:**
```bash
nvidia-smi
```

**Check port availability:**
```bash
# Windows
netstat -ano | findstr :8015

# Linux
lsof -i :8015
```

**Verify model name:**
```bash
vllm serve google/gemma-3-27b-it --help
```

### Problem: Out of memory

**Solution: Increase tensor parallelism**
```bash
vllm serve google/gemma-3-27b-it \
  --tensor-parallel-size 4  # Increase from 2 to 4
```

**Or use smaller model:**
```bash
vllm serve google/gemma-9b-it  # Instead of 27b
```

---

## Missing API Keys

### Problem
```
API key not found or invalid
```

### Solution

Edit model files in `LLMs_bootstrap/core/models/`:
```python
# This needs to be filled with your actual API keys
ChatGPTModel(api_key="YOUR_OPENAI_API_KEY", temperature=0.0)
ClaudeModel(api_key="YOUR_CLAUDE_API_KEY", temperature=0.0)
GeminiModel(api_key="YOUR_GEMINI_API_KEY", temperature=0.0)
```

---

## CUDA Out of Memory

### Problem
```
RuntimeError: CUDA out of memory
```

### Solution

**For ML baselines:**
```python
# In binary_relevance_with_bert.py
device = torch.device('cpu')  # Force CPU instead of CUDA
```

**For vLLM:**
```bash
# Reduce batch size or use smaller model
vllm serve google/gemma-9b-it  # Smaller model
```

---

## Failed Requests

### Problem
Requests fail intermittently

### Solution

**Check failed requests log:**
```bash
cat failed_requests.csv
```

**Retry failed instances:**
Edit `LLMs_bootstrap/core/retriever/main_RAG.py`:
```python
# Uncomment retry line
retry_failed_instances(model, folds_dir, output_path, LABELS, retrieval_mode)
```

**Increase retry attempts:**
Edit `LLMs_bootstrap/core/crossval_executor.py`:
```python
MAX_RETRIES = 10  # Increase from 5
```

---

## Statistical Testing Errors

### Problem
```
FileNotFoundError: performance_analysis/zero_shot_vs_ml_baselines.csv not found
```

### Solution

**Ensure predictions exist:**
1. Run LLM experiments first
2. Run ML baselines
3. Transform data using `transform_simple.py`
4. Then run statistical tests

**Check file paths:**
Edit `apply_tim_testing.py`:
```python
input_csv = Path("./performance_analysis/zero_shot_vs_ml_baselines.csv")
# Verify this path exists
```

---

## Slow Execution

### Problem
Experiments take too long

### Solution

**Test with single fold first:**
```python
# In main.py or main_RAG.py
for fold in range(1):  # Change from range(5) to range(1)
    ...
```

**Use smaller temperature range:**
```python
for temp in [0.0, 0.3, 0.6]:  # Instead of [0.0, 0.1, 0.2, ...]
    ...
```

**Parallelize across models:**
Run different models in separate terminal sessions

---

## Data Loading Errors

### Problem
```
KeyError: 'SATD Comment' not found in DataFrame
```

### Solution

**Check CSV structure:**
```python
import pandas as pd
df = pd.read_csv("path/to/file.csv")
print(df.columns.tolist())
```

**Verify file path:**
```python
# In binary_relevance_with_bert.py
train_data = pd.read_csv(
    '../Data_Splitting/stratified_cleaned_folds/stratified_cleaned_train_fold_0.csv'
)
# Check if path is correct relative to script location
```

---

## Permission Errors

### Problem
```
PermissionError: [Errno 13] Permission denied
```

### Solution

**Windows:**
```powershell
# Run PowerShell as Administrator
# Or change file permissions
icacls "path\to\file" /grant Users:F
```

**Linux:**
```bash
chmod +x script.py
# Or run with sudo if necessary
sudo python script.py
```

---

## Getting Help

If issues persist:

1. **Check logs:** Review terminal output and error messages
2. **Verify paths:** Ensure all file paths are correct
3. **Test incrementally:** Run on small subset first
4. **Check dependencies:** Verify all packages installed correctly
5. **Review configuration:** Double-check API keys, model names, etc.
