import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def write_slurm_file(input_folder, output_folder, filename, dataset_id, trainer, model_path, partition="volta"):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")
    slurm_content = f"""#!/bin/bash
    
#SBATCH --account='b391'
#SBATCH --partition={partition}
#SBATCH --gres=gpu:1
#SBATCH --time=30:00
#SBATCH -c 1
#SBATCH -o predict_nnunet_%j.out
#SBATCH -e predict_nnunet_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate longiseg_new
"""

    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)

def organize_files(subject, sessions, input_path, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for subject_ in os.listdir(input_path):
        if subject_ != subject:
            continue

        subject_input_dir = os.path.join(input_path, subject)
        for session in os.listdir(subject_input_dir):
            if session not in sessions:
                continue
            print(session)


if __name__ == "__main__":
    input_path = cfg.DATA_PATH
    output_path = "data_nnunet_longi/Borgne"
    sessions = ["ses06", "ses07", "ses08", "ses09", "ses10"]
    organize_files("Borgne", sessions, input_path, output_path)