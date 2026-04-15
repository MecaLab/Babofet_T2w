#!/bin/bash

# This script orchestrates the full training pipeline using SLURM dependencies.
# You can run this directly (no tmux required). It will submit the jobs and exit immediately.

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

mkdir -p logs
mkdir -p segmentation_module/train_module/slurm_files

echo "Retrieving paths from configuration.py..."
CODE_PATH=$(python -c "import configuration as cfg; print(cfg.CODE_PATH)")
LONGISEG_RAW_PATH_MESO=$(python -c "import configuration as cfg; print(cfg.LONGISEG_RAW_PATH_MESO)")
LONGISEG_RESULTS_PATH_MESO=$(python -c "import configuration as cfg; print(cfg.LONGISEG_RESULTS_PATH_MESO)")

echo "=================================================================="
echo "Step 1: Preparing dataset (Local Execution)..."
echo "=================================================================="
# This step runs synchronously because it is fast and necessary to build the jobs
python segmentation_module/train_module/01_prepare_dataset.py --dataset_id $DATASET_ID --name "$DATASET_NAME"
if [ $? -ne 0 ]; then echo "Error in Step 1: Prepare Dataset"; exit 1; fi

LongiSeg_plan_and_preprocess -d $DATASET_ID --verify_dataset_integrity

echo "=================================================================="
echo "Step 2: Submitting Training Job Array..."
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
#SBATCH -J train_Dataset$DATASET_ID
#SBATCH -o logs/training_longiseg_%A_%a.out
#SBATCH -e logs/training_longiseg_%A_%a.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4
source ~/.bashrc
conda activate longiseg_new

echo "Training fold \$SLURM_ARRAY_TASK_ID for Dataset $DATASET_ID"
LongiSeg_train $DATASET_ID 3d_fullres \$SLURM_ARRAY_TASK_ID -tr $TRAINER --npz
EOF

# Soumission du job d'entraînement et récupération de son ID
# --parsable permet de ne retourner que le numéro (ex: 123456) au lieu de "Submitted batch job 123456"
TRAIN_JOB_ID=$(sbatch --parsable $TRAIN_SLURM_FILE)
echo "Training Job Array submitted successfully! Job ID: $TRAIN_JOB_ID"


echo "=================================================================="
echo "Step 3, 4 & 5: Submitting Post-Processing Job (Dependent on Training)..."
echo "=================================================================="
DATASET_DIR="$LONGISEG_RAW_PATH_MESO/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}"
INPUT_FOLDER="$DATASET_DIR/imagesTs"
PATIENTS_JSON_PATH="$DATASET_DIR/patientsTs.json"
OUTPUT_FOLDER="$CODE_PATH/snapshots/res_seg/pred_dataset_${DATASET_ID}"
MODEL_PATH="$LONGISEG_RESULTS_PATH_MESO/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}/${TRAINER}__nnUNetPlans__3d_fullres"
CROSSVAL_PATH="$MODEL_PATH/crossval_results_folds_0_1_2_3_4"
PKL_FILE="$CROSSVAL_PATH/postprocessing.pkl"
PLANS_JSON="$CROSSVAL_PATH/plans.json"
MODEL_TO_EXPORT_PATH="$LONGISEG_RESULTS_PATH_MESO/Dataset${DATASET_ID_PADDED}_${DATASET_NAME}"

mkdir -p $OUTPUT_FOLDER

POST_TRAIN_SLURM_FILE="segmentation_module/train_module/slurm_files/run_post_training.slurm"
cat << EOF > $POST_TRAIN_SLURM_FILE
#!/bin/bash
#SBATCH --account='b391'
#SBATCH --partition=$PRED_PARTITION
#SBATCH --gres=gpu:1
#SBATCH --time=01:30:00
#SBATCH -c 4
#SBATCH -J post_Dataset$DATASET_ID
#SBATCH -o logs/post_training_%j.out
#SBATCH -e logs/post_training_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4
source ~/.bashrc
conda activate longiseg_new
export PYTHONPATH=\$PYTHONPATH:\$(pwd)

echo "--- STEP 3: PREDICTION ---"
LongiSeg_find_best_configuration $DATASET_ID -c 3d_fullres -tr $TRAINER -f 0 1 2 3 4
LongiSeg_predict -i $INPUT_FOLDER -o $OUTPUT_FOLDER -d $DATASET_ID -c 3d_fullres -tr $TRAINER -f 0 1 2 3 4 --save_probabilities -pat $PATIENTS_JSON_PATH
LongiSeg_apply_postprocessing -i $OUTPUT_FOLDER -o $OUTPUT_FOLDER -pp_pkl_file $PKL_FILE -np 8 -plans_json $PLANS_JSON

echo "--- STEP 4: METRICS ---"
python segmentation_module/train_module/04_metrics.py --dataset_id $DATASET_ID

echo "--- STEP 5: EXPORT ---"
python segmentation_module/train_module/05_export_model.py --export_path "$MODEL_TO_EXPORT_PATH"

echo "Post-training pipeline completed successfully!"
EOF

# Soumission du job de post-traitement avec dépendance stricte sur l'entraînement
POST_JOB_ID=$(sbatch --parsable --dependency=afterok:$TRAIN_JOB_ID $POST_TRAIN_SLURM_FILE)
echo "Post-Processing Job submitted successfully! Job ID: $POST_JOB_ID"
echo "This job is queued and will ONLY start when Job $TRAIN_JOB_ID completes."

echo "=================================================================="
echo "Pipeline is fully delegated to SLURM. You can now close your terminal."
echo "Monitor your jobs using: squeue -u \$USER"
echo "=================================================================="