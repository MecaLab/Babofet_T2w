import sys
import os
import subprocess


def write_slurm_file(dataset_id, trainer, filename):
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=kepler
#SBATCH --gres=gpu:1
#SBATCH --time=96:00:00
#SBATCH -c 12
#SBATCH -o training_nnunet_%j.out
#SBATCH -e training_nnunet_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate nnunet

export PYTHONPATH=$PYTHONPATH:/scratcj/lbaptiste/Babofet_T2w

cd $HOME

nnUNetv2_train {dataset_id} 3d_fullres 4 -tr {trainer} --npz --val 
"""
    # nnUNetv2_train {dataset_id} 3d_fullres $SLURM_ARRAY_TASK_ID -tr {trainer} --npz
    # nnUNetv2_train {dataset_id} 3d_fullres all -tr {trainer} --npz
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    print("Starting training")

    dataset_id = sys.argv[1]
    trainer = sys.argv[2]  # "nnUNetTrainerBias_Xepochs"

    filename = "slurm_files/nnunet_longi_train.slurm"
    write_slurm_file(dataset_id, trainer, filename)
    subprocess.run(["sbatch", filename])



