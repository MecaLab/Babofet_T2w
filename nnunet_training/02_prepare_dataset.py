import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import shutil
import nibabel as nib
import numpy as np


if __name__ == "__main__":
    subject_sessions = {
        "Filoutte": ["ses03", "ses04", "ses05"],
        "Fabienne": ["ses03", "ses04", "ses05"],
        "Formule": ["ses02", "ses03"],
        # Borgne soon
    }

    for subject, sessions in subject_sessions.items():

        input_path_3d_stacks = os.path.join(cfg.BOUNTI_PATH, "svrtk_BOUNTI/input_SRR_niftymic/haste", subject)
        input_path_3d_segs = os.path.join(cfg.BOUNTI_PATH, "svrtk_BOUNTI/output_BOUNTI_seg/haste", subject)

        output_path = os.path.join(cfg.NNUNET_RAW_PATH, "Dataset001_Babofet")

        images_tr_path = os.path.join(output_path, "imagesTr")
        images_ts_path = os.path.join(output_path, "imagesTs")
        labels_tr_path = os.path.join(output_path, "labelsTr")

        if not os.path.exists(images_tr_path):
            os.makedirs(images_tr_path)
        if not os.path.exists(images_ts_path):
            os.makedirs(images_ts_path)
        if not os.path.exists(labels_tr_path):
            os.makedirs(labels_tr_path)

        for session in sessions:
            input_path_3d_stack = os.path.join(input_path_3d_stacks, session, "reo-SVR-output-brain_rhesus.nii.gz")
            input_path_3d_seg = os.path.join(input_path_3d_segs, session, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

            output_path_3d_stack = os.path.join(images_tr_path, f"{subject}_{session}_0000.nii.gz")
            output_path_3d_seg = os.path.join(labels_tr_path, f"{subject}_{session}.nii.gz")

            shutil.copy2(input_path_3d_stack, output_path_3d_stack)
            shutil.copy2(input_path_3d_seg, output_path_3d_seg)