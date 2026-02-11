import subprocess
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file(subject, filename, sessions, output_path, trainer):
    sorted_sessions = sorted(sessions)
    sessions_str = " ".join(sorted_sessions)

    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=2:00:00
#SBATCH -c 12
#SBATCH -o logs/pred_{trainer}_{subject}_%j.out
#SBATCH -e logs/pred_{trainer}_{subject}_%j.err

source ~/.bashrc
conda activate longiseg_new

# --- CONFIGURATION ---
INPUT_DIR="/scratch/lbaptiste/Babofet_T2w/results_seg/{trainer.lower()}/{subject}"
OUTPUT_DIR={output_path}
PATIENT_JSON="${{OUTPUT_DIR}}/patientsTr.json"

MODEL_FOLDER="/scratch/lbaptiste/data/LongiSeg_results/Dataset001_FirstTry/{trainer}__nnUNetPlans__3d_fullres"
PKL_FILE="${{MODEL_FOLDER}}/crossval_results_folds_0_1_2_3_4/postprocessing.pkl"
PLANS_JSON="${{MODEL_FOLDER}}/crossval_results_folds_0_1_2_3_4/plans.json"

mkdir -p "$OUTPUT_DIR"
SESSIONS=({sessions_str})

for t in "${{SESSIONS[@]}}"
do
    echo "--- Processing Timepoint $t ---"

    TMP_IN="${{OUTPUT_DIR}}/tmp_in_$t"
    TMP_OUT="${{OUTPUT_DIR}}/tmp_out_$t"
    mkdir -p "$TMP_IN" "$TMP_OUT"

    cp "${{INPUT_DIR}}/{subject}_${{t}}_0000.nii.gz" "${{TMP_IN}}/{subject}_${{t}}_0000.nii.gz"

    LongiSeg_predict -i "$TMP_IN" \\
                     -o "$TMP_OUT" \\
                     -d 1 \\
                     -c 3d_fullres \\
                     -f 0 1 2 3 4 \\
                     --save_probabilities \\
                     -tr {trainer} \\
                     -pat "$PATIENT_JSON"

    LongiSeg_apply_postprocessing -i "$TMP_OUT" \\
                                  -o "$TMP_OUT" \\
                                  -pp_pkl_file "$PKL_FILE" \\
                                  -np 8 \\
                                  -plans_json "$PLANS_JSON"

    mv "${{TMP_OUT}}/{subject}_${{t}}.nii.gz" "${{OUTPUT_DIR}}/{subject}_${{t}}.nii.gz"

    rm -rf "$TMP_IN" "$TMP_OUT"
done

echo "Toutes les segmentations ont été générées dans $OUTPUT_DIR"
"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)
    os.chmod(filename, 0o755)

def prepare_folder(subject, sessions, input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for session in sessions:
        input_path = os.path.join(input_dir, f"{subject}_{session}_0000.nii.gz")
        output_path = os.path.join(output_dir, f"{subject}_{session}_0000.nii.gz")
        if not os.path.exists(input_path):
            print(f"Warning: {input_path} does not exist. Please check the path.")
        else:
            os.system(f"cp {input_path} {output_path}")

    print("Input files have been copied to the output directory for prediction.")

def write_patients_json(subject, sessions, filename):
    data = {
        subject: [f"{subject}_{s}" for s in sessions]
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":

    subject = sys.argv[1]
    raw_sessions = sys.argv[2]
    trainer = sys.argv[3]

    sessions = [f"ses{item.strip()}" for item in raw_sessions.split(',')]

    print(f"Computing predictions for subject {subject} and sessions: \n{sessions}")
    input_dir = "inference_all"
    output_dir = os.path.join(cfg.CODE_PATH, "results_seg", f"{trainer.lower()}", subject)
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)

    prepare_folder(subject, sessions, input_dir, output_dir)
    write_patients_json(subject, sessions, os.path.join(output_dir, "patientsTr.json"))

    target_filename = f"slurm_files/predict_{subject}_{trainer}.slurm"
    write_slurm_file(subject, target_filename, sessions, output_dir, trainer)
    subprocess.run(["sbatch", target_filename])