#!/bin/bash

# Check arguments if your scripts need them
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

echo "Submitting pipeline jobs..."

# Submit Step 1 and capture its Job ID using --parsable
# --parsable forces sbatch to output ONLY the job ID
JOB1_ID=$(sbatch --parsable nifty_module/run_pipeline_niftymic.slurm "$SUBJECT" "$SESSION")
echo "Step 1 submitted with Job ID: $JOB1_ID"

# Submit Step 2, setting a dependency on Step 1
# afterok means Step 2 will only start if Step 1 exits with code 0
JOB2_ID=$(sbatch --parsable --dependency=afterok:$JOB1_ID segmentation_module/inference_module/run_inference_pipeline.sh "$SUBJECT" "$SESSION")
echo "Step 2 submitted with Job ID: $JOB2_ID"

# Submit Step 3, setting a dependency on Step 2
JOB3_ID=$(sbatch --parsable --dependency=afterok:$JOB2_ID extraction_module/run_extraction_pipeline.slurm "$SUBJECT" "$SESSION")
echo "Step 3 submitted with Job ID: $JOB3_ID"

echo "All jobs submitted successfully."