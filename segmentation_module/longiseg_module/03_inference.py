import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file(input_folder, output_folder, filename, patients_json_path, dataset_id, trainer):
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b219'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=10:00
#SBATCH -c 1
#SBATCH -o predict_longiseg_%j.out
#SBATCH -e predict_longiseg_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate longiseg

LongiSeg_predict -i {input_folder} -o {output_folder} -pat {patients_json_path} -d {dataset_id} -c 3d_fullres -tr {trainer} -f all --save_probabilities

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]  # "nnUNetTrainerBias_Xepochs"

    if dataset_id < 10:
        dataset_name = f"Dataset00{dataset_id}_{name}"
    elif dataset_id < 100:
        dataset_name = f"Dataset0{dataset_id}_{name}"
    else:
        dataset_name = f"Dataset{dataset_id}_{name}"

    base_folder = os.path.join(cfg.LONGISEG_RAW_PATH, dataset_name)
    patients_json = os.path.join(base_folder, "patientsTs.json")
    input_folder = os.path.join(base_folder, "imagesTs")

    output_folder = os.path.join(cfg.CODE_PATH, f"snapshots/longiseg_res/pred_dataset_{dataset_id}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Starting inference")

    filename = "slurm_files/longiseg_prediction.slurm"
    write_slurm_file(input_folder, output_folder, filename, patients_json, dataset_id, trainer)
    subprocess.run(["sbatch", "slurm_files/longiseg_prediction.slurm"])