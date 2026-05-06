#!/bin/bash

# Check for required arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: ./run_them_all.sh SUBJECT SESSION_ID"
    exit 1
fi

SUBJECT=$1
SESSION=$2

# Global configuration variables
ZIP_SERVER_PATH="/scratch/lbaptiste/LongiSeg/results/Dataset003_FullSessions.zip"
LOCAL_ZIP_DST="/envau/work/meca/data/babofet_DB/2024_new_stuff/Dataset003_FullSessions.zip"
DATASET_ID="3"
DATASET_NAME="FullSessions"
TRAINER="LongiSegTrainerDiffWeighting"
MODE_SURF_EXTRACTION="viz"

echo "Submitting pipeline jobs..."

# ------------------------------------------------------------------------------
# Step 1: Niftymic Pipeline
# ------------------------------------------------------------------------------
JOB1_ID=$(sbatch --parsable nifty_module/run_pipeline_niftymic.slurm "$SUBJECT" "$SESSION")
if [ -z "$JOB1_ID" ]; then
    echo "Failed to submit Step 1"
    exit 1
fi
echo "Step 1 submitted: $JOB1_ID"

# ------------------------------------------------------------------------------
# Step 2: Inference Pipeline (Depends on Step 1)
# ------------------------------------------------------------------------------
JOB2_ID=$(sbatch --parsable --dependency=afterok:$JOB1_ID segmentation_module/inference_module/run_inference_pipeline.slurm "$SUBJECT" "$SESSION" "$ZIP_SERVER_PATH" "$LOCAL_ZIP_DST" "$DATASET_ID" "$DATASET_NAME" "$TRAINER")

if [ -z "$JOB2_ID" ]; then
    echo "Failed to submit Step 2"
    exit 1
fi
echo "Step 2 submitted: $JOB2_ID"

# ------------------------------------------------------------------------------
# Step 3: Surface Extraction (Depends on Step 2)
# ------------------------------------------------------------------------------
JOB3_ID=$(sbatch --parsable --dependency=afterok:$JOB2_ID extraction_module/run_extraction_pipeline.slurm "$SUBJECT" "$SESSION" "$MODE_SURF_EXTRACTION")

if [ -z "$JOB3_ID" ]; then
    echo "Failed to submit Step 3"
    exit 1
fi
echo "Step 3 submitted: $JOB3_ID"

echo "------------------------------------------------------------------------------"
echo "All jobs submitted successfully."
echo "Workflow: $JOB1_ID -> $JOB2_ID -> $JOB3_ID"
echo "------------------------------------------------------------------------------"