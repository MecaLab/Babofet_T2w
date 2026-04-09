import sys
import os
import subprocess


def write_slurm_file(dataset_id, trainer, filename):
    slurm_content = f"""#!/bin/bash

#SBATCH --account='b391'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH --time=72:00:00
#SBATCH -c 12
#SBATCH --array=0-4   # Lance 5 jobs : fold 0 à 4
#SBATCH -o training_longiseg_%j.out
#SBATCH -e training_longiseg_%j.err

module purge
module load userspace/all
module load gcc/14.1.0
module load cuda/12.4

source ~/.bashrc
conda activate longiseg_new

export PYTHONPATH=$PYTHONPATH:/scratch/lbaptiste/Babofet_T2w/LongiSeg

LongiSeg_train {dataset_id} 3d_fullres $SLURM_ARRAY_TASK_ID {trainer} --npz 

LongiSeg_find_best_configuration {dataset_id} -c 3d_fullres -tr {trainer}
"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    print("Starting training")

    dataset_id = sys.argv[1]
    trainer = sys.argv[2]

    filename = "slurm_files/longiseg_train.slurm"
    write_slurm_file(dataset_id, trainer, filename)
    subprocess.run(["sbatch", filename])



