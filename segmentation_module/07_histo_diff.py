import os
import sys
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

# TODO: refont code

if __name__ == "__main__":

    dataset_id_1 = sys.argv[1]
    dataset_id_2 = sys.argv[2]
    model_type = sys.argv[3]

    comparaison_name = f"dataset_{dataset_id_1}_vs_{dataset_id_2}"

    path_1 = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/pred_dataset_{dataset_id_1}")
    path_2 = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/pred_dataset_{dataset_id_2}")

    output_path = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/histo")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    label_names = {1: "CSF", 2: "WM", 3: "GM", 4: "Ventricule"}

    for file_1, file_2 in zip(os.listdir(path_1), os.listdir(path_2)):
        if file_1.endswith(".nii.gz") and file_2.endswith(".nii.gz"):

            subject_name = file_1.split(".")[0]

            mask1 = nib.load(os.path.join(path_1, file_1)).get_fdata()
            mask2 = nib.load(os.path.join(path_2, file_2)).get_fdata()

            mask1_fg = mask1[mask1 > 0]
            mask2_fg = mask2[mask1 > 0]

            diff = mask1_fg - mask2_fg

            plt.figure(figsize=(12, 6))
            plt.hist(diff, bins=np.arange(diff.min(), diff.max() + 2) - 0.5, color='lightcoral', edgecolor='black')
            plt.title(f"Histogramme des différences pour {subject_name}")
            plt.xlabel("Différences de labels (mask1 - mask2)")
            plt.ylabel("Nombre de voxels")
            plt.grid(True)
            plt.xticks(np.arange(diff.min(), diff.max() + 1))
            output_fig = os.path.join(cfg.BASE_PATH, os.path.join(output_path, f"{comparaison_name}_histo_diff_{subject_name}.png"))
            plt.tight_layout()
            plt.savefig(output_fig)

            # 2. Matrice de confusion entre les deux masques (hors background)
            cm = confusion_matrix(mask1_fg, mask2_fg, labels=[1, 2, 3, 4])

            plt.figure(figsize=(12, 10))
            sns.heatmap(cm, annot=True, fmt='d', cmap="Blues", xticklabels=label_names.values(), yticklabels=label_names.values())
            plt.xlabel(f"Prédiction modèle {dataset_id_2}")
            plt.ylabel(f"Prédiction modèle {dataset_id_1}")
            plt.title(f"Matrice de confusion entre masques pour {subject_name}")
            output_fig = os.path.join(output_path, f"{comparaison_name}_heatmap_diff_{subject_name}.png")
            plt.tight_layout()
            plt.savefig(output_fig)
            plt.close()