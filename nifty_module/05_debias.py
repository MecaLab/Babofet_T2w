import os
import shutil
import sys
import subprocess
import argparse
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    """
    N4BiasFieldCorrection -d 3 -i STACK_PATH -x MASK_PATH -o OUTPUT_PATH
    """
    parser = argparse.ArgumentParser(description="Denoise data for a specific subject and session.")
    parser.add_argument("--subject", required=True, help="Subject ID (e.g., sub-Aziza)")
    parser.add_argument("--session", required=True, help="Session ID (e.g., ses-01)")
    args = parser.parse_args()
    subject = args.subject
    session = args.session

    bias_field_correction_path = "/hpc/shared/apps/x86_64/softs/ANTS/2.3.4/bin/N4BiasFieldCorrection"  # path on niolon
    base_path = cfg.DERIVATIVES_BIDS_PATH

    print(f"Processing {subject} {session}...")

    subj_recons_path = os.path.join(base_path, "intermediate", "niftymic", subject, session, "reconstruction_niftymic")
    if not os.path.exists(subj_recons_path):
        print(f"Subject reconstruction path does not exist: {subj_recons_path}")
        sys.exit(1)

    recon_template_space_dir = os.path.join(subj_recons_path, "recon_template_space")
    if not os.path.exists(recon_template_space_dir):
        print(f"Reconstruction template space directory does not exist: {recon_template_space_dir}")
        sys.exit(1)

    stack_path = os.path.join(recon_template_space_dir, "srr_template.nii.gz")
    mask_path = os.path.join(recon_template_space_dir, "srr_template_mask.nii.gz")

    if not os.path.exists(stack_path):
        print(f"\tStack file {stack_path} does not exist, skipping...")
        exit()

    output_filename = os.path.join(recon_template_space_dir, "srr_template_debiased.nii.gz")
    if os.path.exists(output_filename):
        print(f"\tOutput file {output_filename} already exists, skipping...")
        exit()

    subprocess.run([bias_field_correction_path, "-d", "3", "-i", stack_path, "-x", mask_path, "-o", output_filename])
    print(f"N4BiasFieldCorrection done !")

    # SUBJECT_SESSION_rec-niftymic_desc-brainbg_T2w.nii.gz
    out_filename = f"{subject}_{session}_rec-niftymic_desc-brainbg_T2w.nii.gz"
    output_path = os.path.join(base_path, "niftymic", subject, session, "anat", out_filename)
    shutil.copy(output_filename, output_path)
    print(f"Copied debiased volume to {output_path}")

    # SUBJECT_SESSION_rec-niftymic_desc-brain_mask.nii
    out_filename = f"{subject}_{session}_rec-niftymic_desc-brain_mask.nii.gz"
    output_path = os.path.join(base_path, "niftymic", subject, session, "anat", out_filename)
    shutil.copy(output_path, output_path)
    print(f"Copied mask to {output_path}")














