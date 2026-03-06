import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    bias_field_correction_path = "/hpc/shared/apps/x86_64/softs/ANTS/2.3.4/bin/N4BiasFieldCorrection"  # path on niolon

    # command
    """
    N4BiasFieldCorrection -d 3 -i STACK_PATH -x MASK_PATH -o OUTPUT_PATH
    """

    subject = sys.argv[1]
    base_path = os.path.join(cfg.RECONS_FOLDER, subject)

    for session in os.listdir(base_path):
        print(f"Processing {subject} {session}...")
        session_path = os.path.join(base_path, session, "recons_rhesus/recon_template_space")

        stack_path = os.path.join(session_path, "srr_template.nii.gz")
        mask_path = os.path.join(session_path, "srr_template_mask.nii.gz")

        if not os.path.exists(stack_path):
            print(f"\tStack file {stack_path} does not exist, skipping...")
            continue

        output_filename = os.path.join(session_path, "srr_template_debiased.nii.gz")
        if os.path.exists(output_filename):
            print(f"\tOutput file {output_filename} already exists, skipping...")
            continue

        subprocess.run([bias_field_correction_path, "-d", "3", "-i", stack_path, "-x", mask_path, "-o", output_filename])
        print(f"N4BiasFieldCorrection done !")














