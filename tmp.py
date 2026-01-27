import os
import sys
import configuration as cfg
import subprocess

def write_slurm_file_nifty(denoised_files):
    filename = "slurm_files/tmp_nifty_reconstruction.slurm"
    slurm_content = f"""#!/bin/sh

#SBATCH --account='b219'
#SBATCH --partition=skylake
#SBATCH --time=24:00:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=48G
#SBATCH -o recon_pipeline_niftymic_tmp.out
#SBATCH -e recon_pipeline_niftymic_tmp.err

MAIN_PATH="/scratch/lbaptiste/data/tmp_data/"

OUTPUT_PATH="HYPE00_tmp"
MOTION_CORRECTION="${{OUTPUT_PATH}}/motion_correction"
OUTPUT_FILE="srr_3d_tmp.nii.gz"

TEMPLATE_PATH="/scratch/lbaptiste/data/atlas_fetal_rhesus/"
"""

    slurm_content += "\n"
    for i, file in enumerate(denoised_files, start=1):
        slurm_content += f"INPUT_FILE{i}=\"{file}\"\n"

    slurm_content += "\n"

    input_stacks = " ".join(["/data/$INPUT_FILE{}".format(i) for i in range(1, len(denoised_files) + 1)])

    slurm_content += f"""
singularity exec \\
    -B "MAIN_PATH":/data \\
    -B "$OUTPUT_PATH":/output \\
    -B "$TEMPLATE_PATH":/template \\
    /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
    niftymic_run_reconstruction_pipeline \\
        --filenames {input_stacks} \\
        --dir-output /output/ \\
        --isotropic-resolution 0.8 \\
        --bias-field-correction 0 \\

"""
    with open(filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(filename, 0o700)

if __name__ == "__main__":
    denoised_files = os.listdir("/scratch/lbaptiste/data/tmp_data/")
    write_slurm_file_nifty(denoised_files)
    print("lets go")
    subprocess.run(["sbatch", "slurm_files/tmp_nifty_reconstruction.slurm"])


