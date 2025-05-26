import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    bias_field_correction_path = "/hpc/shared/apps/x86_64/softs/ANTS/2.3.4/bin/N4BiasFieldCorrection"  # path on niolon

    # command
    """
    N4BiasFieldCorrection -d 3 -i STACK_PATH -x MASK_PATH -o OUTPUT_PATH
    """

    subject = "Fabienne"
    base_path = os.path.join(cfg.BASE_NIOLON_PATH, "bounti/svrtk_BOUNTI/output_BOUNTI_seg/haste", subject)

    for session in os.listdir(base_path):
        print(session)

    







