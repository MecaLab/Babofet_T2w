import os
import subprocess
import sys
from collections import defaultdict
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file(input_folder, output_folder, filename, dataset_id, trainer, model_path, patients_json_path):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")
    slurm_content = f"""#!/bin/bash

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

LongiSeg_predict -i {input_folder} -o {output_folder} -d {dataset_id} -c 3d_fullres -tr {trainer} -f 0 1 2 3 4 --save_probabilities -pat {patients_json_path} -device cpu

LongiSeg_apply_postprocessing -i {output_folder} -o {output_folder} -pp_pkl_file {pkl_file} -np 8 -plans_json {plans_json}

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


def generate_patient_sessions_json(directory_path, output_filename="patientsTs.json"):
    # defaultdict handles the creation of lists for new keys automatically
    patient_data = defaultdict(list)

    if not os.path.exists(directory_path):
        print(f"Error: The directory '{directory_path}' does not exist.")
        return

    files = os.listdir(directory_path)
    files.sort()

    for filename in files:
        if filename.endswith(".nii.gz"):
            # Format: "Borgne_ses-01_0000.nii.gz"
            parts = filename.split('_')

            if len(parts) >= 2:
                patient_name = parts[0]
                session_id = parts[1] # This will capture "ses-01"

                session_entry = f"{patient_name}_{session_id}"

                if session_entry not in patient_data[patient_name]:
                    patient_data[patient_name].append(session_entry)

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(dict(patient_data), f, indent=4)

    print(f"File '{output_filename}' has been created successfully.")



if __name__ == "__main__":
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]  # LongiSegTrainerDiffWeighting  => 1000 epochs default

    dataset_name = f"Dataset{dataset_id:03d}_{name}"

    model_path = os.path.join(cfg.LONGISEG_RESULTS_PATH, dataset_name, f"{trainer}__nnUNetPlans__3d_fullres")

    input_folder = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "nnunet", "inference_data")
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder '{input_folder}' does not exist. Please prepare the data first by running the previous script")

    test_pred_json = os.path.join(input_folder, "patientsTs.json")
    generate_patient_sessions_json(directory_path=input_folder, output_filename=test_pred_json)

    output_folder = os.path.join(input_folder, "res_seg")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Starting inference")

    filename = "longiseg_prediction.slurm"
    write_slurm_file(input_folder, output_folder, filename, dataset_id, trainer, model_path, test_pred_json)
    subprocess.run(["sbatch", filename])