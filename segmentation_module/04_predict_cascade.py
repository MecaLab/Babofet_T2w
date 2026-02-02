import subprocess
import os


def write_slurm_file(filename):
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=2:00:00
#SBATCH -c 12
#SBATCH -o pred_longiseg_%j.out
#SBATCH -e pred_longiseg_%j.err

# --- CONFIGURATION ---
INPUT_DIR="/scratch/lbaptiste/Babofet_T2w/tmp_borgne_data"
OUTPUT_DIR="/scratch/lbaptiste/Babofet_T2w/tmp_borgne_data/results_segmentations"
MODEL_FOLDER="/scratch/lbaptiste/data/LongiSeg_results/Dataset001_FirstTry/LongiSegTrainer__nnUNetPlans__3d_fullres"

PKL_FILE="${{MODEL_FOLDER}}/crossval_results_folds_0_1_2_3_4/postprocessing.pkl"
PLANS_JSON="${{MODEL_FOLDER}}/crossval_results_folds_0_1_2_3_4/plans.json"
PATIENT_JSON="/scratch/lbaptiste/Babofet_T2w/tmp_borgne_data/patientsTr.json"

mkdir -p "$OUTPUT_DIR"

# --- BOUCLE DE PRÉDICTION DES TIMEPOINTS ---
# On boucle sur les sessions existantes de 06 à 10
for t in 06 07 08 09 10
do
    echo "--- Processing Timepoint $t ---"

    # 1. Création d'un dossier temporaire propre pour ce timepoint
    TMP_IN="${{OUTPUT_DIR}}/tmp_in_$t"
    TMP_OUT="${{OUTPUT_DIR}}/tmp_out_$t"
    mkdir -p "$TMP_IN" "$TMP_OUT"

    # 2. Copie du volume correspondant (ex: Borgne_ses06_0000.nii.gz)
    # On le renomme pour que l'ID de sortie soit clair
    cp "${{INPUT_DIR}}/Borgne_ses${{t}}_0000.nii.gz" "${{TMP_IN}}/Borgne_t${{t}}_0000.nii.gz"

    # 3. Lancement de LongiSeg_predict
    LongiSeg_predict -i "$TMP_IN" \\
                     -o "$TMP_OUT" \\
                     -d 1 \\
                     -c 3d_fullres \\
                     -f 0 1 2 3 4 \\
                     --save_probabilities \\
                     -pat "$PATIENT_JSON"

    # 4. Post-processing (optionnel mais recommandé si calculé au training)
    LongiSeg_apply_postprocessing -i "$TMP_OUT" \\
                                  -o "$TMP_OUT" \\
                                  -pp_pkl_file "$PKL_FILE" \\
                                  -np 8 \\
                                  -plans_json "$PLANS_JSON"

    # 5. Déplacement vers le dossier final et nettoyage
    mv "${{TMP_OUT}}/Borgne_t${{t}}.nii.gz" "${{OUTPUT_DIR}}/seg_Borgne_t${{t}}.nii.gz"

    rm -rf "$TMP_IN" "$TMP_OUT"
done

echo "Toutes les segmentations ont été générées dans $OUTPUT_DIR"
"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)
    os.chmod(filename, 0o755)


if __name__ == "__main__":
    target_filename = "slurm_files/longiseg_predict_all_tp.slurm"
    write_slurm_file(target_filename)
    print(f"Fichier Slurm généré : {target_filename}")