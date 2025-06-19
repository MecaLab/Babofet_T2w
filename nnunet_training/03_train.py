import os
import subprocess

def write_slurm_file():
    filename = "slurm_files/nnunet_training.slurm"
    slurm_content = f"""#!/bin/bash


#SBATCH --account='b219'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=6:00:00
#SBATCH -c 12
#SBATCH -o nnunet_training.out
#SBATCH -e nnunet_training.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

nnUNetv2_train 001 3d_fullres 0 -tr nnUNetTrainer_100epochs --npz --c
nnUNetv2_train 001 3d_fullres 1 -tr nnUNetTrainer_100epochs --npz --c
nnUNetv2_train 001 3d_fullres 2 -tr nnUNetTrainer_100epochs --npz --c
nnUNetv2_train 001 3d_fullres 3 -tr nnUNetTrainer_100epochs --npz --c
nnUNetv2_train 001 3d_fullres 4 -tr nnUNetTrainer_100epochs --npz --c
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    print("Starting training")
    write_slurm_file()
    subprocess.run(["sbatch", "slurm_files/nnunet_training.slurm"])



