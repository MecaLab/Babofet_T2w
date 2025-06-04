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

    subject = "Aziza"
    stack_base_path = os.path.join(cfg.BASE_NIOLON_PATH, "bounti/svrtk_BOUNTI/input_SRR_niftymic/haste", subject)
    mask_base_path = os.path.join(cfg.BASE_NIOLON_PATH, "bounti/svrtk_BOUNTI/output_BOUNTI_seg/haste", subject)

    for session in os.listdir(stack_base_path):

        stack_path = os.path.join(stack_base_path, session, "reo-SVR-output-brain_rhesus.nii.gz")
        mask_path = os.path.join(mask_base_path, session, "reo-SVR-output-brain_rhesus-mask-bet-1.nii.gz")

        if not os.path.exists(stack_path):
            print(f"\tStack file {stack_path} does not exist, skipping...")
            continue

        output_filename = f"{subject}_{session}_reo-SVR-output-brain_rhesus_withbc.nii.gz"

        subprocess.run(["N4BiasFieldCorrection", "-d", "3", "-i", stack_path, "-x", mask_path, "-o", output_filename])
        print(f"\t OK for {subject} {session}")














