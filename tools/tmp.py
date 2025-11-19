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

    counts_qcut = long.groupby("bin_qcut", observed=False).size().reset_index(name="count")

    return long, counts_qcut


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


def format_bounti(input_path, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

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

def compare_models(model_1_path, model_2_path, counts_qcut, long, verbose=False):
    bin_dict = {bin_interval: [] for bin_interval in counts_qcut["bin_qcut"]}
    for file in os.listdir(model_1_path):
        if file.endswith(".nii.gz"):
            file_splited = file.split(".")[0]
            name, sess = file_splited.split("_")
            sess_formated = f"ses-{sess[3:]}"  # sesXX -> ses-XX
            seg_1 = os.path.join(exp_1_path, file)
            seg_2 = os.path.join(model_2_path, file)

            seg1 = nibabel.load(seg_1).get_fdata()
            seg2 = nibabel.load(seg_2).get_fdata()

            gdice = generalized_dice(seg1, seg2, labels)
            subject_row = df[df["subject"] == name]
            sess_value = subject_row[sess_formated].values[0]

            bin_interval = pd.cut([sess_value], bins=long["bin_qcut"].cat.categories, right=True,
                                  labels=long["bin_qcut"].cat.categories)[0]
            bin_dict[bin_interval].append(gdice)
            
            if verbose:
                print(f"File: {file} - DICE généralisé pour {exp_1} vs {exp_2} : {gdice:.4f}. Added to bin {bin_interval}")

    return bin_dict


if __name__ == "__main__":
    df = pd.read_csv("table_data/sessions_to_days.csv")

    long, counts_qcut = compute_bins(df, bins=5)

    root_dir = os.path.join(cfg.CODE_PATH, "inference_all")

    bounti_seg_formated_path = os.path.join(root_dir, "BOUNTI_segmentations")

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
        format_bounti(cfg.SEG_OUTPUT_PATH, bounti_seg_formated_path)

    exp_to_compare = ["BOUNTI", "8"]  # ["BOUNTI", "2", "5", "6", "8"]
    dice_scores = []
    labels = [1, 2, 3, 4]

    for i in range(len(exp_to_compare) - 1):
        exp_1 = exp_to_compare[i + 1]
        exp_2 = exp_to_compare[i]

        exp_1_path = os.path.join(root_dir, f"{exp_1}_segmentations")
        exp_2_path = os.path.join(root_dir, f"{exp_2}_segmentations")

        bin_dict = compare_models(exp_1_path, exp_2_path, counts_qcut, long, verbose=True)

        moyennes = {
            bin_interval: sum(scores) / len(scores) if scores else 0
            for bin_interval, scores in bin_dict.items()
        }

        for bin_interval, mean_score in moyennes.items():
            print(f"Bins: {bin_interval}: {mean_score:.3f}")