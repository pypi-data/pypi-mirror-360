#!/bin/bash
#SBATCH --job-name=ipykernel
#SBATCH --output=ipykernel-%j.log
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500M
#SBATCH --partition=short

# Start the IPython kernel manually and write the connection file to a known location
python -m ipykernel_launcher -f=/tmp/kernel-${SLURM_JOB_ID}.json