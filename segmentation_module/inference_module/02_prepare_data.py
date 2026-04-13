import os
import shutil
import subprocess
import sys
from collections import defaultdict
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def generate_patients_json():
    pass


def mv_files(data, input_path, output_path):
    for subject, sessions in data.items():
        print(f"Processing {subject}")

        for session in sessions:
            print(f"\tProcessing {session}")

            # sub-SUBJECT_SESS_rec-niftymic_desc-brainbg_T2w.nii
            vol_3d_filename = f"sub-{subject}_{session}_rec-niftymic_desc-brainbg_T2w.nii.gz"
            input_3d_path = os.path.join(input_path, f"sub-{subject}", session, "anat", vol_3d_filename)

            output_3d_path = os.path.join(output_path, f"{subject}_{session}_0000.nii.gz")

            if os.path.exists(input_3d_path):
                shutil.copy(input_3d_path, output_3d_path)

if __name__ == "__main__":
    subj_sess = {
        "Borgne": ["ses-01", "ses-03", "ses-04"],
        "Filoutte": ["ses-05", "ses-06", "ses-07"]
    }

    input_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "nnunet", "inference_data")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    mv_files(subj_sess, input_path, output_path)