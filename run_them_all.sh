#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: ./run_them_all.sh SUBJECT SESSION_ID"
    exit 1
fi

SUBJECT=$1
SESSION=$2

ZIP_SERVER_PATH="/scratch/lbaptiste/LongiSeg/results/Dataset003_FullSessions.zip"
LOCAL_ZIP_DST="/envau/work/meca/data/babofet_DB/2024_new_stuff/Dataset003_FullSessions.zip"
DATASET_ID="3"
DATASET_NAME="FullSessions"
TRAINER="LongiSegTrainerDiffWeighting"
MODE_SURF_EXTRACTION="viz"

echo "Submitting pipeline jobs..."

# Step 1: Niftymic
JOB1_ID=$(sbatch --parsable nifty_module/run_pipeline_niftymic.slurm "$SUBJECT" "$SESSION")
if [ -z "$JOB1_ID" ]; then echo "Failed to submit Step 1"; exit 1; fi
echo "Step 1 submitted: $JOB1_ID"

# Step 2: Inference (Will now wait for internal job because of --wait)
JOB2_ID=$(sbatch --parsable --dependency=afterok:$JOB1_ID segmentation_module/inference_module/run_inference_pipeline.slurm "$SUBJECT" "$SESSION" "$ZIP_SERVER_PATH" "$LOCAL_ZIP_DST" "$DATASET_ID" "$DATASET_NAME" "$TRAINER")if [ -z "$JOB2_ID" ]; then echo "Failed to submit Step 2"; exit 1; fi
if [ -z "$JOB2_ID" ]; then echo "Failed to submit Step 2"; exit 1; fi
echo "Step 2 submitted: $JOB2_ID"

# Step 3: Extraction (Will now wait for Step 2 correctly)
JOB3_ID=$(sbatch --parsable --dependency=afterok:$JOB2_ID extraction_module/run_extraction_pipeline.slurm "$SUBJECT" "$MODE_SURF_EXTRACTION")
if [ -z "$JOB3_ID" ]; then echo "Failed to submit Step 3"; exit 1; fi
echo "Step 3 submitted: $JOB3_ID"

echo "All jobs submitted successfully."