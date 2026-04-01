import os
import sys
import nibabel as nib
import numpy as np
import pandas as pd
from scipy.ndimage import distance_transform_edt
import matplotlib.pyplot as plt
import seaborn as sns
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


def calculer_hausdorff_distance(mask1, mask2, labels, spacing=(0.5, 0.5, 0.5)):
    hausdorff_distances = []
    voxel_size = np.mean(spacing)

    for label in labels:
        bin_mask1 = (mask1 == label).astype(int)
        bin_mask2 = (mask2 == label).astype(int)

        if np.any(bin_mask1) and np.any(bin_mask2):
            # 1. Calcul de la distance réelle en mm
            d1 = distance_transform_edt(bin_mask1 == 0, sampling=spacing)
            d2 = distance_transform_edt(bin_mask2 == 0, sampling=spacing)
            hd_mm = max(np.max(d1[bin_mask2 > 0]), np.max(d2[bin_mask1 > 0]))
            hd_voxel = hd_mm / voxel_size
            hausdorff_distances.append(hd_voxel)
        else:
            hausdorff_distances.append(0.0)
    return hausdorff_distances


def mean_std(scores_list):
    # scores_list est une liste de listes, chaque sous-liste contenant les scores pour un sujet
    moyennes = np.mean(scores_list, axis=0)
    stds = np.std(scores_list, axis=0)
    return moyennes, stds


def save_results(dataset_id, moyennes_dice, stds_dice, moyennes_iou, stds_iou, moyennes_hausdorff, stds_hausdorff, dice_scores_list, iou_scores_list, hausdorff_scores_list, labels_map):
    # Créer un DataFrame pour les résultats
    results = []
    for label in labels_map:
        results.append({
            "Model_ID": dataset_id,
            "Label": labels_map[label],
            "Dice_Mean": moyennes_dice[label-1],
            "Dice_Std": stds_dice[label-1],
            "IoU_Mean": moyennes_iou[label-1],
            "IoU_Std": stds_iou[label-1],
            "Hausdorff_Mean": moyennes_hausdorff[label-1],
            "Hausdorff_Std": stds_hausdorff[label-1],
            "Dice_Scores": ",".join(map(str, [score[label-1] for score in dice_scores_list])),
            "IoU_Scores": ",".join(map(str, [score[label-1] for score in iou_scores_list])),
            "Hausdorff_Scores": ",".join(map(str, [score[label-1] for score in hausdorff_scores_list])),
        })

    df = pd.DataFrame(results)

    # Chemin du fichier CSV
    csv_path = os.path.join(cfg.TABLE_DATA_PATH, "resultats_segmentation.csv")

    # Écrire dans le fichier CSV
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)


def plot_and_save_boxplots(csv_path, dataset_id, save_path="boxplots_metrics.png"):
    data = pd.read_csv(csv_path)
    # Convertir les listes de scores
    data['Dice_Scores'] = data['Dice_Scores'].apply(eval)
    data['IoU_Scores'] = data['IoU_Scores'].apply(eval)
    data['Hausdorff_Scores'] = data['Hausdorff_Scores'].apply(eval)

    # Définir l'ordre des labels
    label_order = ['CSF', 'WM', 'GM', 'Ventricle']

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Boxplot pour Dice
    sns.boxplot(x='Label', y='Dice_Scores', hue='Model_ID', data=data.explode('Dice_Scores'), ax=axes[0], order=label_order)
    axes[0].set_title('Dice')
    axes[0].set_ylim(0.8, 1.0)
    axes[0].set_xlabel('Label')
    axes[0].set_ylabel('Dice Score')

    # Boxplot pour IoU
    sns.boxplot(x='Label', y='IoU_Scores', hue='Model_ID', data=data.explode('IoU_Scores'), ax=axes[1], order=label_order)
    axes[1].set_title('IoU')
    axes[1].set_ylim(0.6, 1.0)
    axes[1].set_xlabel('Label')
    axes[1].set_ylabel('IoU Score')

    # Boxplot pour Hausdorff
    sns.boxplot(x='Label', y='Hausdorff_Scores', hue='Model_ID', data=data.explode('Hausdorff_Scores'), ax=axes[2], order=label_order)
    axes[2].set_title('Hausdorff')
    axes[2].set_xlabel('Label')
    axes[2].set_ylabel('Hausdorff Distance')

    # Sauvegarder le graphique
    plt.tight_layout()
    output_path = os.path.join(cfg.CODE_PATH, f"snapshots/res_seg/pred_dataset_{dataset_id}/{save_path}")
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()


