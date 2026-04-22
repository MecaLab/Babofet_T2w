#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: ./run_them_all.sh SUBJECT SESSION_ID [SKIP_STEP]"
    echo "Example: ./run_them_all.sh sub-Borgne ses-01 niftymic"
    exit 1
fi

SUBJECT=$1
SESSION=$2
SKIP=$3

ZIP_SERVER_PATH="/scratch/lbaptiste/LongiSeg/results/Dataset003_FullSessions.zip"
LOCAL_ZIP_DST="/envau/work/meca/data/babofet_DB/2024_new_stuff/Dataset003_FullSessions.zip"
DATASET_ID="3"
DATASET_NAME="FullSessions"
TRAINER="LongiSegTrainerDiffWeighting"

# Define a log directory to avoid cluttering your root
mkdir -p logs

echo "Submitting pipeline jobs..."

# --- Step 1: NiftyMIC ---
if [ "$SKIP" == "niftymic" ]; then
    echo "Skipping Step 1: NiftyMIC"
    PREVIOUS_JOB_ID=""
else
    JOB1_ID=$(sbatch --parsable --output="$LOG_DIR/niftymic-%j.out" nifty_module/run_pipeline_niftymic.slurm "$SUBJECT" "$SESSION")
    echo "Step 1, NiftyMIC 3D Reconstruction, submitted with Job ID: $JOB1_ID"
    PREVIOUS_JOB_ID=$JOB1_ID
fi

# --- Step 2: Segmentation ---
if [ "$SKIP" == "segmentation" ]; then
    echo "Skipping Step 2: LongiSeg"
    # PREVIOUS_JOB_ID remains whatever it was (either Job 1 or empty)
else
    DEP=""
    if [ ! -z "$PREVIOUS_JOB_ID" ]; then
        DEP="--dependency=afterok:$PREVIOUS_JOB_ID"
    fi

    JOB2_ID=$(sbatch --parsable $DEP --output="$LOG_DIR/segmentation-%j.out" segmentation_module/inference_module/run_inference_pipeline.sh "$SUBJECT" "$SESSION" "$ZIP_SERVER_PATH" "$LOCAL_ZIP_DST" "$DATASET_ID" "$DATASET_NAME" "$TRAINER")
    echo "Step 2, LongiSeg Segmentation, submitted with Job ID: $JOB2_ID"
    PREVIOUS_JOB_ID=$JOB2_ID
fi

# --- Step 3: Surface Extraction ---
if [ "$SKIP" == "extraction" ]; then
    echo "Skipping Step 3: Surface Extraction"
else
    DEP=""
    if [ ! -z "$PREVIOUS_JOB_ID" ]; then
        DEP="--dependency=afterok:$PREVIOUS_JOB_ID"
    fi

    JOB3_ID=$(sbatch --parsable $DEP --output="$LOG_DIR/extraction-%j.out" extraction_module/run_extraction_pipeline.slurm "$SUBJECT" "$SESSION")
    echo "Step 3, Surface Extraction, submitted with Job ID: $JOB3_ID"
fi

echo "All jobs submitted successfully. Logs are in $LOG_DIR"