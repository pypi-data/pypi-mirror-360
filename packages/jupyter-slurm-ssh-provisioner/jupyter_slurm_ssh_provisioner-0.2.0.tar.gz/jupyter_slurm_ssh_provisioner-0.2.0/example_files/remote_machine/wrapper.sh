{
  # Everything inside this block is logged
  source ./venv/bin/activate

  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  SLURM_SCRIPT="${SCRIPT_DIR}/slurm.sh"
  JOB_SUBMIT_OUTPUT=$(sbatch "$SLURM_SCRIPT")
  JOB_ID=$(echo "$JOB_SUBMIT_OUTPUT" | awk '{print $4}')
  CONN_FILE="/tmp/kernel-${JOB_ID}.json"

  TIMEOUT=600 # job could be in queue for a long time
  SLEEP_INTERVAL=3
  ELAPSED=0

  while [ ! -f "$CONN_FILE" ]; do
    sleep $SLEEP_INTERVAL
    ELAPSED=$((ELAPSED + SLEEP_INTERVAL))
    if ! squeue -j "$JOB_ID" > /dev/null; then
      echo "Error: Slurm job $JOB_ID not found or finished prematurely." >&2
      exit 1
    fi
    if [ $ELAPSED -ge $TIMEOUT ]; then
      echo "Timeout waiting for kernel connection file." >&2
      exit 1
    fi
  done
} > /tmp/wrapper.log 2>&1

# Only this line goes to stdout
echo "$JOB_ID"