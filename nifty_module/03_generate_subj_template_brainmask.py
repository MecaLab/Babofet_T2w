import os
from pathlib import Path
import re
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def write_slurm_file(
        slurm_filename,
        fullname_subj,
        base_path,
        masks,
        dir_output_recon_template_space):

    slurm_content = f"""#!/bin/sh

#SBATCH -J babofet_gen_bm
#SBATCH -p batch
#SBATCH -w niolon13
#SBATCH --mem-per-cpu=48G
#SBATCH --time=20:00
#SBATCH -N 1
#SBATCH -o logs/gen_bm_{fullname_subj}.out
#SBATCH -e logs/gen_bm{fullname_subj}.err

MASK_PATH="{base_path}"

OUTPUT_PATH="{dir_output_recon_template_space}"
"""
    slurm_content += "\n"
    for i, file in enumerate(masks, start=1):
        slurm_content += f"MASK_FILE{i}=\"{file}\"\n"

    mask_stacks = " ".join(["/data/$MASK_FILE{}".format(i) for i in range(1, len(masks) + 1)])

    slurm_content += f"""
singularity exec \\
    -B "$MASK_PATH":/data \\
    -B "$OUTPUT_PATH":/output \\
    /scratch/lbaptiste/softs/niftymic.multifact_latest.sif \\
    niftymic_reconstruct_volume_from_slices \\
        --filenames {mask_stacks} \\
        --dir-input-mc /output/motion_correction \\
        --output /output/srr_template_mask.nii.gz \\
        --reconstruction-space /output/srr_template.nii.gz \\
        --alpha 1 \\
        --isotropic-resolution 0.5 \\
        --mask \\
        --sda \\
"""

    with open(slurm_filename, "w", encoding="utf-8") as slurm_file:
        slurm_file.write(slurm_content)

    os.chmod(slurm_filename, 0o700)


def get_bids_brain_masks(folder_path, subject, session):
    directory = Path(folder_path)

    # Regex pattern to match the dynamic parts
    # \d+ matches one or more digits for the run number (the 'XX')
    # \.nii\.gz matches the specific file extension
    regex_pattern = rf"sub-{subject}_ses-{session}_acq-haste_run-\d+_desc-brain_mask\.nii\.gz"

    # Compile the pattern for efficient matching
    pattern = re.compile(regex_pattern)

    # List and filter files in the specified directory
    matching_files = [
        file.name for file in directory.iterdir()
        if file.is_file() and pattern.match(file.name)
    ]

    return sorted(matching_files)

if __name__ == "__main__":

    base_path = cfg.DERIVATIVES_BIDS_PATH

    slurm_dir = "slurm_files"
    if not os.path.exists(slurm_dir):
        os.makedirs(slurm_dir)

    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    subject = "sub-Aziza"
    session = "ses-02"
    fullname_subj = f"{subject}_{session}"
    slurm_filename = f"{slurm_dir}/gen_brainmask_{fullname_subj}.slurm"

    subj_recons_path = os.path.join(base_path, "niftymic", subject, session, "reconstruction_niftymic")
    if not os.path.exists(subj_recons_path):
        print(f"Subject reconstruction path does not exist: {subj_recons_path}")
        sys.exit(1)

    recon_template_space_dir = os.path.join(subj_recons_path, "recon_template_space")
    if not os.path.exists(recon_template_space_dir):
        print(f"Reconstruction template space directory does not exist: {recon_template_space_dir}")
        sys.exit(1)

    masks_path = os.path.join(base_path, "niftymic", subject, session, "anat")
    if not os.path.exists(masks_path):
        print(f"Brain masks path does not exist: {masks_path}")
        sys.exit(1)

    masks_stacks = get_bids_brain_masks(masks_path, subject, session)
    if not masks_stacks:
        print(f"No brain mask files found in {masks_path} for subject {subject} and session {session}")
        sys.exit(1)

    write_slurm_file(
        slurm_filename,
        fullname_subj,
        base_path,
        masks_stacks,
        recon_template_space_dir)

    # subprocess.run(["sbatch", "slurm_files/niftymic_reconstruct_3D_mask.slurm"])
