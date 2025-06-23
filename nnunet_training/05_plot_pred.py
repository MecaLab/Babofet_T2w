import os
import sys
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    subject = sys.argv[1]
    session = sys.argv[2]

    base_path = os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, subject, session)

    true_label_path = os.path.join(base_path, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")
    pred_label_path = os.path.join(base_path, "pred_Borgne_ses05.nii.gz")


    print(os.path.exists(true_label_path), os.path.exists(pred_label_path))