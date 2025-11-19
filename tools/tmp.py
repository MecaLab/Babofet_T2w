import shutil

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


def generalized_dice(seg1, seg2, labels):
    numerator = 0
    denominator = 0
    for label in labels:
        intersection = np.logical_and(seg1 == label, seg2 == label).sum()
        size1 = (seg1 == label).sum()
        size2 = (seg2 == label).sum()
        w = 1.0 / ((size1 + size2) ** 2 + 1e-10)
        numerator += w * intersection
        denominator += w * (size1 + size2)
    return 2 * numerator / denominator


def load_models():
    models = {
        "exp_1": ["2", "nnUNetTrainer_100epochs"],
        "exp_2": ["5", "nnUNetTrainerBias_200epochs"],
        "exp_3": ["6", "nnUNetTrainerBias_1000epochs"],
        "exp_4": ["8", "nnUNetTrainerBias_3000epochs"],
    }

    return models


def format_bounti(input_path, output_path):
    for subject in os.listdir(input_path):
        subject_path = os.path.join(input_path, subject)
        if not os.path.isdir(subject_path):
            continue

        for session in os.listdir(subject_path):
            session_path = os.path.join(subject_path, session)
            if not os.path.isdir(session_path):
                continue

            bounti_seg = os.path.join(session_path, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")
            if not os.path.exists(bounti_seg):
                continue

            output_seg_path = os.path.join(output_path, f"{subject}_{session}.nii.gz")

            shutil.copy(bounti_seg, output_seg_path)

        print(f"End for {subject}")

def compare_models(model_1_path, model_2_path):
    pass


if __name__ == "__main__":
    df = pd.read_csv("table_data/sessions_to_days.csv")

    models = load_models()

    nnunet_seg_path = os.path.join(cfg.CODE_PATH, "nnunet_mattia")

    bounti_seg_formated_path = os.path.join(cfg.CODE_PATH, "nnunet_mattia", "BOUNTI_segmentations")

    format_bounti(cfg.SEG_OUTPUT_PATH, bounti_seg_formated_path)

    dice_scores = []

    for file in os.listdir(nnunet_seg_path):
        if file.endswith(".nii.gz"):
            file_splited = file.split(".")[0]
            name, sess = file_splited.split("_")
            bounti_seg = os.path.join(cfg.SEG_OUTPUT_PATH, name, sess, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

            file_seg = os.path.join(nnunet_seg_path, file)

            try:
                seg1 = nibabel.load(file_seg).get_fdata()
                seg2 = nibabel.load(bounti_seg).get_fdata()
            except:
                # print("Error loading files :", file_seg, bounti_seg)
                continue
            
            labels = [1, 2, 3, 4]

            gdice = generalized_dice(seg1, seg2, labels)
            dice_scores.append(gdice)
            print(f"DICE généralisé pour {file} : {gdice:.4f}")

    mean_dice = np.mean(dice_scores)
    print(f"DICE moyen sur le jeu de données : {mean_dice:.4f}")