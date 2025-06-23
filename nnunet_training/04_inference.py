import os
import subprocess

def write_slurm_file(input_folder, output_folder):
    filename = "slurm_files/nnunet_prediction.slurm"
    slurm_content = f"""#!/bin/bash


#SBATCH --account='b219'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=10:00
#SBATCH -c 12
#SBATCH -o nnunet_predict.out
#SBATCH -e nnunet_predict.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

nnUNetv2_predict -i {input_folder} -o {output_folder} -d 1 -c 3d_fullres -tr nnUNetTrainer_100epochs -f all

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    input_folder = "/scratch/lbaptiste/Babofet_T2w/pred_nnunet/"
    output_folder = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/"

    print("Starting inference")
    write_slurm_file(input_folder, output_folder)
    subprocess.run(["sbatch", "slurm_files/nnunet_prediction.slurm"])