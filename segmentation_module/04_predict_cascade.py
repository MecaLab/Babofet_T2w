import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_longiseg_cascade(base_input, final_output, filename, dataset_id, trainer, model_path, start_ses, end_ses,
                           partition="volta"):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")

    slurm_content = f"""#!/bin/bash

#SBATCH --account='b219'
#SBATCH --partition={partition}
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH -c 12
#SBATCH -o cascade_%j.out
#SBATCH -e cascade_%j.err

module purge
module load userspace/all gcc/14.1.0 cuda/12.4
source ~/.bashrc
conda activate longiseg_new

# --- CONFIGURATION ---
BASE_INPUT="{base_input}"
FINAL_DEST="{final_output}"
mkdir -p "$FINAL_DEST"

WORK_DIR="work_longiseg_$SLURM_JOB_ID"
mkdir -p "$WORK_DIR"

# Initialisation du dossier d'entrée
CURRENT_INPUT="$WORK_DIR/step_input"
mkdir -p "$CURRENT_INPUT"
cp "$BASE_INPUT"/*.nii.gz "$CURRENT_INPUT/"

# --- BOUCLE DE CASCADE ---
for (( s={start_ses}; s<{end_ses}; s++ ))
do
    CURR_STR=$(printf "%02d" $s)
    NEXT_S=$((s + 1))
    NEXT_STR=$(printf "%02d" $NEXT_S)

    echo ">>> CASCADE STEP: Predisant session $NEXT_STR depuis $CURR_STR"

    STEP_OUT="$WORK_DIR/out_ses_$NEXT_STR"
    mkdir -p "$STEP_OUT"

    # 1. GÉNÉRATION DYNAMIQUE DU PATIENTS.JSON
    # On scanne le dossier CURRENT_INPUT pour lister les patients présents pour cette session précise
    JSON_PATH="$WORK_DIR/patients_step.json"
    python3 -c "
import os, json
files = [f for f in os.listdir('$CURRENT_INPUT') if f.endswith('.nii.gz')]
patients = {{}}
for f in files:
    # On suppose le format: PatientID_sesXX_0000.nii.gz
    parts = f.split('_ses')
    if len(parts) > 1:
        p_id = parts[0]
        patients[p_id] = ['ses$CURR_STR']
with open('$JSON_PATH', 'w') as jout:
    json.dump(patients, jout)
"

    # 2. INFERENCE LONGISEG
    LongiSeg_predict -i "$CURRENT_INPUT" -o "$STEP_OUT" -d {dataset_id} -c 3d_fullres -tr {trainer} -f 0 1 2 3 4 --save_probabilities -pat "$JSON_PATH"

    # 3. POST-PROCESSING
    LongiSeg_apply_postprocessing -i "$STEP_OUT" -o "$STEP_OUT" -pp_pkl_file {pkl_file} -np 8 -plans_json {plans_json}

    # 4. SAUVEGARDE ET PRÉPARATION DU STEP SUIVANT
    cp "$STEP_OUT"/*.nii.gz "$FINAL_DEST/"

    # On prépare le nouveau dossier d'entrée pour l'itération s+1
    NEXT_INPUT_DIR="$WORK_DIR/step_input_next"
    mkdir -p "$NEXT_INPUT_DIR"

    for f in "$STEP_OUT"/*.nii.gz; do
        fname=$(basename "$f" .nii.gz)
        # On remplace 'ses05' par 'ses06' et on force le suffixe modalité _0000
        new_name=$(echo "$fname" | sed "s/ses$CURR_STR/ses$NEXT_STR/")
        cp "$f" "$NEXT_INPUT_DIR/${{new_name}}_0000.nii.gz"
    done

    # Rotation des dossiers
    rm -rf "$CURRENT_INPUT"
    mv "$NEXT_INPUT_DIR" "$CURRENT_INPUT"
    rm -rf "$STEP_OUT"
done

rm -rf "$WORK_DIR"
echo "Cascade LongiSeg terminée."
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)
    os.chmod(filename, 0o700)
    print(f"Script de cascade généré : {filename}")
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)
    os.chmod(filename, 0o700)

if __name__ == "__main__":
    dataset_name = "Dataset001_FirstTry"
    trainer = "LongiSegTrainerDiffWeighting"
    model_path = os.path.join(cfg.LONGISEG_RESULTS_PATH, dataset_name, f"{trainer}__nnUNetPlans__3d_fullres")

    base_input = "tmp_borgne_data"
    final_output = "tmp_borgne_data/results_cascade"

    write_longiseg_cascade(
         base_input=base_input,
         final_output=final_output,
         filename="slurm_files/run_cascade.slurm",
         dataset_id=1,
         trainer=trainer,
         model_path="/path/to/model",
         start_ses=5,
         end_ses=10
    )

    subprocess.run(["sbatch", "slurm_files/run_cascade.slurm"])
