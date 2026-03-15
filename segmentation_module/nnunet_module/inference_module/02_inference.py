import os
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def write_slurm_file(input_folder, output_folder, filename, dataset_id, trainer, model_path):
    cross_val_path = os.path.join(model_path, f"crossval_results_folds_0_1_2_3_4")
    pkl_file = os.path.join(cross_val_path, "postprocessing.pkl")
    plans_json = os.path.join(cross_val_path, "plans.json")
    slurm_content = f"""#!/bin/bash

#SBATCH -J nnunet_predict
#SBATCH -p batch
#SBATCH -w niolon13
#SBATCH --mem-per-cpu=48G
#SBATCH --time=2:00:00
#SBATCH -c 1
#SBATCH -o logs/predict_nnunet_%j.out
#SBATCH -e logs/predict_nnunet_%j.err

source ~/.bashrc
conda activate nnunet

nnUNetv2_find_best_configuration {dataset_id} -c 3d_fullres -tr {trainer} -f 0 1 2 3 4

nnUNetv2_predict -i {input_folder} -o {output_folder} -d {dataset_id} -c 3d_fullres -tr {trainer} -f 0 1 2 3 4 -p nnUNetPlans

nnUNetv2_apply_postprocessing -i {output_folder} -o {output_folder} -pp_pkl_file {pkl_file} -np 8 -plans_json {plans_json}
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)

if __name__ == "__main__":
    id_dataset = int(sys.argv[1])
    name = sys.argv[2]
    trainer = sys.argv[3]  # "nnUNetTrainerBias_Xepochs"

    dataset_name = f"Dataset{id_dataset:03d}_{name}"

    input_folder = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "nnunet", "inference_dataset")
    output_folder = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "nnunet", "inference_predictions", dataset_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    model_path = cfg.NNUNET_RESULTS_PATH
    slurm_filename = "nnunet_predict.slurm"

    write_slurm_file(input_folder, output_folder, slurm_filename, id_dataset, trainer, model_path)
    subprocess.run(["sbatch", slurm_filename])

