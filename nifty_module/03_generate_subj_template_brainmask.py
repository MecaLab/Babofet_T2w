import os
from pathlib import Path
import glob
import re
import sys
import shutil
import argparse
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def run_niftymic_mask_generation(mask_path, masks_stacks, output_dir, soft_path):
    mask_stacks_mapped = ["/data/" + f for f in masks_stacks]

    cmd = [
              "singularity", "exec",
              "-B", f"{mask_path}:/data",
              "-B", f"{output_dir}:/output",
              soft_path,
              "niftymic_reconstruct_volume_from_slices",
              "--filenames"] + mask_stacks_mapped + [
              "--dir-input-mc", "/output/motion_correction",
              "--output", "/output/srr_template_mask.nii.gz",
              "--reconstruction-space", "/output/srr_template.nii.gz",
              "--alpha", "1",
              "--isotropic-resolution", "0.5",
              "--mask",
              "--sda"
          ]

    print("Generating subject template brainmask...")
    subprocess.run(cmd, check=True)  # This waits until finished


def get_bids_brain_masks(folder_path, subject, session):
    directory = Path(folder_path)

    regex_pattern = rf"{subject}_{session}_acq-haste_run-\d+_desc-brain_mask\.nii\.gz"

    pattern = re.compile(regex_pattern)

    matching_files = [
        file.name for file in directory.iterdir()
        if file.is_file() and pattern.match(file.name)
    ]

    return sorted(matching_files)


def map_transformation_files(motion_correction_dir, mask_files):
    """
    Maps denoised volume and slice TFM files to match the naming
    convention of the input mask stacks.
    """
    available_tfms = glob.glob(os.path.join(motion_correction_dir, "*.tfm"))

    print(f"Mapping transformations in: {motion_correction_dir}")

    for mask_file in mask_files:
        # stack_base represents the name NiftyMIC expects (e.g., ..._desc-brain)
        stack_base = mask_file.replace("_mask.nii.gz", "")

        # Extract run identifier (e.g., 'run-01')
        run_match = re.search(r"run-(\d+)", stack_base)
        if not run_match:
            continue
        run_id = run_match.group(0)

        # Identify all source files for this run containing '_denoised'
        run_source_tfms = [f for f in available_tfms if run_id in f and "_denoised" in f]

        for src_path in run_source_tfms:
            src_name = os.path.basename(src_path)

            # Check for slice files or main volume files
            slice_match = re.search(r"_slice(\d+)\.tfm", src_name)

            if slice_match:
                slice_num = slice_match.group(1)
                dest_name = f"{stack_base}_slice{slice_num}.tfm"
            else:
                dest_name = f"{stack_base}.tfm"

            dest_path = os.path.join(motion_correction_dir, dest_name)

            if not os.path.exists(dest_path):
                shutil.copy(src_path, dest_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Denoise data for a specific subject and session.")
    parser.add_argument("--subject", required=True, help="Subject ID (e.g., sub-Aziza)")
    parser.add_argument("--session", required=True, help="Session ID (e.g., ses-01)")
    args = parser.parse_args()

    subject = args.subject
    session = args.session

    base_path = cfg.DERIVATIVES_BIDS_PATH
    niftymic_soft = os.path.join(cfg.SOFTS_PATH, "niftymic.multifact_latest.sif")

    subj_recons_path = os.path.join(base_path, "intermediate", "niftymic", subject, session, "reconstruction_niftymic")
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

    dir_motion_correction = os.path.join(recon_template_space_dir, "motion_correction")

    map_transformation_files(dir_motion_correction, masks_stacks)

    run_niftymic_mask_generation(
        mask_path=masks_path,
        masks_stacks=masks_stacks,
        output_dir=recon_template_space_dir,
        soft_path=niftymic_soft)