def plot_metrics_by_model(dataset_id, csv_path="resultats_segmentation.csv"):
    # Charger les données
    df = pd.read_csv(csv_path)

    # Créer une figure avec trois sous-graphiques
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Couleurs pour chaque label
    label_colors = {'CSF': 'blue', 'WM': 'green', 'GM': 'purple', 'Ventricle': 'red'}

    # Pour chaque métrique
    for i, metric in enumerate(['Dice_Mean', 'IoU_Mean', 'Hausdorff_Mean']):
        ax = axes[i]
        ax.set_title(metric.replace('_Mean', ''))

        # Pour chaque label, tracer les points
        for label in df['Label'].unique():
            label_df = df[df['Label'] == label]
            models = sorted(label_df['Model_ID'].unique())
            metric_values = label_df[metric].values

            ax.scatter([str(m) for m in models], metric_values, color=label_colors[label], marker='o', label=label)

            for m, val in zip(models, metric_values):
                ax.text(str(m), val + 0.01 if metric != 'Hausdorff_Mean' else val + 0.5, f"{val:.3f}",
                        ha='center', va='bottom', fontsize=8, color=label_colors[label])

        ax.set_xlabel('Modèle')
        ax.set_ylabel('Score')
        ax.set_xticks([str(m) for m in sorted(df['Model_ID'].unique())])
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

    plt.tight_layout()
    output_path = os.path.join(cfg.CODE_PATH, f"snapshots/res_seg/pred_dataset_{dataset_id}/metrics_by_model.png")
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    if not os.path.exists(cfg.TABLE_DATA_PATH):
        os.makedirs(cfg.TABLE_DATA_PATH)
    if not os.path.exists("snapshots/res_seg"):
        os.makedirs("snapshots/res_seg")

    models = [int(x) for x in sys.argv[1].split(",")]
    results_seg_csv_path = os.path.join(cfg.TABLE_DATA_PATH, "resultats_segmentation.csv")

    voxel_spacing = (0.5, 0.5, 0.5)

    gt_dataset = os.path.join(cfg.BASE_PATH, "gt_dataset_2", "test_dataset")

    if not os.path.exists(results_seg_csv_path):
        for model in models:
            dataset_id = int(model)
            input_folder = os.path.join(cfg.CODE_PATH, f"snapshots/res_seg/pred_dataset_{dataset_id}")
            if not os.path.exists(input_folder):
                print(f"Error: input folder of predictions {input_folder} does not exist")
                print("Make sure to run the previous script")
                exit(1)

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

            for file in os.listdir(gt_dataset):
                if file.endswith(".nii.gz"):
                    file_splitted = file.split("_")
                    subject = file_splitted[0]
                    session = file_splitted[1]  # sesXX.nii.gz
                    print(f"Processing {file}")

                    gt_file_path = os.path.join(gt_dataset, file)
                    gt_img = nib.load(gt_file_path).get_fdata()

                    pred_path = os.path.join(input_folder, file)
                    pred_img = nib.load(pred_path).get_fdata()

                    dice_scores = calculer_dice_score(pred_img, gt_img, labels)
                    iou_scores = calculer_iou_score(pred_img, gt_img, labels)
                    hausdorff_scores = calculer_hausdorff_distance(pred_img, gt_img, labels, spacing=voxel_spacing)

                    dice_scores_list.append(dice_scores)
                    iou_scores_list.append(iou_scores)
                    hausdorff_scores_list.append(hausdorff_scores)

                    for label, dice, iou, hd in zip(labels, dice_scores, iou_scores, hausdorff_scores):
                        print(f"\t{labels_map[label]}: Dice={dice:.4f}, IoU={iou:.4f}, Hausdorff={hd:.4f}")

            mean_dice, stds_dice = mean_std(dice_scores_list)
            mean_iou, stds_iou = mean_std(iou_scores_list)
            mean_hausdorff, stds_hausdorff = mean_std(hausdorff_scores_list)

            # Affichage des résultats finaux
            print("\n--- Résultats finaux (moyenne ± std) ---")
            for label, dice, std_dice, iou, std_iou, hd, std_hd in zip(labels, mean_dice, stds_dice, mean_iou, stds_iou, mean_hausdorff, stds_hausdorff):
                print(
                    f"{labels_map[label]}: "
                    f"Dice={dice:.4f}±{std_dice:.4f}, "
                    f"IoU={iou:.4f}±{std_iou:.4f}, "
                    f"Hausdorff={hd:.4f}±{std_hd:.4f}",
                )

            save_results(dataset_id, mean_dice, stds_dice, mean_iou, stds_iou, mean_hausdorff,
                                      stds_hausdorff, dice_scores_list, iou_scores_list, hausdorff_scores_list, labels_map)

            plot_and_save_boxplots(csv_path=results_seg_csv_path, dataset_id=model)

            plot_metrics_by_model(csv_path=results_seg_csv_path, dataset_id=model)