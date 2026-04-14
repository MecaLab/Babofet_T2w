#!/bin/bash

# This script runs the full training pipeline, from data preparation to model export.
# It should be run from the login node (e.g., inside a tmux or screen session).

if [ "$#" -lt 3 ]; then
    echo "Usage: ./run_train_pipeline.sh <dataset_id> <dataset_name> <trainer_class> [train_partition] [pred_partition]"
    echo "Example: ./run_train_pipeline.sh 1 MyFetalDataset LongiSegTrainerDiffWeighting"
    exit 1
fi

DATASET_ID=$1
DATASET_NAME=$2
TRAINER=$3
TRAIN_PARTITION=${4:-volta}
PRED_PARTITION=${5:-volta}

# Zero-pad the dataset ID to 3 digits (e.g., 1 becomes 001)
DATASET_ID_PADDED=$(printf "%03d" $DATASET_ID)

echo "=================================================================="
echo "Setting up environment..."
echo "=================================================================="
module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4
source ~/.bashrc
conda activate longiseg_new

export PYTHONPATH=$PYTHONPATH:$(pwd)

mkdir -p logs
mkdir -p segmentation_module/train_module/slurm_files

echo "Retrieving paths from configuration.py..."
CODE_PATH=$(python -c "import configuration as cfg; print(cfg.CODE_PATH)")
LONGISEG_RAW_PATH_MESO=$(python -c "import configuration as cfg; print(cfg.LONGISEG_RAW_PATH_MESO)")
LONGISEG_RESULTS_PATH_MESO=$(python -c "import configuration as cfg; print(cfg.LONGISEG_RESULTS_PATH_MESO)")

echo "=================================================================="
echo "Step 1: Preparing dataset..."
echo "=================================================================="
# This step now also generates the patientsTs.json file directly.
python segmentation_module/train_module/01_prepare_dataset.py $DATASET_ID "$DATASET_NAME"
if [ $? -ne 0 ]; then echo "Error in Step 1: Prepare Dataset"; exit 1; fi

echo "=================================================================="
echo "Step 2: Training model (submitting job and waiting)..."
echo "=================================================================="
TRAIN_SLURM_FILE="segmentation_module/train_module/slurm_files/run_training.slurm"
cat << EOF > $TRAIN_SLURM_FILE
#!/bin/bash
#SBATCH --account='b391'
#SBATCH --partition=$TRAIN_PARTITION
#SBATCH --gres=gpu:1
#SBATCH --time=72:00:00
#SBATCH -c 12
#SBATCH --array=0-4
#SBATCH -o logs/training_longiseg_%A_%a.out
#SBATCH -e logs/training_longiseg_%A_%a.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4
source ~/.bashrc
conda activate longiseg_new
export PYTHONPATH=$PYTHONPATH:\$(pwd)

echo "Training fold \$SLURM_ARRAY_TASK_ID for Dataset $DATASET_ID"
LongiSeg_train $DATASET_ID 3d_fullres \$SLURM_ARRAY_TASK_ID -tr $TRAINER --npz
EOF

sbatch --wait $TRAIN_SLURM_FILE
if [ $? -ne 0 ]; then echo "Error in Step 2: Model Training"; exit 1; fi
echo "Training finished."

echo "=================================================================="
echo "Step 3: Predicting on test set (submitting job and waiting)..."
echo "=================================================================="
DATASET_DIR="$LONGISEG_RAW_PATH_MESO/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}"

INPUT_FOLDER="$DATASET_DIR/imagesTs"
PATIENTS_JSON_PATH="$DATASET_DIR/patientsTs.json"

OUTPUT_FOLDER="$CODE_PATH/snapshots/res_seg/pred_dataset_${DATASET_ID}"

MODEL_PATH="$LONGISEG_RESULTS_PATH_MESO/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}/${TRAINER}__nnUNetPlans__3d_fullres"
CROSSVAL_PATH="$MODEL_PATH/crossval_results_folds_0_1_2_3_4"
PKL_FILE="$CROSSVAL_PATH/postprocessing.pkl"
PLANS_JSON="$CROSSVAL_PATH/plans.json"

mkdir -p $OUTPUT_FOLDER

PRED_SLURM_FILE="segmentation_module/train_module/slurm_files/run_prediction.slurm"
cat << EOF > $PRED_SLURM_FILE
#!/bin/bash
#SBATCH --account='b391'
#SBATCH --partition=$PRED_PARTITION
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH -c 1
#SBATCH -o logs/predict_longiseg_%j.out
#SBATCH -e logs/predict_longiseg_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4
source ~/.bashrc
conda activate longiseg_new

echo "Finding best configuration..."
LongiSeg_find_best_configuration $DATASET_ID -c 3d_fullres -tr $TRAINER -f 0 1 2 3 4

echo "Running prediction..."
LongiSeg_predict -i $INPUT_FOLDER -o $OUTPUT_FOLDER -d $DATASET_ID -c 3d_fullres -tr $TRAINER -f 0 1 2 3 4 --save_probabilities -pat $PATIENTS_JSON_PATH

echo "Applying post-processing..."
LongiSeg_apply_postprocessing -i $OUTPUT_FOLDER -o $OUTPUT_FOLDER -pp_pkl_file $PKL_FILE -np 8 -plans_json $PLANS_JSON
EOF

sbatch --wait $PRED_SLURM_FILE
if [ $? -ne 0 ]; then echo "Error in Step 3: Prediction"; exit 1; fi
echo "Prediction finished."

echo "=================================================================="
echo "Step 4: Calculating metrics..."
echo "=================================================================="
python segmentation_module/train_module/03_metrics.py $DATASET_ID
if [ $? -ne 0 ]; then echo "Error in Step 4: Metrics Calculation"; exit 1; fi

echo "=================================================================="
echo "Step 5: Exporting model..."
echo "=================================================================="
MODEL_TO_EXPORT_PATH="$LONGISEG_RESULTS_PATH_MESO/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}"
python segmentation_module/train_module/04_export_model.py $MODEL_TO_EXPORT_PATH
if [ $? -ne 0 ]; then echo "Error in Step 5: Model Export"; exit 1; fi

echo "=================================================================="
echo "Pipeline completed successfully!"
echo "=================================================================="