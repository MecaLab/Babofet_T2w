import pandas as pd
import os
import sys
import numpy as np
import nibabel

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def compute_bins(df, bins=5):
    sess_cols = [c for c in df.columns if c.startswith("ses-")]

    long = df.melt(id_vars=["subject"], value_vars=sess_cols, var_name="session", value_name="day")

    long["day"] = pd.to_numeric(long["day"], errors="coerce")
    long = long.dropna(subset=["day"])

    long["bin_qcut"] = pd.qcut(long["day"], q=bins, duplicates='drop')

    counts_qcut = long.groupby("bin_qcut").size().reset_index(name="count")

    return counts_qcut

def dice_coefficient(seg1, seg2, label):
    intersection = np.logical_and(seg1 == label, seg2 == label)
    union = np.logical_or(seg1 == label, seg2 == label)
    if (np.sum(union) == 0) and (np.sum(intersection) == 0):
        return 1.0  # Si les deux segmentations sont vides pour ce label
    return 2. * intersection.sum() / (seg1[seg1 == label].size + seg2[seg2 == label].size)


def load_models():
    models = {
        "exp_1": ["2", "nnUNetTrainer_100epochs"],
        "exp_2": ["5", "nnUNetTrainerBiasField200epochs"],
        "exp_3": ["6", "nnUNetTrainerBiasField1000epochs"],
        "exp_4": ["8", "nnUNetTrainerBias_3000epochs"],
    }

    return models


if __name__ == "__main__":
    df = pd.read_csv("table_data/sessions_to_days.csv")

    models = load_models()

    nnunet_seg = os.path.join(cfg.CODE_PATH, "nnunet_mattia", "Aziza_ses02.nii.gz")

    nnunet_seg_path = os.path.join(cfg.CODE_PATH, "nnunet_mattia")

    for file in os.listdir(nnunet_seg_path):
        if file.endswith(".nii.gz"):
            print("Processing file :", file)
            file_splited = file.split(".")[0]
            name, sess = file_splited.split("_")
            bounti_seg = os.path.join(cfg.SEG_OUTPUT_PATH, name, sess, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

            file_seg = os.path.join(nnunet_seg_path, file)

            try:
                nnunet_img = nibabel.load(file_seg).get_fdata()
                bounti_img = nibabel.load(bounti_seg).get_fdata()
            except:
                print("Error loading files :", file_seg, bounti_seg)
                continue
            
            labels = [1, 2, 3, 4]

            dice_scores = {}
            for label in labels:
                dice_scores[label] = dice_coefficient(nnunet_img, bounti_img, label)

            print("DICE scores par label :", dice_scores)