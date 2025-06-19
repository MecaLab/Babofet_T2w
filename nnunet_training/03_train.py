import os
import subprocess

def write_slurm_file():
    filename = "slurm_files/nnunet_training.slurm"
    slurm_content = f"""#!/bin/bash


#SBATCH --account='b219'
#SBATCH --partition=volta
#SBATCH --time=6:00:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=48G
#SBATCH -o nnunet_training.out
#SBATCH -e nnunet_training.err

source ~/.bashrc
conda activate nnunet

nnUNet_train 3d_fullres nnUNetTrainerV2 001 4 --npz
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    print("Starting training")
    write_slurm_file()
    subprocess.run(["sbatch", "slurm_files/nnunet_training.slurm"])



