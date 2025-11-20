import shutil
import itertools
import seaborn as sns
import matplotlib.pyplot as plt
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
    # Crée un masque pour chaque label
    masks1 = np.stack([seg1 == label for label in labels], axis=0)
    masks2 = np.stack([seg2 == label for label in labels], axis=0)

    # Calcul des intersections et tailles
    intersection = np.logical_and(masks1, masks2).sum(axis=(1, 2, 3))
    size1 = masks1.sum(axis=(1, 2, 3))
    size2 = masks2.sum(axis=(1, 2, 3))

    # Poids et score
    w = 1.0 / ((size1 + size2) ** 2 + 1e-10)
    numerator = np.sum(w * intersection)
    denominator = np.sum(w * (size1 + size2))

    return 2 * numerator / denominator

def dice_coefficient(seg1, seg2, label):
    # Intersection et union pour le label donné
    intersection = np.logical_and(seg1 == label, seg2 == label)
    union = np.logical_or(seg1 == label, seg2 == label)
    # Éviter la division par zéro
    if (np.sum(union) == 0) and (np.sum(intersection) == 0):
        return 1.0  # Si les deux segmentations sont vides pour ce label
    return 2. * intersection.sum() / (seg1[seg1 == label].size + seg2[seg2 == label].size)


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

            if not os.path.exists(output_seg_path):
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

            try:
                seg1 = nibabel.load(seg_1).get_fdata()
            except FileNotFoundError:
                if verbose:
                    print(f"File not found: {seg_1}. Skipping.")
                continue
            except nibabel.filebasedimages.ImageFileError:
                if verbose:
                    print(f"Error loading file: {seg_1}. Skipping.")
                continue
            try:
                seg2 = nibabel.load(seg_2).get_fdata()
            except FileNotFoundError:
                if verbose:
                    print(f"File not found: {seg_2}. Skipping.")
                continue
            except nibabel.filebasedimages.ImageFileError:
                if verbose:
                    print(f"Error loading file: {seg_2}. Skipping.")
                continue

            gdice = generalized_dice(seg1, seg2, labels)

            """dice_scores = []
            for label in labels:
                dice = dice_coefficient(seg1, seg2, label)
                dice_scores.append(dice)

            # Score global = moyenne des Dice par label
            gdice = np.mean(dice_scores)"""

            subject_row = df[df["subject"] == name]
            sess_value = subject_row[sess_formated].values[0]

            bin_interval = pd.cut([sess_value], bins=long["bin_qcut"].cat.categories, right=True,
                                  labels=long["bin_qcut"].cat.categories)[0]
            try:
                bin_dict[bin_interval].append(gdice)
            except KeyError:
                if verbose:
                    print(f"Value {sess_value} for subject {name} and session {sess_formated} does not fit in any bin.")
                continue
            
            if verbose:
                print(f"File: {file} - DICE généralisé pour {exp_1} vs {exp_2} : {gdice:.4f}. Added to bin {bin_interval}")

    return bin_dict


if __name__ == "__main__":
    root_dir = os.path.join(cfg.CODE_PATH, "inference_all")
    csv_path = os.path.join(root_dir, "dice_scores_by_bins.csv")
    df = pd.read_csv(csv_path)
    print(df)

    df["Total"] = df.mean(axis=1)

    # Afficher le DataFrame mis à jour
    print(df)


    exit()
    df = pd.read_csv("table_data/sessions_to_days.csv")

    long, counts_qcut = compute_bins(df, bins=5)

    root_dir = os.path.join(cfg.CODE_PATH, "inference_all")

    bounti_seg_formated_path = os.path.join(root_dir, "BOUNTI_segmentations")

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    format_bounti(cfg.SEG_OUTPUT_PATH, bounti_seg_formated_path)

    exp_to_compare = ["BOUNTI", "2", "5", "6", "7", "8"]
    dice_scores = []
    labels = [1, 2, 3, 4]

    all_results = {}

    for exp_1, exp_2 in itertools.combinations(exp_to_compare, 2):
        comparison_name = f"{exp_1} vs {exp_2}"
        exp_1_path = os.path.join(root_dir, f"{exp_1}_segmentations")
        exp_2_path = os.path.join(root_dir, f"{exp_2}_segmentations")

        if not os.path.exists(exp_1_path) or not os.path.exists(exp_2_path):
            print(f"One of the experiment paths does not exist: {exp_1_path} or {exp_2_path}. Skipping comparison.")
            print("Make sure to run the prediction scripts (05_predict_all) for all experiments before comparing.")
            continue


        print(f"\nComparing {comparison_name}:")
        bin_dict = compare_models(exp_1_path, exp_2_path, counts_qcut, long, verbose=False)

        moyennes = {
            bin_interval: sum(scores) / len(scores) if scores else 0
            for bin_interval, scores in bin_dict.items()
        }

        for bin_interval, mean_dice in moyennes.items():
            print(f"\tBins: {bin_interval}: {mean_dice:.3f}")

        all_results[comparison_name] = moyennes

    # Créer le DataFrame
    results_df = pd.DataFrame(all_results).T

    # Afficher les résultats
    print("\nMoyennes des scores DICE par bin (toutes comparaisons) :")
    print(results_df)

    # Sauvegarder les résultats
    csv_path = os.path.join(root_dir, "dice_scores_by_bins.csv")
    results_df.to_csv(csv_path, index=True)
    print(f"\nRésultats sauvegardés dans : {csv_path}")

    # Générer la heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(results_df, annot=True, cmap="YlGnBu", fmt=".3f", cbar_kws={'label': 'Dice Score'})
    plt.title("Moyennes des scores DICE par bin")
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(root_dir, "heatmap_dice_by_bin.png"), dpi=200, bbox_inches='tight')
    plt.clf()