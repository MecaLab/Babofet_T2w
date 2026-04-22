#!/bin/bash

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: ./run_them_all.sh SUBJECT SESSION_ID"
    echo "Example: ./run_them_all.sh sub-Borgne ses-01"
    exit 1
fi

SUBJECT=$1
SESSION=$2

ZIP_SERVER_PATH="/scratch/lbaptiste/LongiSeg/results/Dataset003_FullSessions.zip"
LOCAL_ZIP_DST="/envau/work/meca/data/babofet_DB/2024_new_stuff/Dataset003_FullSessions.zip"
DATASET_ID="3"
DATASET_NAME="FullSessions"
TRAINER="LongiSegTrainerDiffWeighting"

# Create a logs directory to avoid slurm-ID.out files in the current folder
LOG_DIR="slurm_logs/${SUBJECT}/${SESSION}"
mkdir -p "$LOG_DIR"

echo "Submitting pipeline jobs..."

# Step 1: NiftyMIC
JOB1_ID=$(sbatch --parsable --output="$LOG_DIR/step1_%j.out" nifty_module/run_pipeline_niftymic.slurm "$SUBJECT" "$SESSION")
echo "Step 1, NiftyMIC 3D Reconstruction, submitted with Job ID: $JOB1_ID"

# Step 2: LongiSeg Segmentation
# We check if JOB1_ID is not empty to avoid dependency errors
if [ -n "$JOB1_ID" ]; then
    JOB2_ID=$(sbatch --parsable --dependency=afterok:$JOB1_ID --output="$LOG_DIR/step2_%j.out" segmentation_module/inference_module/run_inference_pipeline.sh "$SUBJECT" "$SESSION" "$ZIP_SERVER_PATH" "$LOCAL_ZIP_DST" "$DATASET_ID" "$DATASET_NAME" "$TRAINER")
    echo "Step 2, LongiSeg Segmentation, submitted with Job ID: $JOB2_ID"
else
    echo "Error: Step 1 failed to return a Job ID."
    exit 1
fi

# Step 3: Surface Extraction
# We check if JOB2_ID is not empty
if [ -n "$JOB2_ID" ]; then
    JOB3_ID=$(sbatch --parsable --dependency=afterok:$JOB2_ID --output="$LOG_DIR/step3_%j.out" extraction_module/run_extraction_pipeline.slurm "$SUBJECT" "$SESSION")
    echo "Step 3, Surface Extraction, submitted with Job ID: $JOB3_ID"
else
    echo "Error: Step 2 failed to return a Job ID. Step 3 not submitted."
    exit 1
fi

echo "All jobs submitted successfully. Logs are in: $LOG_DIR"