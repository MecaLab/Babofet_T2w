#!/bin/bash
#SBATCH -J niftymic_pipeline
#SBATCH -p batch
#SBATCH -w niolon13
#SBATCH --mem-per-cpu=48G
#SBATCH --time=48:00:00
#SBATCH -N 1
#SBATCH -o logs/init_%j.out
#SBATCH -e logs/init_%j.err

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: sbatch run_pipeline.slurm <subject> <session>"
    exit 1
fi

SUBJECT=$1
SESSION=$2

# Redirecting output from slurm to a file named with subject and session
LOG_FILE="logs/pipeline_niftymic_${SUBJECT}_${SESSION}.out"
mkdir -p logs
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=================================================================="
echo "Starting pipeline for Subject: $SUBJECT, Session: $SESSION"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Log file: $LOG_FILE"
echo "=================================================================="

conda activate longiseg  # needs tqdm, torch, monai for fetalbet inference
module load singularity
module load ANTS

# Step 1: Denoising
echo "Running Step 1: Denoising"
python nifty_module/01_denoising.py --subject "$SUBJECT" --session "$SESSION"
if [ $? -ne 0 ]; then echo "Error in Step 1"; exit 1; fi

# Step 2: Denoising
echo "Running Step 2: Brainmask generation using FetalBET"
python nifty_module/02_generate_brainmask.py --subject "$SUBJECT" --session "$SESSION"
if [ $? -ne 0 ]; then echo "Error in Step 2"; exit 1; fi

# Step 3: Image Reconstruction (Blocking call)
echo "Running Step 3: Image Reconstruction"
python nifty_module/03_image_reconstruction.py --subject "$SUBJECT" --session "$SESSION"
if [ $? -ne 0 ]; then echo "Error in Step 3"; exit 1; fi

# Step 4: Generate Subject Template Brainmask
echo "Running Step 4: Generate Subject Template Brainmask"
python nifty_module/04_generate_subj_template_brainmask.py --subject "$SUBJECT" --session "$SESSION"
if [ $? -ne 0 ]; then echo "Error in Step 4"; exit 1; fi

# Step 5: Debias
echo "Running Step 5: Debias"
python nifty_module/05_debias.py --subject "$SUBJECT" --session "$SESSION"
if [ $? -ne 0 ]; then echo "Error in Step 5"; exit 1; fi

echo "=================================================================="
echo "Pipeline completed successfully for $SUBJECT $SESSION"
echo "=================================================================="