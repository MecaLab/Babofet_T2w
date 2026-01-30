import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def get_actual_previous_session(subject, current_session, full_dict):
    """Trouve la session précédente réelle dans la liste des sessions disponibles."""
    sessions = sorted(full_dict[subject])
    idx = sessions.index(current_session)
    if idx > 0:
        return sessions[idx - 1]
    return None


import os


def write_slurm_cascade(base_input, final_output, filename, dataset_id, trainer, model_path, start_ses, end_ses,
                        partition="volta"):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")

    slurm_content = f"""#!/bin/bash
#SBATCH --account='b391'
#SBATCH --partition={partition}
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH -c 12
#SBATCH -o predict_cascade_%j.out
#SBATCH -e predict_cascade_%j.err

module purge
module load userspace/all 
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate longiseg_new

# Dossiers de travail temporaires
CURRENT_INPUT="{base_input}"
FINAL_DEST="{final_output}"
mkdir -p $FINAL_DEST

# Boucle de cascade de {start_ses} à {end_ses}
for (( s={start_ses}; s<{end_ses}; s++ ))
do
    # Formater les noms de sessions (ex: 05, 06...)
    NEXT_S=$((s + 1))
    CURR_STR=$(printf "%02d" $s)
    NEXT_STR=$(printf "%02d" $NEXT_S)

    echo "--- Prédiction de la session $NEXT_STR à partir de $CURR_STR ---"

    TMP_OUT="tmp_out_ses_$NEXT_STR"
    mkdir -p $TMP_OUT

    # 1. Inférence
    LongiSeg_predict -i $CURRENT_INPUT -o $TMP_OUT -d {dataset_id} -c 3d_fullres -tr {trainer} -f 0 1 2 3 4 -p nnUNetPlans

    # 2. Post-processing
    LongiSeg_apply_postprocessing -i $TMP_OUT -o $TMP_OUT -pp_pkl_file {pkl_file} -np 8 -plans_json {plans_json}

    # 3. Préparation pour le prochain tour
    # On déplace le résultat vers le dossier final
    cp $TMP_OUT/*.nii.gz $FINAL_DEST/

    # On prépare le dossier input du prochain tour : 
    # Le résultat 'Patient_ses05.nii.gz' doit devenir 'Patient_ses06_0000.nii.gz'
    NEXT_INPUT="input_ses_$NEXT_STR"
    mkdir -p $NEXT_INPUT

    for f in $TMP_OUT/*.nii.gz; do
        basename=$(basename "$f" .nii.gz)
        # On remplace l'ancienne session par la nouvelle dans le nom du fichier
        new_name=$(echo $basename | sed "s/ses$CURR_STR/ses$NEXT_STR/")
        cp "$f" "$NEXT_INPUT/${{new_name}}_0000.nii.gz"
    done

    # Mettre à jour le pointeur pour la prochaine itération
    CURRENT_INPUT=$NEXT_INPUT
    rm -rf $TMP_OUT
done

echo "Cascade terminée. Résultats dans $FINAL_DEST"
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)
    os.chmod(filename, 0o700)

if __name__ == "__main__":
    dataset_name = "Dataset001_FirstTry"
    trainer = "LongiSegTrainerDiffWeighting"
    model_path = os.path.join(cfg.LONGISEG_RESULTS_PATH, dataset_name, f"{trainer}__nnUNetPlans__3d_fullres")

    base_input = "tmp_borgne_data"
    final_output = "tmp_borgne_data/results_cascade"

    write_slurm_cascade(
         base_input=base_input,
         final_output=final_output,
         filename="slurm_files/run_cascade.slurm",
         dataset_id=1,
         trainer=trainer,
         model_path="/path/to/model",
         start_ses=5,
         end_ses=10
    )