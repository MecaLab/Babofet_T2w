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

echo "Submitting pipeline jobs..."

# --- Step 1: NiftyMIC ---
if [ "$SKIP" == "skip-niftymic" ]; then
    echo "Skipping Step 1: NiftyMIC"
    JOB1_ID=""
else
    JOB1_ID=$(sbatch --parsable nifty_module/run_pipeline_niftymic.slurm "$SUBJECT" "$SESSION")
    echo "Step 1, NiftyMIC 3D Reconstruction, submitted with Job ID: $JOB1_ID"
fi

# --- Step 2: Segmentation ---
if [ "$SKIP" == "skip-segmentation" ]; then
    echo "Skipping Step 2: LongiSeg"
    JOB2_ID=$JOB1_ID
else
    # Build dependency string: only add it if JOB1_ID is not empty
    DEP1=""
    if [ ! -z "$JOB1_ID" ]; then DEP1="--dependency=afterok:$JOB1_ID"; fi

    JOB2_ID=$(sbatch --parsable $DEP1 segmentation_module/inference_module/run_inference_pipeline.sh "$SUBJECT" "$SESSION" "$ZIP_SERVER_PATH" "$LOCAL_ZIP_DST" "$DATASET_ID" "$DATASET_NAME" "$TRAINER")
    echo "Step 2, LongiSeg Segmentation, submitted with Job ID: $JOB2_ID"
fi

# --- Step 3: Surface Extraction ---
if [ "$SKIP" == "skip-extraction" ]; then
    echo "Skipping Step 3: Surface Extraction"
else
    # Build dependency string: use JOB2_ID if Step 2 ran, or JOB1_ID if Step 2 was skipped
    DEP2=""
    if [ ! -z "$JOB2_ID" ]; then DEP2="--dependency=afterok:$JOB2_ID"; fi

    JOB3_ID=$(sbatch --parsable $DEP2 extraction_module/run_extraction_pipeline.slurm "$SUBJECT" "$SESSION")
    echo "Step 3, Surface Extraction, submitted with Job ID: $JOB3_ID"
fi

echo "All jobs submitted successfully."