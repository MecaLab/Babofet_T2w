import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


if __name__ == "__main__":
    base_path = cfg.MESO_DATA_PATH

    subject_IDs = os.listdir(base_path)
    subject_IDs.sort()
    print('subjects to be processed')
    print(subject_IDs)
    subject_processed_haste = list()
    subject_processed_truefisp = list()


# input_path = "/scratch/lbaptiste/data/dataset/babofet/subjects/sub-Aziza_ses-01/scans/10-T2_HASTE_AX2/resources/NIFTI/files"
# output_path = "/scratch/lbaptiste/data/dataset/babofet/output"
# input_file = "sub-Aziza_ses-01_T2_HASTE_AX2_10.nii"
# output_file = "mask.nii.gz"
#
# # Contenu du fichier SLURM
# slurm_script_content = f"""#!/bin/sh
#
# #SBATCH --account='a391'
# #SBATCH --partition=volta
# #SBATCH --gres=gpu:1
# #SBATCH --time=00:30:00
# #SBATCH -o tmp.out
# #SBATCH -e tmp.err
#
# module load userspace/all
# module load cuda/11.6
#
# singularity exec --nv -B "{input_path}":/data -B "{output_path}":/output softs/nesvor_latest.sif nesvor segment-stack --input-stacks "/data/{input_file}" --output-stack-masks "/output/{output_file}"
#
# echo "Running on: $SLURM_NODELIST"
# """
#
# # Écrire le contenu dans le fichier nesvor.slurm
# slurm_script_path = "nesvor.slurm"
# with open(slurm_script_path, "w", encoding="utf-8") as file:
#     file.write(slurm_script_content)
#
# # Soumettre le job à SLURM
# subprocess.run(["sbatch", slurm_script_path])