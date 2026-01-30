#!/bin/bash
#SBATCH --job-name=satd_llm
#SBATCH --partition=main
#SBATCH --gres=gpu:4
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=32
#SBATCH --time=07:00:00
#SBATCH --output=logs/vllm_experiment_%j.out

echo "🧠 Host: $(hostname)"
echo "📅 Started at: $(date)"

# === Configuration ===
MODEL_NAME="Qwen/Qwen3-32B"
VLLM_VENV="XXXXXXXXXXXXXX" # Insert the venv absolute path
VLLM_PATH="$VLLM_VENV/bin/vllm"

# === Activate virtual environment ===
echo "🐍 Activating virtual environment: $VLLM_VENV"
source "$VLLM_VENV/bin/activate"

# Start vLLM server in the background
$VLLM_PATH serve "$MODEL_NAME" \
  --port 8015 \
  --host 0.0.0.0 \
  --tensor-parallel-size 4 \
  --chat-template ./qwen3_nonthinking.jinja \ # Insert the qwen3_nonthinking.jinja template
  > vllm_server.log 2>&1 &


# Save PID so we can wait or kill later if needed
VLLM_PID=$!

# Health check loop — wait for vLLM to accept completions
echo "⏳ Waiting for vLLM server to fully start..."

sleep 10

# Wait until vLLM server is up
until curl -s http://localhost:8015/v1 > /dev/null; do
  echo "🔁 Waiting for vLLM API to become available..."
  sleep 2
done

echo "🚀 vLLM is ready. Starting experiment script..."

#####python3 -m llm_crossval_runner.main

python3 -m llm_crossval_runner.retriever.main_RAG

echo "🎉 Experiment finished."

kill $VLLM_PID

