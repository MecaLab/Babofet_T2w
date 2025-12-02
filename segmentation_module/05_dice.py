import os
import sys
import nibabel as nib
import numpy as np
from scipy.ndimage import distance_transform_edt
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


def calculer_iou_score(mask1, mask2, labels):
    iou_scores = []
    for label in labels:
        bin_mask1 = (mask1 == label).astype(int)
        bin_mask2 = (mask2 == label).astype(int)
        intersection = np.logical_and(bin_mask1, bin_mask2).sum()
        union = np.logical_or(bin_mask1, bin_mask2).sum()
        if union == 0:
            iou_scores.append(1.0)
        else:
            iou = intersection / union
            iou_scores.append(iou)
    return iou_scores


def calculer_hausdorff_distance(mask1, mask2, labels):
    hausdorff_distances = []
    for label in labels:
        bin_mask1 = (mask1 == label).astype(int)
        bin_mask2 = (mask2 == label).astype(int)
        if np.any(bin_mask1) and np.any(bin_mask2):
            # Calcul de la distance de Hausdorff
            d1 = distance_transform_edt(bin_mask1 == 0, sampling=None)
            d2 = distance_transform_edt(bin_mask2 == 0, sampling=None)
            hd = max(np.max(d1[bin_mask2 > 0]), np.max(d2[bin_mask1 > 0]))
            hausdorff_distances.append(hd)
        else:
            hausdorff_distances.append(0.0)
    return hausdorff_distances


def moyenne_et_std(scores_list):
    # scores_list est une liste de listes, chaque sous-liste contenant les scores pour un sujet
    moyennes = np.mean(scores_list, axis=0)
    stds = np.std(scores_list, axis=0)
    return moyennes, stds


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
    iou_scores_list = []
    hausdorff_scores_list = []

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
            iou_scores = calculer_iou_score(pred_img, gt_img, labels)
            hausdorff_scores = calculer_hausdorff_distance(pred_img, gt_img, labels)

            dice_scores_list.append(dice_scores)
            iou_scores_list.append(iou_scores)
            hausdorff_scores_list.append(hausdorff_scores)

            for label, dice, iou, hd in zip(labels, dice_scores, iou_scores, hausdorff_scores):
                print(f"\t{labels_map[label]}: Dice={dice:.4f}, IoU={iou:.4f}, Hausdorff={hd:.4f}")

    moyennes_dice, stds_dice = moyenne_et_std(dice_scores_list)
    moyennes_iou, stds_iou = moyenne_et_std(iou_scores_list)
    moyennes_hausdorff, stds_hausdorff = moyenne_et_std(hausdorff_scores_list)

    # Affichage des résultats finaux
    print("\n--- Résultats finaux (moyenne ± std) ---")
    for label, dice, std_dice, iou, std_iou, hd, std_hd in zip(labels, moyennes_dice, stds_dice, moyennes_iou, stds_iou, moyennes_hausdorff, stds_hausdorff):
        print(
            f"{labels_map[label]}: "
            f"Dice={dice:.4f}±{std_dice:.4f}, "
            f"IoU={iou:.4f}±{std_iou:.4f}, "
            f"Hausdorff={hd:.4f}±{std_hd:.4f}"
        )


    """
    10:
        CSF: 0.9747
        WM: 0.9840
        GM: 0.9578
        Ventricle: 0.8519
    11:
        CSF: 0.9755
        WM: 0.9840
        GM: 0.9582
        Ventricle: 0.8562
    12:
        CSF: 0.9746
        WM: 0.9839
        GM: 0.9580
        Ventricle: 0.8532
    20:
        CSF: 0.9737
        WM: 0.9837
        GM: 0.9567
        Ventricle: 0.8517
    """