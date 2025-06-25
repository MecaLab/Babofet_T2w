import os
import subprocess


def write_slurm_file(model_checkpoint_path):
    filename = "slurm_files/nnunet_finetuning.slurm"
    slurm_content = f"""#!/bin/bash


#SBATCH --account='b219'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=6:00:00
#SBATCH -c 12
#SBATCH -o nnunet_finetuning.out
#SBATCH -e nnunet_finetuning.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

nnUNetv2_train 002 3d_fullres all -tr nnUNetTrainer_10epochs --npz -pretrained_weights {model_checkpoint_path}
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    print("Starting fine-tuning")
    model_checkpoint_path = "/scratch/lbaptiste/data/nnUNet_trained_models/Dataset001_Babofet/nnUNetTrainer_100epochs__nnUNetPlans__3d_fullres/fold_all/checkpoint_final.pth"
    write_slurm_file(model_checkpoint_path)
    subprocess.run(["sbatch", "slurm_files/nnunet_finetuning.slurm"])



