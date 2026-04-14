#!/bin/bash

# This script runs the full inference pipeline: model retrieval, data preparation, and CPU inference.
# It should be run from the login node (e.g., inside a tmux or screen session).

if [ "$#" -lt 5 ]; then
    echo "Usage: ./run_inference_pipeline.sh <zip_server_path> <local_zip_dst> <dataset_id> <dataset_name> <trainer_class>"
    echo "Example: ./run_inference_pipeline.sh /scratch/lbaptiste/LongiSeg/results/Dataset001_Name.zip ./models/Dataset001_Name.zip 1 Name LongiSegTrainerDiffWeighting"
    exit 1
fi

ZIP_SERVER_PATH=$1
LOCAL_ZIP_DST=$2
DATASET_ID=$3
DATASET_NAME=$4
TRAINER=$5

DATASET_ID_PADDED=$(printf "%03d" $DATASET_ID)

echo "=================================================================="
echo "Setting up environment..."
echo "=================================================================="
source ~/.bashrc
conda activate longiseg

mkdir -p logs

echo "Retrieving paths from configuration.py..."
DERIVATIVES_BIDS_PATH=$(python -c "import configuration as cfg; print(cfg.DERIVATIVES_BIDS_PATH)")
LONGISEG_RESULTS_PATH=$(python -c "import configuration as cfg; print(cfg.LONGISEG_RESULTS_PATH)")

echo "=================================================================="
echo "Step 1: Retrieving and unzipping model..."
echo "=================================================================="
python 01_retrieve_model.py --server_path "$ZIP_SERVER_PATH" --dst_path "$LOCAL_ZIP_DST"
if [ $? -ne 0 ]; then echo "Error in Step 1: Model Retrieval"; exit 1; fi

echo "=================================================================="
echo "Step 2: Preparing inference data..."
echo "=================================================================="
# This step now moves the NIfTI files AND generates patientsTs.json
python 02_prepare_data.py
if [ $? -ne 0 ]; then echo "Error in Step 2: Data Preparation"; exit 1; fi

echo "=================================================================="
echo "Step 3: Predicting on test set (submitting CPU job and waiting)..."
echo "=================================================================="
INPUT_FOLDER="$DERIVATIVES_BIDS_PATH/intermediate/nnunet/inference_data"
PATIENTS_JSON_PATH="$INPUT_FOLDER/patientsTs.json"
OUTPUT_FOLDER="$INPUT_FOLDER/res_seg"
MODEL_PATH="$LONGISEG_RESULTS_PATH/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}/${TRAINER}__nnUNetPlans__3d_fullres"
CROSSVAL_PATH="$MODEL_PATH/crossval_results_folds_0_1_2_3_4"
PKL_FILE="$CROSSVAL_PATH/postprocessing.pkl"
PLANS_JSON="$CROSSVAL_PATH/plans.json"

mkdir -p "$OUTPUT_FOLDER"

PRED_SLURM_FILE="longiseg_prediction.slurm"
cat << EOF > $PRED_SLURM_FILE
#!/bin/bash
#SBATCH -J longiseg_predict
#SBATCH -p batch
#SBATCH -w niolon13
#SBATCH --mem-per-cpu=48G
#SBATCH --time=10:00:00
#SBATCH -c 1
#SBATCH -o logs/predict_longiseg_%j.out
#SBATCH -e logs/predict_longiseg_%j.err

source ~/.bashrc
conda activate longiseg
export PYTHONPATH=\$PYTHONPATH:\$(pwd)

echo "Running prediction on CPU..."
LongiSeg_predict -i $INPUT_FOLDER -o $OUTPUT_FOLDER -d $DATASET_ID -c 3d_fullres -tr $TRAINER -f 0 1 2 3 4 --save_probabilities -pat $PATIENTS_JSON_PATH -device cpu

echo "Applying post-processing..."
LongiSeg_apply_postprocessing -i $OUTPUT_FOLDER -o $OUTPUT_FOLDER -pp_pkl_file $PKL_FILE -np 8 -plans_json $PLANS_JSON
EOF

sbatch --wait $PRED_SLURM_FILE
if [ $? -ne 0 ]; then echo "Error in Step 3: Inference"; exit 1; fi
echo "Inference finished."

echo "=================================================================="
echo "Pipeline completed successfully!"
echo "=================================================================="