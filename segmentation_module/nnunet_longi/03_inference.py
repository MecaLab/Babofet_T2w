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

#SBATCH --account='b391'
#SBATCH --partition=pascal
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
conda activate nnunet

nnUNetv2_predict -i {input_folder} -o {output_folder} -d {dataset_id} -c 3d_fullres -tr {trainer} -f 0 1 2 3 4 --save_probabilities

nnUNetv2_apply_postprocessing -i {output_folder} -o {output_folder} -pp_pkl_file {pkl_file} -np 8 -plans_json {plans_json}


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

    model_path = os.path.join(cfg.NNUNET_RESULTS_PATH, dataset_name, f"{trainer}__nnUNetPlans__3d_fullres")

    input_folder = os.path.join(cfg.NNUNET_RAW_PATH, dataset_name, "imagesTs")

    # input_folder = os.path.join(cfg.CODE_PATH, "tmp_seg_input")
    output_folder = os.path.join(cfg.CODE_PATH, f"snapshots/nnunet_res/pred_dataset_{dataset_id}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Starting inference")

    filename = "slurm_files/nnunet_prediction.slurm"
    write_slurm_file(input_folder, output_folder, filename, dataset_id, trainer, model_path)
    subprocess.run(["sbatch", filename])