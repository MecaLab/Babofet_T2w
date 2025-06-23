import os
import sys
import nibabel as nib
import numpy as np

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def calculer_dice_score(mask1, mask2, labels):
    dice_scores = []
    for label in labels:
        bin_mask1 = (mask1 == label).astype(int)
        bin_mask2 = (mask2 == label).astype(int)

        intersection = np.logical_and(bin_mask1, bin_mask2).sum()
        sum_masks = bin_mask1.sum() + bin_mask2.sum()

        if sum_masks == 0:
            dice_scores.append(1.0)
        else:
            dice = (2. * intersection) / sum_masks
            dice_scores.append(dice)

    return dice_scores


def moyenne_dice_scores(dice_scores_list):
    # dice_scores_list est une liste de listes, chaque sous-liste contenant les scores pour un sujet
    moyennes = np.mean(dice_scores_list, axis=0)
    return moyennes


if __name__ == "__main__":
    session = "ses03"

    input_folder = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/"
    dice_scores_list = []

    for file in os.listdir(input_folder):
        if file.endswith(".nii.gz") and session in file:
            subject = file.split("_")[0]
            print(f"Processing {subject} {session}")

            gt_path = os.path.join(cfg.SEG_OUTPUT_PATH, subject, session, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")
            gt_img = nib.load(gt_path).get_fdata()

            pred_path = os.path.join(input_folder, file)
            pred_img = nib.load(pred_path).get_fdata()

            labels = [1, 2, 3, 4]
            labels_map = {
                1: "CSF",
                2: "WM",
                3: "GM",
                4: "Ventricle"
            }

            labels_avg_list = {
                1: [],
                2: [],
                3: [],
                4: []
            }

            dice_scores = calculer_dice_score(pred_img, gt_img, labels)
            dice_scores_list.append(dice_scores)

            for elem in zip(labels, dice_scores):
                label, score = elem
                print(f"\t{labels_map[label]}: {score:.4f}")

    moyennes_dice_scores = moyenne_dice_scores(dice_scores_list)
    print("DICE score moyens pour chaque label:", moyennes_dice_scores)
