import sys
import os
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import torch
import numpy

# Autoriser les anciens objets picklés
torch.serialization.add_safe_globals([numpy.core.multiarray.scalar])


def write_slurm_file(dataset_id, trainer, filename, checkpoint_path):
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=volta
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

nnUNetv2_train {dataset_id} 3d_fullres all -tr {trainer} --npz -pretrained_weights {checkpoint_path}
"""
    # nnUNetv2_train {dataset_id} 3d_fullres all -tr {trainer} --npz
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    print("Starting fine tuning")

    dataset_id = sys.argv[1]
    trainer = sys.argv[2]  # "nnUNetTrainerBias_Xepochs"

    checkpoint_path = os.path.join(cfg.NNUNET_RESULTS_PATH, "Dataset008_MoreYoungData/nnUNetTrainerBias_3000epochs__nnUNetPlans__3d_fullres/fold_all/checkpoint_best.pth")

    filename = "slurm_files/nnunet_finetuning.slurm"
    write_slurm_file(dataset_id, trainer, filename, checkpoint_path)
    subprocess.run(["sbatch", filename])