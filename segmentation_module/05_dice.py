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
    dataset_id = int(sys.argv[1])
    name = sys.argv[2]

    if dataset_id < 10:
        dataset_name = f"Dataset00{dataset_id}_{name}"
    elif dataset_id < 100:
        dataset_name = f"Dataset0{dataset_id}_{name}"
    else:
        dataset_name = f"Dataset{dataset_id}_{name}"

    input_folder = os.path.join(cfg.CODE_PATH, f"snapshots/nnunet_res/pred_dataset_{dataset_id}")
    dice_scores_list = []

    labels = [1, 2, 3, 4]
    labels_map = {
        1: "CSF",
        2: "WM",
        3: "GM",
        4: "Ventricle"
    }

    for file in os.listdir(input_folder):
        if file.endswith(".nii.gz"):
            file_splitted = file.split("_")
            subject = file_splitted[0]
            session = file_splitted[1]  # sesXX.nii.gz
            print(f"Processing {file}")

            try:
                gt_path = os.path.join(cfg.BASE_PATH, "gt_dataset/test_dataset", f"{subject}_{session}")
                gt_img = nib.load(gt_path).get_fdata()
            except FileNotFoundError:
                gt_path = os.path.join(cfg.BASE_PATH, "gt_dataset/test_dataset", f"{subject}_{session}.nii.gz")
                gt_img = nib.load(gt_path).get_fdata()

            pred_path = os.path.join(input_folder, file)
            pred_img = nib.load(pred_path).get_fdata()

            dice_scores = calculer_dice_score(pred_img, gt_img, labels)
            dice_scores_list.append(dice_scores)

            for elem in zip(labels, dice_scores):
                label, score = elem
                print(f"\t{labels_map[label]}: {score:.4f}")

    moyennes_dice_scores = moyenne_dice_scores(dice_scores_list)
    for label, score in zip(labels, moyennes_dice_scores):
        print(f"Score moyen pour {labels_map[label]}: {score:.4f}")
