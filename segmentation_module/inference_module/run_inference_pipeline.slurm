#!/bin/bash
#SBATCH -J inference_pipeline
#SBATCH -p batch
#SBATCH --mem-per-cpu=48G
#SBATCH --time=12:00:00
#SBATCH -c 8
#SBATCH -o logs/inference_wrapper_%j.out
#SBATCH -e logs/inference_wrapper_%j.err

if [ "$#" -lt 7 ]; then
    echo "Usage: sbatch run_inference_pipeline.slurm <subject> <session> <zip_server_path> <local_zip_dst> <dataset_id> <dataset_name> <trainer_class>"
    exit 1
fi

SUBJECT=$1
SESSION=$2
ZIP_SERVER_PATH=$3
LOCAL_ZIP_DST=$4
DATASET_ID=$5
DATASET_NAME=$6
TRAINER=$7

DATASET_ID_PADDED=$(printf "%03d" $DATASET_ID)

echo "=================================================================="
echo "Starting Inference Pipeline for Subject: $SUBJECT"
echo "=================================================================="

source ~/.bashrc
conda activate longiseg

mkdir -p logs

echo "Step 1: Retrieving and unzipping model..."
python segmentation_module/inference_module/01_retrieve_model.py \
    --zip_server_path "$ZIP_SERVER_PATH" \
    --local_zip_dst "$LOCAL_ZIP_DST"

echo "Step 2: Preparing data..."
python segmentation_module/inference_module/02_prepare_data.py \
    --subject "$SUBJECT" \
    --session "$SESSION"

DERIVATIVES_BIDS_PATH=$(python -c "import configuration as cfg; print(cfg.DERIVATIVES_BIDS_PATH)")
LONGISEG_RESULTS_PATH=$(python -c "import configuration as cfg; print(cfg.LONGISEG_RESULTS_PATH)")

# Chemins pour LongiSeg
INPUT_FOLDER="$DERIVATIVES_BIDS_PATH/intermediate/longiseg/inference_data"
PATIENTS_JSON_PATH="$INPUT_FOLDER/patientsTs.json"
OUTPUT_FOLDER="$INPUT_FOLDER/res_seg"

MODEL_PATH="$LONGISEG_RESULTS_PATH/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}/${TRAINER}__nnUNetPlans__3d_fullres"
CROSSVAL_PATH="$MODEL_PATH/crossval_results_folds_0_1_2_3_4"
PKL_FILE="$CROSSVAL_PATH/postprocessing.pkl"
PLANS_JSON="$CROSSVAL_PATH/plans.json"

mkdir -p "$OUTPUT_FOLDER"

echo "Step 3: Running LongiSeg prediction..."
LongiSeg_predict -i "$INPUT_FOLDER" -o "$OUTPUT_FOLDER" -d "$DATASET_ID" -c 3d_fullres -tr "$TRAINER" -f 0 1 2 3 4 --save_probabilities -pat "$PATIENTS_JSON_PATH" -device cpu

echo "Step 4: Applying post-processing..."
LongiSeg_apply_postprocessing -i "$OUTPUT_FOLDER" -o "$OUTPUT_FOLDER" -pp_pkl_file "$PKL_FILE" -np 8 -plans_json "$PLANS_JSON"

echo "Step 5: Moving and renaming prediction files..."
python segmentation_module/inference_module/03_move_pred.py

echo "=================================================================="
echo "Inference pipeline completed successfully."
echo "=================================================================="