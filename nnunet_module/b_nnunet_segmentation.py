import sys
import os
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def nnunet_slurm_file():
    filename = "slurm_files/nnunet_segmentation.slurm"
    slurm_content = f"""#!/bin/sh

#SBATCH --account='b219'
#SBATCH --partition=volta
#SBATCH --gres=gpu:1
#SBATCH -c 10
#SBATCH --time=10:00

#SBATCH -e nnunet_pred-%j_3d_full_res.err
#SBATCH -o nnunet_pred-%j_3d_full_res.out

source ~/.bashrc
conda activate nnunet

module purge
module load userspace/all
module load cuda/11.6

nnUNetv2_predict -i /scratch/lbaptiste/data/nnUNet_raw/Dataset001_BrainSeg/imagesTr/ -o /scratch/lbaptiste/data/my_pred -d 006 -c 3d_fullres -f all
    """

    # ./mv_recons.sh {subj} {mode_bm} {suffix}
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)


if __name__ == "__main__":
    nnunet_slurm_file()

    subprocess.run(["sbatch", "slurm_files/nnunet_segmentation.slurm"])